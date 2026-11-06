import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import reedsolo

# ==========================================
# CONFIGURATION
# ==========================================
RS_N = 12
RS_K = 6
RS = reedsolo.RSCodec(6)

N_BITS = RS_N * 8 
FREQ_CANAUX = np.linspace(10.0, 1000.0, N_BITS)
FREQ_ACQUISITION = np.linspace(10.0, 1000.0, 5000)

# L'espacement entre deux canaux
ESPACEMENT = (1000.0 - 10.0) / (N_BITS - 1) # ~10.42

Q_FACTOR = 200

# ==========================================
# 1. GÉNÉRATION DU SPECTRE
# ==========================================
def lorentzienne(w, w0, Q, A=1.0):
    largeur = w0 / Q
    return A / (1 + 4 * ((w - w0) / largeur)**2)

def generer_spectre(bits, bruit=0.05, derive=0.0):
    spectre = np.random.normal(0, bruit, len(FREQ_ACQUISITION))
    for i, bit in enumerate(bits):
        if bit == 1:
            w0 = FREQ_CANAUX[i] + derive 
            spectre += lorentzienne(FREQ_ACQUISITION, w0, Q=Q_FACTOR)
    return np.clip(spectre, 0, None)

# ==========================================
# 2. LECTEUR V5 (DÉTECTION GLOBALE)
# ==========================================
def lire_spectre_v5(spectre):
    """
    Détecte tous les pics du spectre, puis assigne chacun au canal le plus proche.
    Si un pic est trop loin d'un canal, il est ignoré (c'est du bruit).
    """
    # On cherche les pics avec une proéminence de 0.3
    pics, props = find_peaks(spectre, height=0.4, prominence=0.3, distance=10)
    
    bits_lus = np.zeros(N_BITS, dtype=np.uint8)
    
    for pic_idx in pics:
        f_pic = FREQ_ACQUISITION[pic_idx]
        
        # Trouver le canal dont la fréquence est la plus proche
        canal_idx = np.argmin(np.abs(FREQ_CANAUX - f_pic))
        distance = np.abs(FREQ_CANAUX[canal_idx] - f_pic)
        
        # On accepte le pic s'il est à moins d'un demi-espacement du canal
        # (cela permet une dérive allant jusqu'à ~5.2 unités)
        if distance < (ESPACEMENT / 2):
            bits_lus[canal_idx] = 1
            
    return bits_lus

# ==========================================
# 3. CONVERSION ET ERREURS
# ==========================================
def octets_vers_bits(octets): return np.unpackbits(np.asarray(octets, dtype=np.uint8))
def bits_vers_octets(bits): return np.packbits(np.asarray(bits, dtype=np.uint8))

def compter_erreurs_symboles(ref, lu):
    """Compte le nombre d'octets différents (erreurs de symbole pour RS)."""
    return int(np.sum(ref != lu))

# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================
def main():
    print("=== TEST SPECTRAL V5 (DÉTECTION GLOBALE) ===")
    np.random.seed(42)
    
    donnees = np.random.randint(0, 256, RS_K, dtype=np.uint8)
    print(f"Données originales : {donnees}")
    
    mot_rs = np.frombuffer(RS.encode(bytes(donnees)), dtype=np.uint8)
    bits_emis = octets_vers_bits(mot_rs)
    
    spectre_propre = generer_spectre(bits_emis, bruit=0.0, derive=0.0)
    
    print("\n--- Test avec perturbations ---")
    # On teste des dérives allant jusqu'à 4.0 (dans la tolérance de 5.2)
    for bruit in [0.05, 0.1, 0.2]:
        for derive in [0.0, 2.0, 4.0]:
            spectre_bruite = generer_spectre(bits_emis, bruit=bruit, derive=derive)
            bits_lus = lire_spectre_v5(spectre_bruite)
            mot_lu = bits_vers_octets(bits_lus)
            
            # 1. Erreurs binaires
            err_bits = np.sum(bits_emis != bits_lus)
            
            # 2. Erreurs de symboles (octets)
            err_sym = compter_erreurs_symboles(mot_rs, mot_lu)
            
            # 3. Décodage RS
            try:
                donnees_corrigees, _, _ = RS.decode(bytes(mot_lu))
                succes = np.array_equal(np.frombuffer(donnees_corrigees, dtype=np.uint8), donnees)
                statut = "✅ SUCCÈS" if succes else "❌ ÉCHEC (mauvais décodage)"
            except reedsolo.ReedSolomonError:
                statut = "❌ ÉCHEC (trop d'erreurs)"
            
            print(f"Bruit={bruit:.2f}, Dérive={derive:.1f} | Err bits: {err_bits:2d}/96 | Err octets: {err_sym:2d}/12 | RS: {statut}")

    # Affichage du spectre
    plt.figure(figsize=(14, 5))
    plt.plot(FREQ_ACQUISITION, spectre_propre, label="Spectre propre", color='blue', alpha=0.6)
    spectre_test = generer_spectre(bits_emis, bruit=0.1, derive=4.0)
    plt.plot(FREQ_ACQUISITION, spectre_test, label="Spectre bruité (bruit=0.1, dérive=4.0)", color='orange', alpha=0.8)
    plt.title("Signature Spectrale V5 (Détection Globale + Assignation)")
    plt.xlabel("Fréquence (unités arbitraires)")
    plt.ylabel("Intensité")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
