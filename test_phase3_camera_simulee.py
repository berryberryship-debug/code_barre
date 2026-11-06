import numpy as np
import matplotlib.pyplot as plt
import reedsolo
from scipy.ndimage import gaussian_filter1d

# ==========================================
# CONFIGURATION
# ==========================================
RS_N = 12
RS_K = 6
RS = reedsolo.RSCodec(6)

N_BITS = RS_N * 8 
FREQ_CANAUX = np.linspace(10.0, 1000.0, N_BITS)
FREQ_ACQUISITION = np.linspace(10.0, 1000.0, 5000) # Grille idéale
ESPACEMENT = (1000.0 - 10.0) / (N_BITS - 1)
Q_FACTOR = 200

# ==========================================
# 1. GÉNÉRATION DU SPECTRE IDÉAL
# ==========================================
def lorentzienne(w, w0, Q, A=1.0):
    largeur = w0 / Q
    return A / (1 + 4 * ((w - w0) / largeur)**2)

def generer_spectre_ideal(bits, derive=0.0):
    spectre = np.zeros(len(FREQ_ACQUISITION))
    for i, bit in enumerate(bits):
        if bit == 1:
            w0 = FREQ_CANAUX[i] + derive 
            spectre += lorentzienne(FREQ_ACQUISITION, w0, Q=Q_FACTOR)
    return spectre

# ==========================================
# 2. SIMULATEUR MATÉRIEL (CORRIGÉ)
# ==========================================
def simuler_materiel(spectre_ideal, resolution_pixels=1024, bruit_electronique=0.05, saturation=1.2):
    # A. Le capteur (1024 pixels, c'est le minimum pour voir 96 canaux clairement)
    freq_camera = np.linspace(10.0, 1000.0, resolution_pixels)
    spectre_camera = np.interp(freq_camera, FREQ_ACQUISITION, spectre_ideal)
    
    # B. Flou optique (PSF)
    spectre_camera = gaussian_filter1d(spectre_camera, sigma=1.5)
    
    # C. Bruit du capteur
    bruit = np.random.normal(0, bruit_electronique, len(freq_camera))
    spectre_camera += bruit
    
    # D. Saturation
    spectre_camera = np.clip(spectre_camera, 0, saturation)
    
    return freq_camera, spectre_camera

# ==========================================
# 3. LECTEUR (MATCHED FILTER)
# ==========================================
def lire_spectre_camera(freq_camera, spectre_camera):
    bits_lus = np.zeros(N_BITS, dtype=np.uint8)
    demi_fenetre = ESPACEMENT / 2 
    
    for i in range(N_BITS):
        f_c = FREQ_CANAUX[i]
        idx_debut = np.searchsorted(freq_camera, f_c - demi_fenetre)
        idx_fin = np.searchsorted(freq_camera, f_c + demi_fenetre)
        
        if idx_fin > idx_debut:
            template = lorentzienne(freq_camera[idx_debut:idx_fin], f_c, Q=Q_FACTOR)
            signal_local = spectre_camera[idx_debut:idx_fin]
            
            energie = np.sum(signal_local * template) / np.sum(template * template)
            
            if energie > 0.3: 
                bits_lus[i] = 1
                
    return bits_lus

# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================
def main():
    print("=== PHASE 2 : SIMULATION AVEC CAPTEUR 1024 PX ===")
    np.random.seed(42)
    
    donnees = np.random.randint(0, 256, RS_K, dtype=np.uint8)
    mot_rs = np.frombuffer(RS.encode(bytes(donnees)), dtype=np.uint8)
    bits_emis = np.unpackbits(mot_rs)
    
    spectre_ideal = generer_spectre_ideal(bits_emis, derive=2.0)
    
    print("\n--- Test de robustesse au Capteur (1024 px) ---")
    # On teste directement avec une bonne résolution
    for res in [512, 1024, 2048]:
        for bruit in [0.05, 0.1, 0.2]:
            freq_cam, spectre_cam = simuler_materiel(spectre_ideal, resolution_pixels=res, bruit_electronique=bruit)
            
            bits_lus = lire_spectre_camera(freq_cam, spectre_cam)
            
            err_bits = np.sum(bits_emis != bits_lus)
            mot_lu = np.packbits(bits_lus)
            err_octets = np.sum(mot_rs != mot_lu)
            
            try:
                donnees_corrigees, _, _ = RS.decode(bytes(mot_lu))
                succes = np.array_equal(np.frombuffer(donnees_corrigees, dtype=np.uint8), donnees)
                statut = "✅ SUCCÈS" if succes else "❌ ÉCHEC"
            except reedsolo.ReedSolomonError:
                statut = "❌ ÉCHEC (trop d'erreurs)"
                
            print(f"Résolution={res:4d}px, Bruit={bruit:.2f} | Err bits: {err_bits:2d} | Err octets: {err_octets:2d}/12 | RS: {statut}")

    # Affichage de l'effet du matériel avec 1024 px
    freq_cam, spectre_cam = simuler_materiel(spectre_ideal, resolution_pixels=1024, bruit_electronique=0.1)
    
    plt.figure(figsize=(14, 5))
    plt.plot(FREQ_ACQUISITION, spectre_ideal, label="Signal Idéal (Informatique)", color='blue', alpha=0.5)
    plt.plot(freq_cam, spectre_cam, label="Signal Capteur CCD (1024 px, bruité)", color='orange', marker='.', markersize=1)
    plt.title("Phase 2 : Effet d'un capteur 1024px sur la signature spectrale")
    plt.xlabel("Fréquence")
    plt.ylabel("Intensité")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
