import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import rotate, gaussian_filter

def generer_materiau(N=128, densite=0.05):
    """Genere un materiau avec des particules (diffuseurs) 3D."""
    materiau = np.zeros((N, N))
    n_particules = int(N * N * densite)
    for _ in range(n_particules):
        x = np.random.randint(0, N)
        y = np.random.randint(0, N)
        materiau[x, y] = 1.0
    # On lisse un peu pour simuler la taille physique des particules
    return gaussian_filter(materiau, sigma=1.0)

def simuler_lecture_laser(materiau, rotation_angle=0.0, bruit_photon_scale=1.0, bruit_lecture=0.05):
    """Simule le motif de diffraction avec imperfections."""
    # 1. Petite rotation (defaut de positionnement du lecteur)
    if rotation_angle != 0:
        materiau_rot = rotate(materiau, rotation_angle, reshape=False, mode='constant')
    else:
        materiau_rot = materiau
        
    # 2. Diffraction (FFT2)
    champ_diffracte = np.fft.fftshift(np.fft.fft2(materiau_rot))
    intensite = np.abs(champ_diffracte)**2
    
    # 3. Normalisation (0 a 1)
    intensite = intensite / np.max(intensite)
    
    # 4. Bruit de photon (Loi de Poisson)
    # Plus le signal est fort, plus le bruit relatif est faible
    intensite_poisson = np.random.poisson(intensite * 1000) / 1000.0 
    
    # 5. Bruit de lecture de la camera (Gaussien relatif)
    bruit = np.random.normal(0, bruit_lecture, intensite.shape)
    intensite_bruitee = intensite_poisson + bruit
    
    # On garde l'intensite positive
    return np.clip(intensite_bruitee, 0, 1)

def extraire_cle(intensite):
    """Extrait des bits en comparant chaque pixel a son voisin de droite."""
    # On compare intensite[:, :-1] avec intensite[:, 1:]
    bits = (intensite[:, :-1] > intensite[:, 1:]).astype(int)
    return bits.flatten()

def distance_hamming(cle1, cle2):
    return np.mean(cle1 != cle2) * 100

def main():
    print("=== V29.1: SIMULATEUR PUF OPTIQUE REALISTE ===")
    
    N = 128
    np.random.seed(42)
    materiau = generer_materiau(N)
    
    # 1. Lecture de reference (conditions parfaites)
    intensite_ref = simuler_lecture_laser(materiau, rotation_angle=0.0, bruit_photon_scale=1.0, bruit_lecture=0.0)
    cle_ref = extraire_cle(intensite_ref)
    print(f"Cle de reference generee : {len(cle_ref)} bits")
    
    # 2. Test de robustesse (Bruit de photon + Bruit de lecture)
    print("\n--- Test de robustesse au bruit de camera ---")
    bruits_lecture = [0.0, 0.01, 0.05, 0.1, 0.2, 0.5]
    
    for b in bruits_lecture:
        intensite_bruitee = simuler_lecture_laser(materiau, rotation_angle=0.0, bruit_lecture=b)
        cle_bruitee = extraire_cle(intensite_bruitee)
        err = distance_hamming(cle_ref, cle_bruitee)
        print(f"Bruit de lecture = {b:.2f} | Taux d'erreur = {err:5.2f} %")

    # 3. Test de robustesse (Rotation mecanique)
    print("\n--- Test de robustesse au positionnement (Rotation) ---")
    angles = [0.0, 0.1, 0.5, 1.0, 2.0]
    
    for a in angles:
        intensite_rot = simuler_lecture_laser(materiau, rotation_angle=a, bruit_lecture=0.01)
        cle_rot = extraire_cle(intensite_rot)
        err = distance_hamming(cle_ref, cle_rot)
        print(f"Rotation = {a:.1f} deg  | Taux d'erreur = {err:5.2f} %")
        
    # 4. Test d'unicite (Materiau different)
    print("\n--- Test d'unicite (Inter-device) ---")
    materiau_2 = generer_materiau(N)
    intensite_2 = simuler_lecture_laser(materiau_2, rotation_angle=0.0, bruit_lecture=0.0)
    cle_2 = extraire_cle(intensite_2)
    print(f"Materiau A vs Materiau B : {distance_hamming(cle_ref, cle_2):5.2f} % d'erreur (doit etre proche de 50%)")

if __name__ == "__main__":
    main()
