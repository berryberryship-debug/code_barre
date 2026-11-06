import numpy as np
import hashlib
from scipy.ndimage import gaussian_filter, rotate
import reedsolo

# ==========================================
# 1. SIMULATION PHYSIQUE DE LA PUF
# ==========================================
def generer_masque_phase(N=128):
    return np.exp(1j * np.random.uniform(0, 2*np.pi, (N, N)))

def simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.01):
    if angle != 0.0:
        masque_rot = rotate(np.real(masque), angle, reshape=False) + 1j * rotate(np.imag(masque), angle, reshape=False)
    else:
        masque_rot = masque
    champ = np.fft.fftshift(np.fft.fft2(masque_rot))
    intensite = np.abs(champ)**2
    intensite = intensite / np.max(intensite)
    intensite_bruitee = intensite + np.random.normal(0, bruit_camera, intensite.shape)
    return np.clip(intensite_bruitee, 0, 1)

def extraire_bits(intensite, block_size=8):
    intensite_floue = gaussian_filter(intensite, sigma=2.0)
    N = intensite.shape[0]
    n_blocks = N // block_size
    blocs = intensite_floue.reshape(n_blocks, block_size, n_blocks, block_size)
    moyennes = blocs.mean(axis=(1, 3))
    diff = moyennes[:, :-1] - moyennes[:, 1:]
    
    # Zone de garde dynamique
    y, x = np.ogrid[:diff.shape[0], :diff.shape[1]]
    centre_y, centre_x = (diff.shape[0] - 1) / 2, (diff.shape[1] - 1) / 2
    masque_cercle = ((x - centre_x)**2 + (y - centre_y)**2) <= (min(centre_y, centre_x) * 0.85)**2
    seuil = np.median(np.abs(diff[masque_cercle]))
    
    masque_valide = masque_cercle & (np.abs(diff) > seuil)
    bits = (diff > 0).astype(np.uint8)
    return bits.flatten(), masque_valide.flatten()

# ==========================================
# 2. CRYPTOGRAPHIE (VRAI FUZZY EXTRACTOR)
# ==========================================
def main():
    print("=== PIPELINE CRYPTOGRAPHIQUE (VRAIE METHODE) ===")
    np.random.seed(42)
    masque = generer_masque_phase(128)
    
    # On utilise une taille de bloc de 4 pour avoir BEAUCOUP de bits (plus de sécurité)
    block_size = 4 
    
    # --- 1. Enrôlement (Fabrication) ---
    ref = simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.0)
    bits_ref_full, masque_valide = extraire_bits(ref, block_size)
    
    # On extrait les bits stables, puis on garde les 96 premiers (12 octets)
    bits_stables = bits_ref_full[masque_valide]
    bits_puf_bytes = np.packbits(bits_stables[:96]).tobytes()
    
    # Clé secrète qu'on veut protéger (6 octets)
    cle_secrete = np.random.bytes(6)
    
    # On la protège avec Reed-Solomon (6 données + 6 correction = 12 octets)
    rs = reedsolo.RSCodec(6)
    cle_encodee = rs.encode(cle_secrete)
    
    # HELPER DATA = PUF XOR CLÉ ENCODÉE
    helper_data = bytes([a ^ b for a, b in zip(bits_puf_bytes, cle_encodee)])
    
    # La clé finale qu'on garde dans la base de données
    hash_ref = hashlib.sha256(cle_secrete).hexdigest()
    print(f"Clé secrète hashée : {hash_ref[:16]}... (256 bits)")

    # --- 2. Authentification (Lecture sous bruit) ---
    print("\n--- Test de lecture sous bruit ---")
    
    # Lecture avec un bruit de caméra modéré (0.05)
    bruitee = simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.05)
    bits_bruites_full, _ = extraire_bits(bruitee, block_size)
    
    # On applique le même masque qu'à l'enrôlement
    bits_stables_bruites = bits_bruites_full[masque_valide]
    bits_puf_bruites_bytes = np.packbits(bits_stables_bruites[:96]).tobytes()
    
    # RECONSTRUCTION : (PUF bruitée) XOR (Helper Data)
    # Cela recrée la clé encodée, mais avec les erreurs du bruit
    cle_encodee_bruitee = bytes([a ^ b for a, b in zip(bits_puf_bruites_bytes, helper_data)])
    
    try:
        # Reed-Solomon corrige les erreurs et retrouve la clé secrète
        cle_retrouvee, _, _ = rs.decode(cle_encodee_bruitee)
        cle_retrouvee = bytes(cle_retrouvee)
        
        # On hache la clé retrouvée
        hash_test = hashlib.sha256(cle_retrouvee).hexdigest()
        
        print(f"Clé testée hashée  : {hash_test[:16]}...")
        
        if hash_ref == hash_test:
            print("✅ SUCCÈS TOTAL : La clé cryptographique est 100% identique malgré le bruit !")
        else:
            print("❌ ÉCHEC : Les clés sont différentes.")
            
    except reedsolo.ReedSolomonError:
        print("❌ ÉCHEC : Reed-Solomon n'a pas pu corriger (trop d'erreurs).")

if __name__ == "__main__":
    main()
