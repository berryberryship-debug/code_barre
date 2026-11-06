import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_widths
import reedsolo

# ==========================================
# CONFIGURATION
# ==========================================
RS_N = 12
RS_K = 6
RS = reedsolo.RSCodec(6)

N_BITS = RS_N * 8 # 96 canaux
# Grille théorique des 96 fréquences
FREQ_CANAUX = np.linspace(10.0, 100.0, N_BITS)

# Grille d'acquisition ultra-fine (le "spectromètre" à 4000 points)
FREQ_ACQUISITION = np.linspace(10.0, 100.0, 4000)

# Facteur de qualité très élevé pour des pics ultra-fins
Q_FACTOR = 1000

# ==========================================
# 1. GÉNÉRATION DU SPECTRE
# ==========================================
def lorentzienne(w, w0, Q, A=1.0):
    largeur = w0 / Q
    return A / (1 + 4 * ((w - w0) / largeur)**2)

def generer_spectre(bits, bruit=0.05, derive=0.0, variation_Q=0.0):
    spectre = np.random.normal(0, bruit, len(FREQ_ACQUISITION))
    Q_actuel = Q_FACTOR + variation_Q
    
    for i, bit in enumerate(bits):
        if bit == 1:
            w0 = FREQ_CANAUX[i] + derive 
            pic = lorentzienne(FREQ_ACQUISITION, w0, Q=Q_actuel)
            spectre += pic
            
    return np.clip(spectre, 0, None)

# ==========================================
# 2. LECTEUR SPECTRAL (FILTRE ADAPTÉ)
# ==========================================
def lire_spectre(spectre):
    """
    Utilise find_peaks avec des critères stricts (prominence) 
    pour ignorer le bruit de fond.
    """
    # On cherche les pics avec une hauteur de 0.4 et une proéminence de 0.3
    # (La proéminence exige que le pic ressorte nettement du bruit environnant)
    pics, proprietes = find_peaks(
        spectre, 
        height=0.4, 
        prominence=0.3, 
        distance=20 # Au moins 20 points d'acquisition entre deux pics (évite les doublons de bruit)
    )
    
    bits_retrouves = np.zeros(N_BITS, dtype=np.uint8)
    
    for pic_idx in pics:
        # On associe le pic à la fréquence théorique la plus proche
        freq_pic = FREQ_ACQUISITION[pic_idx]
        idx_bit = np.argmin(np.abs(FREQ_CANAUX - freq_pic))
        bits_retrouves[idx_bit] = 1
        
    return bits_retrouves

# ==========================================
# 3. CONVERSION ET CORRECTION
# ==========================================
def octets_vers_bits(octets):
    return np.unpackbits(np.asarray(octets, dtype=np.uint8))

def bits_vers_octets(bits):
    return np.packbits(np.asarray(bits, dtype=np.uint8))

# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================
def main():
    print("=== TEST DE TRANSMISSION SPECTRALE V4 (FILTRE ADAPTÉ) ===")
    np.random.seed(42)
    
    donnees = np.random.randint(0, 256, RS_K, dtype=np.uint8)
    print(f"Données originales : {donnees}")
    
    mot_rs = np.frombuffer(RS.encode(bytes(donnees)), dtype=np.uint8)
    bits_emis = octets_vers_bits(mot_rs)
    
    spectre_propre = generer_spectre(bits_emis, bruit=0.0, derive=0.0)
    
    print("\n--- Test avec perturbations (Monte Carlo) ---")
    for bruit in [0.05, 0.1, 0.2]:
        for derive in [0.0, 0.5, 1.0]:
            spectre_bruite = generer_spectre(
                bits_emis, 
                bruit
