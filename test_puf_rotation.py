import warnings
import numpy as np

from scipy.ndimage import gaussian_filter, rotate

try:
    import reedsolo
except ImportError:
    raise ImportError(
        "Le module 'reedsolo' est requis.\n"
        "Installation : pip install reedsolo"
    )


# ============================================================
# CONFIGURATION RS
# ============================================================

RS_N = 12          # longueur totale
RS_K = 6           # données
RS_PARITE = 6      # 6 symboles de parité
RS_T = RS_PARITE // 2   # 3 erreurs de symboles corrigeables

RS = reedsolo.RSCodec(RS_PARITE)


# ============================================================
# 1. GÉNÉRATION DU MASQUE DE PHASE
# ============================================================

def generer_masque_phase(N=128, seed=None):
    """
    Génère un masque de phase aléatoire.

    La valeur retournée est un champ complexe de module 1.
    """
    rng = np.random.default_rng(seed)

    phase = rng.uniform(0, 2 * np.pi, (N, N))

    return np.exp(1j * phase)


# ============================================================
# 2. ENCODAGE REED-SOLOMON
# ============================================================

def encoder_rs(donnees):
    """
    Encode 6 octets avec RS(12,6).

    Entrée :
        donnees : 6 octets

    Sortie :
        mot RS de 12 octets
    """

    donnees = np.asarray(donnees, dtype=np.uint8)

    if donnees.size != RS_K:
        raise ValueError(
            f"RS(12,6) exige exactement {RS_K} octets de données."
        )

    mot = RS.encode(bytes(donnees))

    mot = np.frombuffer(mot, dtype=np.uint8)

    if len(mot) != RS_N:
        raise RuntimeError(
            f"Longueur RS inattendue : {len(mot)} au lieu de {RS_N}"
        )

    return mot


# ============================================================
# 3. DÉCODAGE REED-SOLOMON
# ============================================================

def decoder_rs(mot_recu):
    """
    Tente de corriger un mot RS(12,6).

    Retourne :
        donnees_corrigees
        succes
        mot_corrige
    """

    mot_recu = np.asarray(mot_recu, dtype=np.uint8)

    if mot_recu.size != RS_N:
        raise ValueError(
            f"Le décodeur RS(12,6) attend {RS_N} octets."
        )

    try:
        resultat = RS.decode(bytes(mot_recu))

        # reedsolo peut retourner directement les données
        # ou un tuple selon la version.
        if isinstance(resultat, tuple):
            donnees_corrigees = np.frombuffer(
                resultat[0],
                dtype=np.uint8
            )
        else:
            donnees_corrigees = np.frombuffer(
                resultat,
                dtype=np.uint8
            )

        # Reconstruction du mot corrigé pour vérification.
        mot_corrige = encoder_rs(donnees_corrigees)

        return donnees_corrigees, True, mot_corrige

    except reedsolo.ReedSolomonError:
        return None, False, None


# ============================================================
# 4. CONVERSION OCTETS → BITS
# ============================================================

def octets_vers_bits(octets):
    """
    12 octets -> 96 bits.
    """
    octets = np.asarray(octets, dtype=np.uint8)

    return np.unpackbits(octets)


# ============================================================
# 5. CONVERSION BITS → OCTETS
# ============================================================

def bits_vers_octets(bits):
    """
    96 bits -> 12 octets.
    """

    bits = np.asarray(bits, dtype=np.uint8)

    if len(bits) != RS_N * 8:
        raise ValueError(
            f"Il faut exactement {RS_N * 8} bits."
        )

    return np.packbits(bits)


# ============================================================
# 6. INSERTION DES BITS DANS LE MASQUE DE PHASE
# ============================================================

