import numpy as np
import matplotlib.pyplot as plt
import reedsolo
from scipy.ndimage import gaussian_filter1d

# ==========================================
# CONFIGURATION (Le retour à l'équilibre)
# ==========================================
RS_N = 12
RS_K = 6
RS = reedsolo.RSCodec(6) # Peut corriger jusqu'à 3 octets

N_BITS = RS_N * 8  # 96 canaux
FREQ_CANAUX = np.linspace(10.0, 1000.0, N_BITS)
FREQ_IDEAL = np.linspace(10.0, 1000.0, 5000)
ESPACEMENT = (1000.0 - 10.0) / (N_BITS - 1)
Q_FACTOR = 200

# ==========================================
# 1. GÉNÉRATION DU SPECTRE IDÉAL
# ==========================================
def lorentzienne(w, w0, Q, A=1.0):
    largeur = w0 / Q
    return A / (1 + 4 * ((w - w0) / largeur)**2)

def generer_spectre_ideal(bits, derive=0.0):
    spectre = np.zeros(len(FREQ_IDEAL))
    for i, bit in enumerate(bits):
        if bit == 1:
            w0 = FREQ_CANAUX[i] + derive 
            spectre += lorentzienne(FREQ_IDEAL, w0, Q=Q_FACTOR)
    return spectre

# ==========================================
# 2. SIMULATEUR MATÉRIEL (CAMERA 512 PX)
# ==========================================
def simuler_camera(spectre_ideal, resolution_pixels=512, bruit_electronique=0.05):
    """
    Simule une vraie caméra avec intégration (moyenne) et flou optique.
    """
    # 1. On découpe le spectre idéal en "buckets" (pixels de la caméra)
    buckets = np.array_split(spectre_ideal, resolution_pixels)
    
    # 2. La caméra intègre la lumière sur chaque pixel
    spectre_camera = np.array([np.mean(b) for b in buckets])
    
    # 3. Flou optique (lentille)
    spectre_camera = gaussian_filter1d(spectre_camera, sigma=1.0)
    
    # 4. Bruit électronique
    bruit = np.random.normal(0, bruit_electronique, len(spectre_camera))
    spectre_camera += bruit
    
    # 5. Saturation et positivité
    spectre_camera = np.clip(spectre_camera, 0, 1.5)
    
    freq_camera = np.linspace(10.0, 1000.0, resolution_pixels)
    
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
            # Corrélation avec le template
            template = lorentzienne(freq_camera[idx_debut:idx_fin], f_c, Q=Q_FACTOR)
            signal_local = spectre_camera[idx_debut:idx_fin]
            
            energie = np.sum(signal_local * template) / np.sum(template * template)
            
            if energie > 0.15: # Seuil abaissé car la caméra intègre et réduit les pics
                bits_lus[i] = 1
                
    return bits_lus

# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================
def main():
    print("=== PHASE 2 : SIMULATION MATÉRIELLE RÉALISTE (512 PX) ===")
    np.random.seed(42)
    
    donnees = np.random.randint(0, 256, RS_K, dtype=np.uint8)
    mot_rs = np.frombuffer(RS.encode(bytes(donnees)), dtype=np.uint8)
    bits_emis = np.unpackbits(mot_rs)
    
    spectre_ideal = generer_spectre_ideal(bits_emis, derive=2.0)
    
    print("\n--- Test de robustesse au Capteur ---")
    for res in [256, 512, 1024]:
        for bruit in [0.02, 0.05, 0.1]:
            freq_cam, spectre_cam = simuler_camera(spectre_ideal, resolution_pixels=res, bruit_electronique=bruit)
            
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

    # Affichage
    freq_cam, spectre_cam = simuler_camera(spectre_ideal, resolution_pixels=512, bruit_electronique=0.05)
    
    plt.figure(figsize=(14, 5))
    plt.plot(FREQ_IDEAL, spectre_ideal, label="Signal Idéal", color='blue', alpha=0.5)
    plt.plot(freq_cam, spectre_cam, label="Signal Capteur CCD (512 px)", color='orange', marker='.', markersize=2)
    plt.title("Effet d'un capteur 512px (96 canaux, RS(12,6))")
    plt.xlabel("Fréquence")
    plt.ylabel("Intensité")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
