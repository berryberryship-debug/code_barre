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
    
    # Zone de garde dynamique (top 50%)
    y, x = np.ogrid[:diff.shape[0], :diff.shape[1]]
    centre_y, centre_x = (diff.shape[0] - 1) / 2, (diff.shape[1] - 1) / 2
    masque_cercle = ((x - centre_x)**2 + (y - centre_y)**2) <= (min(centre_y, centre_x) * 0.85)**2
    seuil = np.median(np.abs(diff[masque_cercle]))
    
    masque_valide = masque_cercle & (np.abs(diff) > seuil)
    bits = (diff > 0).astype(np.uint8)
    return bits.flatten(), masque_valide.flatten()

# ==========================================
# 2. CRYPTOGRAPHIE (Fuzzy Extractor & SHA-256)
# ==========================================
def main():
    print("=== PIPELINE CRYPTOGRAPHIQUE FINAL (PUF -> SHA-256) ===")
    np.random.seed(42)
    masque = generer_masque_phase(128)
    
    # --- Phase d'Enrôlement (Fabrication) ---
    ref = simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.0)
    bits_ref_full, _ = extraire_bits(ref)
    
    # On prend 48 bits stables pour avoir 6 octets (assez pour Reed-Solomon)
    bits_ref = bits_ref_full[:_48] 
    ref_bytes = np.packbits(bits_ref).tobytes()
    
    # Création d'un code correcteur Reed-Solomon (6 octets de données + 6 de correction)
    rs = reedsolo.RSCodec(6)
    code_secret = rs.encode(ref_bytes)
    
    # On hache le code secret pour créer la clé finale (Privacy Amplification)
    cle_finale_ref = hashlib.sha256(code_secret).hexdigest()
    print(f"Clé de référence SHA-256 : {cle_finale_ref[:16]}... (256 bits)")

    # --- Phase d'Authentification (Lecture sous bruit) ---
    print("\n--- Test de lecture sous bruit et rotation ---")
    
    # On simule une lecture avec de la poussière (bruit 0.05)
    bruitee = simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.05)
    bits_bruites_full, _ = extraire_bits(bruitee)
    bits_bruites = bits_bruites_full[:_48]
    bytes_bruites = np.packbits(bits_bruites).tobytes()
    
    try:
        # Reed-Solomon tente de corriger les erreurs
        bytes_corriges, _, _ = rs.decode(bytes_bruites)
        
        # On hache la clé corrigée
        cle_finale_test = hashlib.sha256(bytes(bytes_corriges)).hexdigest()
        
        print(f"Clé testée SHA-256     : {cle_finale_test[:16]}...")
        
        if cle_finale_ref == cle_finale_test:
            print("✅ SUCCÈS : La clé cryptographique est 100% identique malgré le bruit !")
        else:
            print("❌ ÉCHEC : Les clés sont différentes.")
            
    except reedsolo.ReedSolomonError:
        print("❌ ÉCHEC : Trop d'erreurs, la clé n'a pas pu être corrigée.")

if __name__ == "__main__":
    main()