def encoder_bits_dans_masque(
    masque,
    bits,
    block_size=4
):
    """
    Encode les 96 bits dans des blocs de phase.

    bit = 0 -> phase locale inchangée
    bit = 1 -> inversion de phase de pi

    Les blocs sont placés au centre du masque.
    """

    masque = np.asarray(masque, dtype=np.complex128).copy()
    bits = np.asarray(bits, dtype=np.uint8)

    N = masque.shape[0]

    n_blocks = int(np.ceil(np.sqrt(len(bits))))

    hauteur = n_blocks * block_size
    largeur = n_blocks * block_size

    if hauteur > N or largeur > N:
        raise ValueError(
            "Le masque est trop petit pour encoder les bits."
        )

    y0 = (N - hauteur) // 2
    x0 = (N - largeur) // 2

    # Chaque bit reçoit un bloc.
    for i, bit in enumerate(bits):

        by = i // n_blocks
        bx = i % n_blocks

        ys = y0 + by * block_size
        xs = x0 + bx * block_size

        if bit:
            masque[
                ys:ys + block_size,
                xs:xs + block_size
            ] *= -1.0

    return masque


# ============================================================
# 7. LECTURE LASER
# ============================================================

def simuler_lecture_laser(
    masque,
    angle=0.0,
    bruit_camera=0.01
):
    """
    Simule :

        masque de phase
            ↓
        rotation
            ↓
        FFT
            ↓
        intensité
            ↓
        bruit caméra
    """

    if angle != 0.0:

        masque_rot = (
            rotate(
                np.real(masque),
                angle,
                reshape=False,
                order=3
            )
            +
            1j * rotate(
                np.imag(masque),
                angle,
                reshape=False,
                order=3
            )
        )

    else:
        masque_rot = masque

    champ = np.fft.fftshift(
        np.fft.fft2(masque_rot)
    )

    intensite = np.abs(champ) ** 2

    maximum = np.max(intensite)

    if maximum > 0:
        intensite /= maximum

    bruit = np.random.normal(
        0,
        bruit_camera,
        intensite.shape
    )

    return np.clip(
        intensite + bruit,
        0,
        1
    )


# ============================================================
# 8. RECALAGE ANGULAIRE
# ============================================================

def recaler_image(
    image_bruitee,
    image_ref,
    plage_angle=6.0,
    pas=0.5
):

    meilleur_angle = 0.0
    meilleure_corr = -1.0

    angles_test = np.arange(
        -plage_angle,
        plage_angle + pas / 2,
        pas
    )

    ref_flat = image_ref.flatten()

    ref_std = np.std(ref_flat)

    for angle in angles_test:

        img_rot = rotate(
            image_bruitee,
            angle,
            reshape=False,
            order=1
        )

        rot_flat = img_rot.flatten()

        std_rot = np.std(rot_flat)

        std_prod = ref_std * std_rot

        if std_prod > 0:

            corr = np.cov(
                rot_flat,
                ref_flat
            )[0, 1] / std_prod

            if corr > meilleure_corr:
                meilleure_corr = corr
                meilleur_angle = angle

    image_corrigee = rotate(
        image_bruitee,
        meilleur_angle,
        reshape=False,
        order=3
    )

    return (
        image_corrigee,
        meilleur_angle,
        meilleure_corr
    )


# ============================================================
# 9. EXTRACTION DES BITS
# ============================================================

def extraire_bits_et_masque(
    intensite,
    block_size=4
):

    intensite_floue = gaussian_filter(
        intensite,
        sigma=2.0
    )

    N = intensite.shape[0]

    if N % block_size != 0:
        raise ValueError(
            "N doit être divisible par block_size."
        )

    n_blocks = N // block_size

    blocs = intensite_floue.reshape(
        n_blocks,
        block_size,
        n_blocks,
        block_size
    )

    moyennes = blocs.mean(axis=(1, 3))

    # Différence horizontale.
    diff = (
        moyennes[:, :-1]
        -
        moyennes[:, 1:]
    )

    y, x = np.ogrid[
        :diff.shape[0],
        :diff.shape[1]
    ]

    centre_y = (
        diff.shape[0] - 1
    ) / 2

    centre_x = (
        diff.shape[1] - 1
    ) / 2

    rayon = (
        min(centre_y, centre_x)
        * 0.85
    )

    masque_cercle = (
        (x - centre_x) ** 2
        +
        (y - centre_y) ** 2
    ) <= rayon ** 2

    valeurs_valides = np.abs(
        diff[masque_cercle]
    )

    if valeurs_valides.size == 0:
        raise RuntimeError(
            "Aucune zone valide pour l'extraction."
        )

    seuil = np.median(
        valeurs_valides
    )

    masque_valide = (
        masque_cercle
        &
        (np.abs(diff) > seuil)
    )

    bits = (
        diff > 0
    ).astype(np.uint8)

    return (
        bits.flatten(),
        masque_valide.flatten()
    )


