import numpy as np
from scipy.ndimage import gaussian_filter
import reedsolo

def generer_masque_phase(N=160):
    phase = np.random.uniform(0, 2*np.pi, (N, N))
    return np.exp(1j * phase)

def simuler_lecture_laser(masque, bruit_camera=0.01):
    champ = np.fft.fftshift(np.fft.fft2(masque))
    intensite = np.abs(champ)**2
    intensite = intensite / np.max(intensite)
    intensite_bruitee = intensite + np.random.normal(0, bruit_camera, intensite.shape)
    return np.clip(intensite_bruitee, 0, 1)

def extraire_cle_robuste(intensite, block_size=8):
    intensite_floue = gaussian_filter(intensite, sigma=2.0)
    N = intensite.shape[0]
    n_blocks = N // block_size
    blocs = intensite_floue.reshape(n_blocks, block_size, n_blocks, block_size)
    moyennes = blocs.mean(axis=(1, 3))
    bits = (moyennes[:, :-1] > moyennes[:, 1:]).astype(np.uint8)
    return bits.flatten()

def main():
    print("=== V33 CORRIGE : LE VRAI FUZZY EXTRACTOR ===")
    
    # On augmente un peu la taille pour avoir assez d'octets pour Reed-Solomon
    N = 160
    np.random.seed(42)
    masque_A = generer_masque_phase(N)
    
    # --- 1. Enrôlement ---
    print("\n--- 1. Enrôlement ---")
    # 1. On génère une clé secrète de 16 octets (128 bits)
    cle_secrete = bytes([np.random.randint(0, 256) for _ in range(16)])
    
    # 2. On encode la clé avec Reed-Solomon (16 octets + 20 octets de correction = 36 octets)
    rs = reedsolo.RSCodec(20)
    mot_de_code = rs.encode(cle_secrete)
    
    # 3. Lecture de référence de la PUF
    intensite_ref = simuler_lecture_laser(masque_A, bruit_camera=0.0)
    bits_puf_ref = extraire_cle_robuste(intensite_ref)
    
    # 4. On prend les 36 premiers octets de la PUF (288 bits)
    puf_ref_bytes = np.packbits(bits_puf_ref)[:36].tobytes()
    
    # 5. Helper Data = PUF_Ref XOR Mot_de_Code
    helper_data = bytes([a ^ b for a, b in zip(puf_ref_bytes, mot_de_code)])
    print(f"Clé secrète : {len(cle_secrete)} octets")
    print(f"Helper Data générée : {len(helper_data)} octets")
    
    # --- 2. Authentification ---
    print("\n--- 2. Authentification sous bruit ---")
    bruits = [0.01, 0.05, 0.10]
    
    for b in bruits:
        intensite_bruitee = simuler_lecture_laser(masque_A, bruit_camera=b)
        bits_puf_bruite = extraire_cle_robuste(intensite_bruitee)
        puf_noisy_bytes = np.packbits(bits_puf_bruite)[:36].tobytes()
        
        # Calcul de l'erreur brute sur la PUF (pour l'affichage)
        err_brute = np.mean(np.unpackbits(np.frombuffer(puf_ref_bytes, dtype=np.uint8)) != 
                            np.unpackbits(np.frombuffer(puf_noisy_bytes, dtype=np.uint8))) * 100
        
        # LA VRAIE LOGIQUE : On XOR la Helper Data avec la nouvelle PUF bruitée
        # Cela recrée un mot de code qui contient les erreurs du bruit
        mot_de_code_bruite = bytes([a ^ b for a, b in zip(helper_data, puf_noisy_bytes)])
        
        try:
            # Reed-Solomon répare le mot de code bruité pour retrouver la clé parfaite
            cle_retrouvee, _, _ = rs.decode(mot_de_code_bruite)
            cle_retrouvee = bytes(cle_retrouvee)
            
            if cle_retrouvee == cle_secrete:
                print(f"Bruit = {b:.2f} | Erreur PUF = {err_brute:5.2f}% | ✅ CLÉ PARFAITE RETROUVÉE !")
            else:
                print(f"Bruit = {b:.2f} | Erreur PUF = {err_brute:5.2f}% | ❌ Clé fausse (mais RS a décodé)")
                
        except reedsolo.ReedSolomonError:
            print(f"Bruit = {b:.2f} | Erreur PUF = {err_brute:5.2f}% | ❌ ECHEC : Reed-Solomon impuissant (trop de bruit).")

if __name__ == "__main__":
    main()
