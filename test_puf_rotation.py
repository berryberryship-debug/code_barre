import numpy as np
from scipy.ndimage import gaussian_filter, rotate
import reedsolo

def generer_masque_phase(N=128):
    return np.exp(1j * np.random.uniform(0, 2*np.pi, (N, N)))

def simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.01):
    if angle != 0.0:
        masque_rot = rotate(np.real(masque), angle, reshape=False, order=3) + \
                     1j * rotate(np.imag(masque), angle, reshape=False, order=3)
    else:
        masque_rot = masque
    champ = np.fft.fftshift(np.fft.fft2(masque_rot))
    intensite = np.abs(champ)**2
    intensite = intensite / np.max(intensite)
    intensite_bruitee = intensite + np.random.normal(0, bruit_camera, intensite.shape)
    return np.clip(intensite_bruitee, 0, 1)

def recaler_image(image_bruitee, image_ref, plage_angle=6.0, pas=0.5):
    meilleur_angle = 0.0
    meilleure_corr = -1.0
    angles_test = np.arange(-plage_angle, plage_angle + pas/2, pas)
    
    ref_flat = image_ref.flatten()
    ref_std = np.std(ref_flat)
    
    for a in angles_test:
        img_rot = rotate(image_bruitee, a, reshape=False, order=1)
        rot_flat = img_rot.flatten()
        std_prod = ref_std * np.std(rot_flat)
        if std_prod > 0:
            corr = np.cov(rot_flat, ref_flat)[0, 1] / std_prod
            if corr > meilleure_corr:
                meilleure_corr = corr
                meilleur_angle = a
                
    image_corrigee = rotate(image_bruitee, meilleur_angle, reshape=False, order=3)
    return image_corrigee, meilleur_angle, meilleure_corr

def extraire_bits_et_masque(intensite, block_size=4):
    intensite_floue = gaussian_filter(intensite, sigma=2.0)
    N = intensite.shape[0]
    n_blocks = N // block_size
    blocs = intensite_floue.reshape(n_blocks, block_size, n_blocks, block_size)
    moyennes = blocs.mean(axis=(1, 3))
    diff = moyennes[:, :-1] - moyennes[:, 1:]
    
    y, x = np.ogrid[:diff.shape[0], :diff.shape[1]]
    centre_y, centre_x = (diff.shape[0] - 1) / 2, (diff.shape[1] - 1) / 2
    masque_cercle = ((x - centre_x)**2 + (y - centre_y)**2) <= (min(centre_y, centre_x) * 0.85)**2
    
    seuil = np.median(np.abs(diff[masque_cercle]))
    masque_valide = masque_cercle & (np.abs(diff) > seuil)
    bits = (diff > 0).astype(np.uint8)
    return bits.flatten(), masque_valide.flatten()

def distance_hamming(b1, b2):
    return np.mean(b1 != b2) * 100

def test_monte_carlo_rotation(n_iterations=50, angle_reel=3.5, bruit=0.01, block_size=4):
    print(f"\n--- MONTE CARLO ({n_iterations} itérations) | Angle: {angle_reel}° | Bruit: {bruit} | Bloc: {block_size} ---")
    ber_sans_liste = []
    ber_avec_liste = []
    echecs_rs_avec = 0
    echecs_rs_sans = 0
    
    for i in range(n_iterations):
        masque = generer_masque_phase(128)
        ref = simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.0)
        bits_ref, masque_valide = extraire_bits_et_masque(ref, block_size=block_size)
        cle_ref = bits_ref[masque_valide][:96]
        
        lecture = simuler_lecture_laser(masque, angle=angle_reel, bruit_camera=bruit)
        
        # 1. Sans recalage
        bits_sans, _ = extraire_bits_et_masque(lecture, block_size=block_size)
        cle_sans = bits_sans[masque_valide][:96]
        ber_sans = distance_hamming(cle_ref, cle_sans)
        ber_sans_liste.append(ber_sans)
        
        # On vérifie si RS(12,6) aurait pu corriger
        octets_err_sans = sum(a != b for a, b in zip(np.packbits(cle_ref), np.packbits(cle_sans)))
        if octets_err_sans > 3:
            echecs_rs_sans += 1
            
        # 2. Avec recalage
        lecture_corrigee, _, _ = recaler_image(lecture, ref, plage_angle=6.0, pas=0.5)
        bits_avec, _ = extraire_bits_et_masque(lecture_corrigee, block_size=block_size)
        cle_avec = bits_avec[masque_valide][:96]
        ber_avec = distance_hamming(cle_ref, cle_avec)
        ber_avec_liste.append(ber_avec)
        
        octets_err_avec = sum(a != b for a, b in zip(np.packbits(cle_ref), np.packbits(cle_avec)))
        if octets_err_avec > 3:
            echecs_rs_avec += 1
            
    print(f"Sans recalage -> BER moyen: {np.mean(ber_sans_liste):.2f}% | Échecs RS(12,6): {echecs_rs_sans}/{n_iterations} ({echecs_rs_sans/n_iterations*100:.1f}%)")
    print(f"Avec recalage -> BER moyen: {np.mean(ber_avec_liste):.2f}% | Échecs RS(12,6): {echecs_rs_avec}/{n_iterations} ({echecs_rs_avec/n_iterations*100:.1f}%)")

if __name__ == "__main__":
    np.random.seed(42)
    test_monte_carlo_rotation(n_iterations=30, angle_reel=3.5, bruit=0.01, block_size=4)