# ============================================================
# 10. EXTRACTION DES 96 BITS
# ============================================================

def extraire_96_bits(
    intensite,
    block_size=4
):

    bits, masque = extraire_bits_et_masque(
        intensite,
        block_size=block_size
    )

    bits_valides = bits[masque]

    if len(bits_valides) < RS_N * 8:
        raise RuntimeError(
            f"Extraction insuffisante : "
            f"{len(bits_valides)} bits disponibles, "
            f"{RS_N * 8} requis."
        )

    return bits_valides[:RS_N * 8]


# ============================================================
# 11. DISTANCE DE HAMMING
# ============================================================

def distance_hamming(b1, b2):

    b1 = np.asarray(b1)
    b2 = np.asarray(b2)

    if b1.shape != b2.shape:
        raise ValueError(
            "Les deux vecteurs doivent avoir "
            "la même longueur."
        )

    return np.mean(b1 != b2) * 100.0


# ============================================================
# 12. COMPARAISON DIRECTE DES OCTETS
# ============================================================

def compter_erreurs_symboles(
    reference,
    recu
):

    reference = np.asarray(
        reference,
        dtype=np.uint8
    )

    recu = np.asarray(
        recu,
        dtype=np.uint8
    )

    return int(
        np.sum(reference != recu)
    )


# ============================================================
# 13. TEST D'UN SEUL ESSAI
# ============================================================

def tester_une_iteration(
    angle_reel=3.5,
    bruit=0.01,
    block_size=4,
    seed=None
):

    rng = np.random.default_rng(seed)

    # --------------------------------------------------------
    # A. DONNÉES ORIGINALES
    # --------------------------------------------------------

    donnees = rng.integers(
        0,
        256,
        RS_K,
        dtype=np.uint8
    )

    # --------------------------------------------------------
    # B. ENCODAGE RS
    # --------------------------------------------------------

    mot_rs = encoder_rs(donnees)

    bits_rs = octets_vers_bits(
        mot_rs
    )

    # --------------------------------------------------------
    # C. MASQUE PORTEUR
    # --------------------------------------------------------

    masque_base = generer_masque_phase(
        128,
        seed=seed
    )

    # --------------------------------------------------------
    # D. INSERTION DU MOT RS
    # --------------------------------------------------------

    masque = encoder_bits_dans_masque(
        masque_base,
        bits_rs,
        block_size=block_size
    )

    # --------------------------------------------------------
    # E. LECTURE DE RÉFÉRENCE
    # --------------------------------------------------------

    ref = simuler_lecture_laser(
        masque,
        angle=0.0,
        bruit_camera=0.0
    )

    bits_ref = extraire_96_bits(
        ref,
        block_size=block_size
    )

    mot_ref = bits_vers_octets(
        bits_ref
    )

    # --------------------------------------------------------
    # F. LECTURE ROTÉE + BRUITÉE
    # --------------------------------------------------------

    lecture = simuler_lecture_laser(
        masque,
        angle=angle_reel,
        bruit_camera=bruit
    )

    # ========================================================
    # CAS 1 : SANS RECALAGE
    # ========================================================

    bits_sans = extraire_96_bits(
        lecture,
        block_size=block_size
    )

    mot_sans = bits_vers_octets(
        bits_sans
    )

    erreurs_sans = compter_erreurs_symboles(
        mot_ref,
        mot_sans
    )

    ber_sans = distance_hamming(
        bits_ref,
        bits_sans
    )

    donnees_sans, succes_sans, _ = decoder_rs(
        mot_sans
    )

    # ========================================================
    # CAS 2 : AVEC RECALAGE
    # ========================================================

    lecture_corrigee, angle_estime, correlation = (
        recaler_image(
            lecture,
            ref,
            plage_angle=6.0,
            pas=0.5
        )
    )

    bits_avec = extraire_96_bits(
        lecture_corrigee,
        block_size=block_size
    )

    mot_avec = bits_vers_octets(
        bits_avec
    )

    erreurs_avec = compter_erreurs_symboles(
        mot_ref,
        mot_avec
    )

    ber_avec = distance_hamming(
        bits_ref,
        bits_avec
    )

    donnees_avec, succes_avec, _ = decoder_rs(
        mot_avec
    )

    # --------------------------------------------------------
    # VÉRIFICATION FINALE
    # --------------------------------------------------------

    donnees_ok_sans = (
        succes_sans
        and np.array_equal(
            donnees_sans,
            donnees
        )
    )

    donnees_ok_avec = (
        succes_avec
        and np.array_equal(
            donnees_avec,
            donnees
        )
    )

    return {
        "ber_sans": ber_sans,
        "ber_avec": ber_avec,

        "erreurs_symboles_sans":
            erreurs_sans,

        "erreurs_symboles_avec":
            erreurs_avec,

        "rs_succes_sans":
            succes_sans,

        "rs_succes_avec":
            succes_avec,

        "donnees_correctes_sans":
            donnees_ok_sans,

        "donnees_correctes_avec":
            donnees_ok_avec,

        "angle_estime":
            angle_estime,

        "correlation":
            correlation,

        "donnees_originales":
            donnees,

        "mot_rs":
            mot_rs,

        "mot_ref":
            mot_ref,

        "mot_sans":
            mot_sans,

        "mot_avec":
            mot_avec
    }


