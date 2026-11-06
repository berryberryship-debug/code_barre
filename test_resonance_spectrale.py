import numpy as np
import matplotlib.pyplot as plt
import reedsolo

# ==========================================
# CONFIGURATION
# ==========================================
RS_N = 12
RS_K = 6
RS = reedsolo.RSCodec(6)

N_BITS = RS_N * 8 # 96 canaux
# 1. Grille des fréquences théoriques (les 96 canaux)
FREQ_CANAUX = np.linspace(10.0, 100.0, N_BITS)

# 2. Grille d'acquisition ultra-fine (le "spectromètre" à 2000 points)
# On couvre la même plage (10 à 100) avec beaucoup plus de résolution
FREQ_ACQUISITION = np.linspace(10.0, 100.0, 2000)

# Facteur de qualité (Q). Plus Q est élevé, plus le pic est fin.
# Q=200 donne une largeur d'environ 0.5 à 100THz, ce qui sépare bien les canaux espacés de 0.94.
Q_FACTOR = 200
SEUIL_DETECTION = 0.3

# ==========================================
# 1. GÉNÉRATION DU SPECTRE (PHYSIQUE)
# ==========================================
def lorentzienne(w, w0, Q, A=1.0):
    """Génère un pic de résonance centré sur w0 avec un facteur de qualité Q."""
    largeur = w0 / Q
    return A / (1 + 4 * ((w - w0) / largeur)**2)

def generer_spectre(bits, bruit=0.05, derive=0.0, variation_Q=0.0):
    """
    Crée le spectre optique sur la grille d'acquisition fine.
    Un bit à 1 = présence d'un pic de résonance.
    Un bit à 0 = pas de pic (bruit de fond).
    """
    # Bruit de fond thermique
    spectre = np.random.normal(0, bruit, len(FREQ_ACQUISITION))
    
    Q_actuel = Q_FACTOR + variation_Q
    
    for i, bit in enumerate(bits):
        if bit == 1:
            # La fréquence du canal se décale avec la dérive
            w0 = FREQ_CANAUX[i] + derive 
            pic = lorentzienne(FREQ_ACQUISITION, w0, Q=Q_actuel)
            spectre += pic
            
    return np.clip(spectre, 0, None)

# ==========================================
# 2. LECTEUR SPECTRAL (MÉTHODE ROBUSTE)
# ==========================================
def lire_spectre(spectre, derive_max_attendue=1.0):
    """
    Le lecteur n'utilise pas find_peaks.
    Pour chaque canal, il cherche le maximum local dans une fenêtre
    autour de la fréquence théorique (pour compenser la dérive).
    """
    bits_lus = np.zeros(N_BITS, dtype=np.uint8)
    
    for i in range(N_BITS):
        f_c = FREQ_CANAUX[i]
        
        # On cherche dans une fenêtre de +/- derive_max_attendue autour du canal
        idx_debut = np.searchsorted(FREQ_ACQUISITION, f_c - derive_max_attendue)
        idx_fin = np.searchsorted(FREQ_ACQUISITION, f_c + derive_max_attendue)
        
        if idx_fin > idx_debut:
            # On prend le maximum local
            max_local = np.max(spectre[idx_debut:idx_fin])
            if max_local > SEUIL_DETECTION:
                bits_lus[i] = 1
                
    return bits_lus

# ==========================================
# 3. CONVERSION ET CORRECTION (REED-SOLOMON)
# ==========================================
def octets_vers_bits(octets):
    return np.unpackbits(np.asarray(octets, dtype=np.uint8))

def bits_vers_octets(bits):
    return np.packbits(np.asarray(bits, dtype=np.uint8))

# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================
def main():
    print("=== TEST DE TRANSMISSION SPECTRALE V3 (96 CANAUX) ===")
    np.random.seed(42)
    
    # 1. Données originales
    donnees = np.random.randint(0, 256, RS_K, dtype=np.uint8)
    print(f"Données originales : {donnees}")
    
    # 2. Encodage RS
    mot_rs = np.frombuffer(RS.encode(bytes(donnees)), dtype=np.uint8)
    bits_emis = octets_vers_bits(mot_rs)
    
    # 3. Spectre propre (sans perturbation)
    spectre_propre = generer_spectre(bits_emis, bruit=0.0, derive=0.0)
    
    # 4. Test de robustesse (Monte Carlo sur le bruit et la dérive)
    print("\n--- Test avec perturbations (Bruit + Dérive) ---")
    for bruit in [0.05, 0.1, 0.2]:
        for derive in [0.0, 0.5, 1.0]:
            spectre_bruite = generer_spectre(
                bits_emis, 
                bruit=bruit, 
                derive=derive
            )
            
            # Lecture
            bits_lus = lire_spectre(spectre_bruite, derive_max_attendue=1.5)
            mot_lu = bits_vers_octets(bits_lus)
            
            # Décodage RS
            try:
                donnees_corrigees, _, _ = RS.decode(bytes(mot_lu))
                succes = np.array_equal(np.frombuffer(donnees_corrigees, dtype=np.uint8), donnees)
                statut = "✅ SUCCÈS" if succes else "❌ ÉCHEC (mauvais décodage)"
            except reedsolo.ReedSolomonError:
                statut = "❌ ÉCHEC (trop d'erreurs)"
            
            # Affichage
            erreurs = np.sum(bits_emis != bits_lus)
            print(f"Bruit={bruit:.2f}, Dérive={derive:.1f} | Erreurs bits: {erreurs:2d}/96 | RS: {statut}")

    # 5. Affichage du spectre
    plt.figure(figsize=(14, 5))
    plt.plot(FREQ_ACQUISITION, spectre_propre, label="Spectre propre", color='blue', alpha=0.6)
    
    # On affiche un spectre bruité spécifique
    spectre_test = generer_spectre(bits_emis, bruit=0.1, derive=0.5)
    plt.plot(FREQ_ACQUISITION, spectre_test, label="Spectre bruité (bruit=0.1, dérive=0.5)", color='orange', alpha=0.8)
    
    # On affiche les fréquences des canaux théoriques
    for i in range(N_BITS):
        plt.axvline(x=FREQ_CANAUX[i], color='red', linestyle=':', alpha=0.1)
        
    plt.title("Signature Spectrale (Grille fine, 96 canaux, Q=200)")
    plt.xlabel("Fréquence (unités arbitraires)")
    plt.ylabel("Intensité (Facteur Q)")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
