import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

def generer_masque_phase(N=128):
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

def distance_hamming(cle1, cle2):
    n = min(len(cle1), len(cle2))
    return np.mean(cle1[:n] != cle2[:n]) * 100

def main():
    print("=== TEST D'UNICITE (INTER-DEVICE) SUR 100 PUF ===")
    
    N = 128
    n_puces = 100
    np.random.seed(42) # Pour la reproductibilité
    
    cles = []
    
    # 1. Génération et lecture des 100 puces
    print(f"Génération et lecture de {n_puces} matériaux différents...")
    for i in range(n_puces):
        masque = generer_masque_phase(N)
        # On lit la puce avec un bruit normal de caméra
        intensite = simuler_lecture_laser(masque, bruit_camera=0.01)
        cle = extraire_cle_robuste(intensite)
        cles.append(cle)
        
    # 2. Calcul de toutes les distances croisées
    print("Calcul des distances de Hamming inter-puces...")
    distances = []
    
    # On compare chaque puce avec toutes les autres (sans se comparer avec soi-même)
    for i in range(n_puces):
        for j in range(i + 1, n_puces):
            d = distance_hamming(cles[i], cles[j])
            distances.append(d)
            
    distances = np.array(distances)
    
    # 3. Statistiques
    moyenne = np.mean(distances)
    ecart_type = np.std(distances)
    min_dist = np.min(distances)
    max_dist = np.max(distances)
    
    print("\n--- RÉSULTATS STATISTIQUES ---")
    print(f"Nombre total de comparaisons : {len(distances)}")
    print(f"Distance moyenne : {moyenne:.2f} % (Idéal = 50%)")
    print(f"Écart-type : {ecart_type:.2f} % (Idéal < 5%)")
    print(f"Distance minimale (Pire cas) : {min_dist:.2f} %")
    print(f"Distance maximale (Meilleur cas) : {max_dist:.2f} %")
    
    if min_dist > 40.0:
        print("\n✅ SUCCÈS : Aucune collision détectée. Les 100 puces sont uniques.")
    else:
        print("\n⚠️ ATTENTION : Certaines puces se ressemblent trop (risque de collision).")

    # 4. Affichage graphique (Histogramme)
    plt.figure(figsize=(8, 5))
    plt.hist(distances, bins=20, color='purple', edgecolor='black', alpha=0.7)
    plt.axvline(50, color='red', linestyle='dashed', linewidth=2, label='Idéal (50%)')
    plt.title("Distribution de l'unicité des PUF (Inter-device)")
    plt.xlabel("Distance de Hamming (%)")
    plt.ylabel("Nombre de paires")
    plt.legend()
    plt.grid(axis='y', alpha=0.5)
    plt.show()

if __name__ == "__main__":
    main()
