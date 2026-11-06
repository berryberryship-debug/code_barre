import numpy as np
import matplotlib.pyplot as plt
import reedsolo
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

# ==========================================
# CONFIGURATION (Identique à la Phase 1)
# ==========================================
RS_N = 12
RS_K = 6
RS = reedsolo.RSCodec(6)

N_BITS = RS_N * 8 
FREQ_CANAUX = np.linspace(10.0, 1000.0, N_BITS)
FREQ_ACQUISITION = np.linspace(10.0, 1000.0, 5000) # Le spectre "idéal"
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
# 2. SIMULATEUR MATÉRIEL (LE NOUVEAU BLOC)
# ==========================================
def simuler_materiel(spectre_ideal, resolution_pixels=256, bruit_electronique=0.05, saturation=1.2):
    """
    Fait passer le spectre par un capteur CCD réel.
    1. Sous-échantillonnage (la caméra a moins de pixels que la simulation)
    2. Fonction d'étalement (flou optique)
    3. Bruit électronique
    4. Saturation (si un pic est trop fort, il est écrêté)
    """
    # A. Le capteur a une résolution limitée (ex: 256 pixels)
    freq_camera = np.linspace(10.0, 1000.0, resolution_pixels)
    spectre_camera = np.interp(freq_camera, FREQ_ACQUISITION, spectre_ideal)
    
    # B. Flou optique (Point Spread Function de la lentille)
    # Le signal est "étalé" sur les pixels voisins
    spectre_camera = gaussian_filter1d(spectre_camera, sigma=1.5)
    
    # C. Bruit du capteur (électronique)
    bruit = np.random.normal(0, bruit_electronique, len(freq_camera))
    spectre_camera += bruit
    
    # D. Saturation
    spectre_camera = np.clip(spectre_camera, 0, saturation)
    
    return freq_camera, spectre_camera

# ==========================================
# 3. LECTEUR (DOIT S'ADAPTER À LA CAMÉRA)
# ==========================================
def lire_spectre_camera(freq_camera, spectre_camera):
    """
    Lit l'image de la caméra (basse résolution) au lieu du spectre idéal.
    """
    bits_lus = np.zeros(N_BITS, dtype=np.uint8)
    demi_fenetre = ESPACEMENT / 2 
    
    for i in range(N_BITS):
        f_c = FREQ_CANAUX[i]
        
        # On cherche dans l'image de la caméra
        idx_debut = np.searchsorted(freq_camera, f_c - demi_fenetre)
        idx_fin = np.searchsorted(freq_camera, f_c + demi_fenetre)
        
        if idx_fin > idx_debut:
            # On utilise toujours la corrélation avec le template (Matched Filter)
            # Mais on le fait sur les données de la caméra
            template = lorentzienne(freq_camera[idx_debut:idx_fin], f_c, Q=Q_FACTOR)
            signal_local = spectre_camera[idx_debut:idx_fin]
            
            energie = np.sum(signal_local * template) / np.sum(template * template)
            
            # Le seuil est ajusté car le signal est flouté et saturé
            if energie > 0.3: 
                bits_lus[i] = 1
                
    return bits_lus

# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================
def main():
    print("=== PHASE 2 : SIMULATION DES IMPERFECTIONS MATÉRIELLES ===")
    np.random.seed(42)
    
    donnees = np.random.randint(0, 256, RS_K, dtype=np.uint8)
    mot_rs = np.frombuffer(RS.encode(bytes(donnees)), dtype=np.uint8)
    bits_emis = np.unpackbits(mot_rs)
    
    # 1. Génération du spectre parfait (comme en Phase 1)
    spectre_ideal = generer_spectre_ideal(bits_emis, derive=2.0)
    
    print("\n--- Test de robustesse au Capteur ---")
    # On teste différentes résolutions de caméra et différents bruits
    for res in [128, 256, 512]:
        for bruit in [0.02, 0.05, 0.1]:
            freq_cam, spectre_cam = simuler_materiel(spectre_ideal, resolution_pixels=res, bruit_electronique=bruit)
            
            bits_lus = lire_spectre_camera(freq_cam, spectre_cam)
            
            # Calcul des erreurs
            err_bits = np.sum(bits_emis != bits_lus)
            mot_lu = np.packbits(bits_lus)
            err_octets = np.sum(mot_rs != mot_lu)
            
            # Décodage Reed-Solomon
            try:
                donnees_corrigees, _, _ = RS.decode(bytes(mot_lu))
                succes = np.array_equal(np.frombuffer(donnees_corrigees, dtype=np.uint8), donnees)
                statut = "✅ SUCCÈS" if succes else "❌ ÉCHEC"
            except reedsolo.ReedSolomonError:
                statut = "❌ ÉCHEC (trop d'erreurs)"
                
            print(f"Résolution={res:3d}px, Bruit={bruit:.2f} | Err bits: {err_bits:2d} | Err octets: {err_octets:2d}/12 | RS: {statut}")

    # Affichage de l'effet du matériel
    freq_ideal = FREQ_ACQUISITION
    freq_cam, spectre_cam = simuler_materiel(spectre_ideal, resolution_pixels=128, bruit_electronique=0.05)
    
    plt.figure(figsize=(14, 5))
    plt.plot(freq_ideal, spectre_ideal, label="Signal Idéal (Informatique)", color='blue', alpha=0.5)
    plt.plot(freq_cam, spectre_cam, label="Signal Capteur CCD (128 px, bruité, saturé)", color='orange', marker='.', markersize=2)
    plt.title("Effet des imperfections matérielles sur la signature spectrale")
    plt.xlabel("Fréquence")
    plt.ylabel("Intensité")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
