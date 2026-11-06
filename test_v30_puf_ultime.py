import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import rotate

def generer_masque_phase(N=128):
    """Simule un diffuseur (verre depoli) : des phases 100% aleatoires."""
    # Chaque pixel est un defaut microscopique avec une phase aleatoire
    phase = np.random.uniform(0, 2*np.pi, (N, N))
    return np.exp(1j * phase) # Champ complexe

def simuler_lecture_laser(masque, rotation_angle=0.0, bruit_camera=0.01):
    """Simule la diffraction d'un laser a travers le diffuseur."""
    if rotation_angle != 0:
        # La rotation du materiau decale le motif de diffraction
        masque_rot = rotate(np.real(masque), rotation_angle, reshape=False) + \
                     1j * rotate(np.imag(masque), rotation_angle, reshape=False)
    else:
        masque_rot = masque
        
    # Diffraction
    champ = np.fft.fftshift(np.fft.fft2(masque_rot))
    intensite = np.abs(champ)**2
    
    # Normalisation (0 a 1)
    intensite = intensite / np.max(intensite)
    
    # Bruit de camera
    intensite_bruitee = intensite + np.random.normal(0, bruit_camera, intensite.shape)
    return np.clip(intensite_bruitee, 0, 1)

def extraire_cle_robuste(intensite, seuil=0.05):
    """Extrait des bits uniquement sur les zones lumineuses."""
    # On compare un pixel avec son voisin de droite, 
    # MAIS uniquement si le pixel est assez lumineux (au-dessus du seuil)
    
    # Masque des zones lumineuses
    masque_valide = intensite[:, :-1] > seuil
    
    # Comparaison
    bits = (intensite[:, :-1] > intensite[:, 1:]).astype(int)
    
    # On ne garde que les bits des zones valides
    return bits[masque_valide]

def distance_hamming(cle1, cle2):
    # On s'assure d'avoir la meme longueur (au cas ou le masque change)
    n = min(len(cle1), len(cle2))
    return np.mean(cle1[:n] != cle2[:n]) * 100

def main():
    print("=== V30: SIMULATEUR PUF OPTIQUE DE NIVEAU INDUSTRIEL ===")
    
    N = 128
    np.random.seed(42)
    
    # 1. Creation des deux materiaux
    masque_A = generer_masque_phase(N)
    masque_B = generer_masque_phase(N)
    
    # 2. Reference
    intensite_ref = simuler_lecture_laser(masque_A, bruit_camera=0.0)
    cle_ref = extraire_cle_robuste(intensite_ref)
    print(f"Taille de la cle stable : {len(cle_ref)} bits")
    
    # 3. Test Unicite (Materiau A vs B)
    intensite_B = simuler_lecture_laser(masque_B, bruit_camera=0.0)
    cle_B = extraire_cle_robuste(intensite_B)
    err_unicite = distance_hamming(cle_ref, cle_B)
    print(f"\n[UNICITE] Materiau A vs B : {err_unicite:.2f}% (doit etre ~50%)")
    
    # 4. Test Bruit Camera (Materiau A vs A bruite)
    print("\n[ROBUSTESSE] Test au bruit de camera :")
    for b in [0.01, 0.05, 0.1, 0.2]:
        intensite_bruitee = simuler_lecture_laser(masque_A, bruit_camera=b)
        cle_bruitee = extraire_cle_robuste(intensite_bruitee)
        err = distance_hamming(cle_ref, cle_bruitee)
        print(f"  Bruit = {b:.2f} | Taux d'erreur = {err:.2f}%")
        
    # 5. Test Rotation (Defaut d'alignement)
    print("\n[POSITIONNEMENT] Test a la rotation :")
    for angle in [0.5, 1.0, 2.0, 5.0]:
        intensite_rot = simuler_lecture_laser(masque_A, rotation_angle=angle, bruit_camera=0.01)
        cle_rot = extraire_cle_robuste(intensite_rot)
        err = distance_hamming(cle_ref, cle_rot)
        print(f"  Angle = {angle:.1f} deg | Taux d'erreur = {err:.2f}%")

    # Affichage
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title("Motif de diffraction (Reference)")
    plt.imshow(intensite_ref, cmap='inferno')
    plt.subplot(1, 2, 2)
    plt.title("Motif d'un autre materiau (B)")
    plt.imshow(intensite_B, cmap='inferno')
    plt.show()

if __name__ == "__main__":
    main()
