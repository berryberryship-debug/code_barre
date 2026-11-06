import numpy as np
from scipy.ndimage import gaussian_filter, rotate

def generer_masque_phase(N=128):
    phase = np.random.uniform(0, 2*np.pi, (N, N))
    return np.exp(1j * phase)

def simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.01):
    if angle != 0.0:
        # On tourne le masque avec order=0 pour éviter le flou
        masque_rot = rotate(np.real(masque), angle, reshape=False, order=0) + \
                     1j * rotate(np.imag(masque), angle, reshape=False, order=0)
    else:
        masque_rot = masque

    champ = np.fft.fftshift(np.fft.fft2(masque_rot))
    intensite = np.abs(champ)**2
    intensite = intensite / np.max(intensite)
    intensite_bruitee = intensite + np.random.normal(0, bruit_camera, intensite.shape)
    return np.clip(intensite_bruitee, 0, 1)

def extraire_cle_robuste(intensite, block_size=16):
    intensite_floue = gaussian_filter(intensite, sigma=3.0)
    N = intensite.shape[0]
    n_blocks = N // block_size
    blocs = intensite_floue.reshape(n_blocks, block_size, n_blocks, block_size)
    moyennes = blocs.mean(axis=(1, 3))
    bits = (moyennes[:, :-1] > moyennes[:, 1:]).astype(np.uint8)
    return bits.flatten()

def distance_hamming(cle1, cle2):
    n = min(len(cle1), len(cle2))
    return np.mean(cle1[:n] != cle2[:n]) * 100

def redresser_image(intensite_bruitee, intensite_ref, angles_cherches):
    meilleur_angle = 0.0
    meilleure_correlation = -1.0
    
    for a in angles_cherches:
        # On tourne avec order=0 pour la recherche aussi
        img_redressee = rotate(intensite_bruitee, a, reshape=False, order=0)
        corr = np.corrcoef(img_redressee.flatten(), intensite_ref.flatten())[0, 1]
        
        if corr > meilleure_correlation:
            meilleure_correlation = corr
            meilleur_angle = a
            
    return meilleur_angle, meilleure_correlation

def main():
    print("=== TEST DE ROBUSTESSE AU POSITIONNEMENT (ORDER=0) ===")
    
    N = 128
    np.random.seed(42)
    masque = generer_masque_phase(N)
    
    intensite_ref = simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.0)
    cle_ref = extraire_cle_robuste(intensite_ref)
    
    angle_vrai_defaut = 3.5
    print(f"\nSimulation d'une lecture avec un defaut de {angle_vrai_defaut} degres...")
    intensite_bruitee = simuler_lecture_laser(masque, angle=angle_vrai_defaut, bruit_camera=0.01)
    
    cle_sans_recalage = extraire_cle_robuste(intensite_bruitee)
    err_sans = distance_hamming(cle_ref, cle_sans_recalage)
    print(f"-> Erreur SANS recalage : {err_sans:.2f}% (La cle est detruite)")
    
    print("-> L'algorithme cherche le meilleur angle de correction...")
    angles_a_tester = np.arange(-6.0, 6.1, 0.5) 
    
    angle_trouve, correlation = redresser_image(intensite_bruitee, intensite_ref, angles_a_tester)
    
    # Application de la correction avec order=0
    intensite_corrigee = rotate(intensite_bruitee, angle_trouve, reshape=False, order=0)
    cle_avec_recalage = extraire_cle_robuste(intensite_corrigee)
    err_avec = distance_hamming(cle_ref, cle_avec_recalage)
    
    print(f"-> Angle de correction trouve : {angle_trouve:.1f} degres (Correlation : {correlation:.3f})")
    print(f"-> Erreur AVEC recalage  : {err_avec:.2f}% (La cle est sauvee !)")

if __name__ == "__main__":
    main()
