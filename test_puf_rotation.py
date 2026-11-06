import numpy as np
from scipy.ndimage import gaussian_filter, rotate

def generer_masque_phase(N=128):
    return np.exp(1j * np.random.uniform(0, 2*np.pi, (N, N)))

def simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.01):
    if angle != 0.0:
        masque_rot = rotate(np.real(masque), angle, reshape=False) + 1j * rotate(np.imag(masque), angle, reshape=False)
    else:
        masque_rot = masque
    champ = np.fft.fftshift(np.fft.fft2(masque_rot))
    intensite = np.abs(champ)**2
    intensite = intensite / np.max(intensite)
    intensite_bruitee = intensite + np.random.normal(0, bruit_camera, intensite.shape)
    return np.clip(intensite_bruitee, 0, 1)

def extraire_bits_et_indices(intensite, block_size=8, seuil=0.05):
    """Extrait les bits ET garde seulement ceux qui sont fiables (zone de garde) et au centre."""
    intensite_floue = gaussian_filter(intensite, sigma=2.0)
    N = intensite.shape[0]
    n_blocks = N // block_size
    blocs = intensite_floue.reshape(n_blocks, block_size, n_blocks, block_size)
    moyennes = blocs.mean(axis=(1, 3))
    
    # 1. Calcul des différences entre blocs voisins
    diff = moyennes[:, :-1] - moyennes[:, 1:]
    
    # 2. Masque circulaire (on ignore les bords de l'image)
    y, x = np.ogrid[:n_blocks, :n_blocks - 1]
    centre = (n_blocks - 1) / 2
    masque_cercle = ((x - centre)**2 + (y - centre)**2) <= (centre * 0.85)**2
    
    # 3. Zone de garde (on ignore les bits instables où la différence est trop faible)
    masque_garde = np.abs(diff) > seuil
    
    # On combine les deux masques
    masque_valide = masque_cercle & masque_garde
    
    bits = (diff > 0).astype(np.uint8)
    return bits, masque_valide

def distance_hamming(cle1, cle2):
    n = min(len(cle1), len(cle2))
    return np.mean(cle1[:n] != cle2[:n]) * 100

def main():
    print("=== TEST FINAL : MASQUE CIRCULAIRE + ZONE DE GARDE ===")
    np.random.seed(42)
    masque = generer_masque_phase(128)
    
    # Enrôlement (Référence)
    ref = simuler_lecture_laser(masque, angle=0.0, bruit_camera=0.0)
    bits_ref_full, masque_valide = extraire_bits_et_indices(ref)
    
    # On ne garde que les bits fiables pour la clé de référence
    cle_ref = bits_ref_full[masque_valide]
    print(f"Taille de la clé stable : {len(cle_ref)} bits (sur {bits_ref_full.size})")
    
    # Test avec défaut
    bruitee = simuler_lecture_laser(masque, angle=3.5, bruit_camera=0.01)
    
    # Sans recalage
    bits_sans, _ = extraire_bits_et_indices(bruitee)
    cle_sans = bits_sans[masque_valide] # on applique le même masque
    print(f"Erreur SANS recalage : {distance_hamming(cle_ref, cle_sans):.2f}%")
    
    # Avec recalage
    meilleur_angle, meilleure_corr = 0.0, -1.0
    for a in np.arange(-6.0, 6.1, 0.5):
        img = rotate(bruitee, a, reshape=False)
        corr = np.corrcoef(img.flatten(), ref.flatten())[0, 1]
        if corr > meilleure_corr:
            meilleure_corr = corr
            meilleur_angle = a
            
    corrigee = rotate(bruitee, meilleur_angle, reshape=False)
    bits_avec, _ = extraire_bits_et_indices(corrigee)
    cle_avec = bits_avec[masque_valide]
    
    print(f"Angle trouve : {meilleur_angle} deg (Corr: {meilleure_corr:.3f})")
    print(f"Erreur AVEC recalage  : {distance_hamming(cle_ref, cle_avec):.2f}%")

if __name__ == "__main__":
    main()