# ============================================================
# 14. MONTE CARLO
# ============================================================

def test_monte_carlo_rotation(
    n_iterations=50,
    angle_reel=3.5,
    bruit=0.01,
    block_size=4
):

    print()
    print("=" * 70)
    print(
        "MONTE CARLO — TRANSMISSION OPTIQUE + RS(12,6)"
    )
    print("=" * 70)

    print(
        f"Itérations : {n_iterations}"
    )

    print(
        f"Angle réel  : {angle_reel}°"
    )

    print(
        f"Bruit       : {bruit}"
    )

    print(
        f"Bloc        : {block_size}"
    )

    print(
        f"RS          : ({RS_N},{RS_K})"
    )

    print(
        f"Correction  : {RS_T} erreurs symboles maximum"
    )

    print("=" * 70)

    ber_sans = []
    ber_avec = []

    erreurs_sans = []
    erreurs_avec = []

    rs_succes_sans = 0
    rs_succes_avec = 0

    donnees_ok_sans = 0
    donnees_ok_avec = 0

    angles_estimes = []
    correlations = []

    for i in range(n_iterations):

        resultat = tester_une_iteration(
            angle_reel=angle_reel,
            bruit=bruit,
            block_size=block_size,
            seed=42 + i
        )

        ber_sans.append(
            resultat["ber_sans"]
        )

        ber_avec.append(
            resultat["ber_avec"]
        )

        erreurs_sans.append(
            resultat[
                "erreurs_symboles_sans"
            ]
        )

        erreurs_avec.append(
            resultat[
                "erreurs_symboles_avec"
            ]
        )

        if resultat["rs_succes_sans"]:
            rs_succes_sans += 1

        if resultat["rs_succes_avec"]:
            rs_succes_avec += 1

        if resultat[
            "donnees_correctes_sans"
        ]:
            donnees_ok_sans += 1

        if resultat[
            "donnees_correctes_avec"
        ]:
            donnees_ok_avec += 1

        angles_estimes.append(
            resultat["angle_estime"]
        )

        correlations.append(
            resultat["correlation"]
        )

    # ========================================================
    # RÉSULTATS
    # ========================================================

    print()
    print("----- SANS RECALAGE -----")

    print(
        f"BER moyen              : "
        f"{np.mean(ber_sans):.2f}%"
    )

    print(
        f"Erreurs RS moyennes    : "
        f"{np.mean(erreurs_sans):.2f} / {RS_N}"
    )

    print(
        f"Succès décodage RS     : "
        f"{rs_succes_sans}/{n_iterations} "
        f"({100 * rs_succes_sans / n_iterations:.1f}%)"
    )

    print(
        f"Données récupérées     : "
        f"{donnees_ok_sans}/{n_iterations} "
        f"({100 * donnees_ok_sans / n_iterations:.1f}%)"
    )

    print()
    print("----- AVEC RECALAGE -----")

    print(
        f"BER moyen              : "
        f"{np.mean(ber_avec):.2f}%"
    )

    print(
        f"Erreurs RS moyennes    : "
        f"{np.mean(erreurs_avec):.2f} / {RS_N}"
    )

    print(
        f"Succès décodage RS     : "
        f"{rs_succes_avec}/{n_iterations} "
        f"({100 * rs_succes_avec / n_iterations:.1f}%)"
    )

    print(
        f"Données récupérées     : "
        f"{donnees_ok_avec}/{n_iterations} "
        f"({100 * donnees_ok_avec / n_iterations:.1f}%)"
    )

    print()
    print("----- RECALAGE -----")

    print(
        f"Angle estimé moyen     : "
        f"{np.mean(angles_estimes):.2f}°"
    )

    print(
        f"Erreur angle moyenne   : "
        f"{np.mean(np.abs("
        f"np.asarray(angles_estimes)"
        f" - angle_reel"
        f")):.2f}°"
    )

    print(
        f"Corrélation moyenne    : "
        f"{np.mean(correlations):.4f}"
    )

    print()
    print("=" * 70)

    return {
        "ber_sans": ber_sans,
        "ber_avec": ber_avec,
        "erreurs_sans": erreurs_sans,
        "erreurs_avec": erreurs_avec,
        "rs_succes_sans": rs_succes_sans,
        "rs_succes_avec": rs_succes_avec,
        "donnees_ok_sans": donnees_ok_sans,
        "donnees_ok_avec": donnees_ok_avec,
        "angles_estimes": angles_estimes,
        "correlations": correlations
    }


