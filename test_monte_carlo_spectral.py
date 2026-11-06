import numpy as np
import reedsolo
import time

# ==========================================
# CONFIGURATION OPTIMISÉE
# ==========================================
RS_N = 12
RS_K = 6
RS = reedsolo.RSCodec(6)

N_BITS = RS_N * 8 
FREQ_CANAUX = np.linspace(10.0, 1000.0, N_BITS)

# Augmentation de la résolution d'acquisition (10000 points)
FREQ_ACQUISITION = np.linspace(10.0, 1000.0, 10000)
ESPACEMENT = (1000.0 - 10.0) / (N_BITS - 1)

# Facteur Q réduit à 80 pour des pics plus larges
Q_FACTOR = 80

# ==========================================
# FONCTIONS DU MOTEUR PHYSIQUE
# ==========================================
def lorentzienne(w, w0, Q, A=1.0):
    largeur = w0 / Q
    return A / (1 + 4 * ((w - w0) / largeur)**2)

def generer_spectre(bits, bruit, derive):
    spectre = np.random.normal(0, bruit, len(FREQ_ACQUISITION))
    for i, bit in enumerate(bits):
        if bit == 1:
            w0 = FREQ_CANAUX[i] + derive 
            spectre += lorentzienne(FREQ_ACQUISITION, w0, Q=Q_FACTOR)
    # On évite le clip strict à 0 pour ne pas biaiser le bruit
    return spectre

def lire_spectre(spectre):
    bits_lus = np.zeros(N_BITS, dtype=np.uint8)
    demi_fenetre = ESPACEMENT / 2 
    
    for i in range(N_BITS):
        f_c = FREQ_CANAUX[i]
        idx_debut = np.searchsorted(FREQ_ACQUISITION, f_c - demi_fenetre)
        idx_fin = np.searchsorted(FREQ_ACQUISITION, f_c + demi_fenetre)
        
        if idx_fin > idx_debut:
            signal_local = spectre[idx_debut:idx_fin]
            max_local = np.max(signal_local)
            
            # Seuil adaptatif : on regarde si le pic dépasse 4 fois le bruit de fond local
            bruit_local = np.median(signal_local)
            seuil = max(0.3, bruit_local + 0.2)
            
            if max_local > seuil:
                bits_lus[i] = 1
    return bits_lus

# ==========================================
# MONTE CARLO (100 ITÉRATIONS)
# ==========================================
def main():
    print("=== MONTE CARLO : VALIDATION SPECTRALE (V6) ===")
    print("100 simulations avec des donnees et du bruit aleatoires.\n")
    
    np.random.seed(123) 
    
    n_iterations = 100
    succes_count = 0
    erreurs_moyennes = 0
    
    bruit_fixe = 0.05
    derive_max = 1.0
    
    start_time = time.time()
    
    for i in range(n_iterations):
        if (i + 1) % 10 == 0:
            print(f"Progression : {i + 1}/{n_iterations}...")
            
        donnees = np.random.randint(0, 256, RS_K, dtype=np.uint8)
        mot_rs = np.frombuffer(RS.encode(bytes(donnees)), dtype=np.uint8)
        bits_emis = np.unpackbits(mot_rs)
        
        derive_aleatoire = np.random.uniform(-derive_max, derive_max)
        
        spectre = generer_spectre(bits_emis, bruit=bruit_fixe, derive=derive_aleatoire)
        bits_lus = lire_spectre(spectre)
        
        mot_lu = np.packbits(bits_lus)
        err_bits = np.sum(bits_emis != bits_lus)
        erreurs_moyennes += err_bits
        
        try:
            decoded = RS.decode(bytes(mot_lu))
            if isinstance(decoded, tuple):
                decoded = decoded[0]
            
            donnees_corrigees = np.frombuffer(bytes(decoded), dtype=np.uint8)
            
            if np.array_equal(donnees_corrigees, donnees):
                succes_count += 1
        except Exception:
            pass 
            
    temps = time.time() - start_time
    taux_succes = (succes_count / n_iterations) * 100
    err_moy = erreurs_moyennes / n_iterations
    
    print("\n" + "="*40)
    print(f"--- RESULTATS SUR {n_iterations} LECTURES ---")
    print(f"Bruit de fond      : {bruit_fixe}")
    print(f"Derive max         : +/- {derive_max} unites")
    print(f"Temps d'execution  : {temps:.2f} secondes")
    print(f"Erreur bits moyenne: {err_moy:.2f} / 96")
    print(f"TAUX DE SUCCES     : {taux_succes:.1f} %")
    
    if taux_succes >= 90:
        print("\n✅ VALIDATION MONTE CARLO REUSSIE !")
    else:
        print("\n⚠️ Le systeme est encore trop fragile.")

if __name__ == "__main__":
    main()