# ============================================================
# 15. TEST DIRECT DU CODE RS
# ============================================================

def test_rs_pur():

    print()
    print("=" * 70)
    print("TEST PUR REED-SOLOMON RS(12,6)")
    print("=" * 70)

    donnees = np.array(
        [10, 20, 30, 40, 50, 60],
        dtype=np.uint8
    )

    mot = encoder_rs(
        donnees
    )

    print(
        f"Données       : {donnees}"
    )

    print(
        f"Mot RS        : {mot}"
    )

    # --------------------------------------------------------
    # 0 erreur
    # --------------------------------------------------------

    recu = mot.copy()

    decoded, succes, _ = decoder_rs(
        recu
    )

    print()
    print(
        f"0 erreur      : "
        f"{'OK' if succes else 'ÉCHEC'}"
    )

    # --------------------------------------------------------
    # 3 erreurs
    # --------------------------------------------------------

    recu = mot.copy()

    recu[1] ^= 0x55
    recu[5] ^= 0xAA
    recu[9] ^= 0x33

    decoded, succes, _ = decoder_rs(
        recu
    )

    print(
        f"3 erreurs     : "
        f"{'CORRIGÉ' if succes else 'ÉCHEC'}"
    )

    if succes:
        print(
            f"Données       : {decoded}"
        )

        print(
            f"Identiques    : "
            f"{np.array_equal(decoded, donnees)}"
        )

    # --------------------------------------------------------
    # 4 erreurs
    # --------------------------------------------------------

    recu = mot.copy()

    recu[0] ^= 0x11
    recu[2] ^= 0x22
    recu[6] ^= 0x33
    recu[10] ^= 0x44

    decoded, succes, _ = decoder_rs(
        recu
    )

    print(
        f"4 erreurs     : "
        f"{'CORRIGÉ (inattendu)' if succes else 'ÉCHEC attendu'}"
    )

    print("=" * 70)


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    np.random.seed(42)

    # Vérification indépendante du RS
    test_rs_pur()

    # Test physique/simulation
    test_monte_carlo_rotation(
        n_iterations=30,
        angle_reel=3.5,
        bruit=0.01,
        block_size=4
    )
