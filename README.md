# Code-barres topologique : simulation d'un réseau de jonctions Josephson frustré

**Statut : exploratoire. Résultats de simulation uniquement.**
Aucun matériau réel n'a été mesuré ni modélisé. Le lien entre la frustration `f` du modèle et une microstructure physique reste une hypothèse non testée.

## Idée testée
Un réseau 2D de phases couplées, soumis à un champ transverse (frustration `f`), répond à un courant de lecture par une tension qui dépend de `f`. On teste si cette réponse peut servir de signature lisible (alphabet de niveaux de `f`).

## Modèle (résumé)
- Grille N×N de phases φ, dynamique du second ordre amortie (γ = 0.1, dt = 0.05, intégrateur de type vitesse-Verlet).
- Jauge de Landau : A_x = −f·i. Bords **ouverts** (aucun `np.roll`).
- Biais DC injecté colonne 0, extrait colonne N−1.
- Observable : V = |⟨v(col N−1) − v(col 0)⟩|, différence de vitesse de phase en **unités du modèle** (pas des volts).
- Apparenté à une équation RCSJ (Tinkham, *Introduction to Superconductivity*, 2ᵉ éd., 1996). La correspondance exacte n'est pas établie : `beta_c` est défini dans le code mais non utilisé.
- Température : bruit de Langevin ajouté à la dynamique. [À VÉRIFIER : la formule exacte dans le moteur. Un bruit par pas sur la vitesse s'écrit √(2γT·dt)·ξ ; √(2γT/dt) vaut pour un bruit sur la force, avant multiplication par dt.]

## Résultats (simulation)
## 🚀 Phase 3 : Pivot vers le Code-Barres Optique (PUF)

Suite aux échecs de robustesse thermique du modèle RCSJ (voir Phase 2), le projet a pivoté vers un modèle de **Fonction Physique Inclonable (PUF) optique**. 

### Principe
Un laser traverse un polymère chargé de particules aléatoires. La diffraction (Speckle Pattern) est capturée par une caméra et transformée en clé binaire.

### Résultats
*   **Extraction de clé** : Un algorithme de filtrage spatial (Block Averaging) extrait une clé binaire de 128 bits à partir du motif de diffraction.
*   **Correction d'erreur** : L'ajout d'un Fuzzy Extractor (Reed-Solomon) permet de corriger les erreurs dues au bruit de la caméra.
*   **Validation** : À un niveau de bruit de caméra de 0.01, la PUF brute a un taux d'erreur de 2.43%. Le Fuzzy Extractor parvient à **reconstruire la clé secrète à 100%** (0.00% d'erreur), validant le concept d'authentification physique infalsifiable.

Fichier de test : `test_v33_vrai_fuzzy.py`

**1. Courbe I-V.** Le décrochage dépend de `f` (voir `courbe_iv_v16.png`). Le seuil dépend aussi de N : à f = 0.25, ≈ 0.22 pour N = 32 contre ≈ 0.32–0.36 pour N = 16. Le seuil n'est donc pas convergé. Le trait rouge de la figure est un seuil arbitraire.

**2. Séparation des niveaux (N = 32, 20 graines par f).** Intervalles « moyenne ± 3σ/√n » à deux biais de lecture (0.30 et 0.36) :
- Les moyennes de 8 classes sont séparées. f = 0.05 et f = 0.10 ne le sont pas (V = 0 à 0.30), elles forment une seule classe.
- Cela concerne la différence entre **moyennes sur 20 réseaux**, pas une lecture unique. En lecture unique, l'écart entre niveaux voisins est de ≈ 2 à 3,6 σ (σ ≈ 0.03–0.045 par graine) : erreur de classement estimée de ≈ 5 à 18 % par côté entre voisins.
- La métrique ρ (médiane des distances relatives) n'est pas une mesure fiable de séparation : pour des valeurs proches de 0 elle vaut ≈ 1 même lorsque les niveaux sont très éloignés.

**3. Température.** Avec un bruit de Langevin, la tension dérive de façon systématique (de l'ordre de +0.07 à +0.12 à T = 0.05 en unités du modèle). Cette dérive est comparable à l'écart entre niveaux voisins. Un lecteur calibré à T = 0 se trompe donc d'environ un niveau. Un classement par ratio V(0.36)/V(0.30) n'annule pas cette dérive (les ratios convergent vers ≈ 1.38).

**4. Scanner multi-biais (V27).**
Protocole du script : 3 niveaux (f = 0.25, 0.30, 0.35), 4 biais (0.24, 0.30, 0.36, 0.42), T = 0.05, 15 graines de calibration par niveau (graines 1000+), lectures de test avec graines séparées (3000+). **La calibration et le test sont faits à la même température** : ce test ne mesure donc pas la dérive thermique.

| Source | Méthode | Erreur | IC95 |
|---|---|---|---|
| Exécution rapportée (45 lectures) | MahaDiag | 8,9 % (4/45) | 3,5–20,7 % |
| Exécution rapportée (45 lectures) | Vote (conflit = erreur) | 17,8 % (8/45) | 9,3–31,3 % |
| Reproduction indépendante (45 lectures) | Maha / MahaDiag / MahaShrink / KL_NLL / vote | 17,8 / 20,0 / 22,2 / 13,3 / 15,6 % | larges |
| Reproduction indépendante (120 lectures) | MahaDiag | 15,8 % | 10,4–23,4 % |
| Reproduction indépendante (120 lectures) | KL_NLL | 17,5 % | 11,7–25,3 % |
| Reproduction indépendante (120 lectures) | Vote (conflit = erreur) | 19,2 % | 13,1–27,1 % |
| Reproduction indépendante (120 lectures) | Vote + départage MahaDiag | 15,0 % | — |

Lecture :
- Les intervalles de confiance se chevauchent : le classement entre MahaDiag, KL_NLL et le vote n'est pas établi.
- Les égalités (conflits) sont comptées comme des erreurs par le script. Dans l'exécution rapportée, 5 des 8 erreurs du vote seraient des conflits, ce qui ne laisse que 3 erreurs franches (6,7 %).
- Le biais 0.42 est peu informatif dans la reproduction : moyennes ≈ 1.10 / 1.09 / 1.17 avec σ de 0.2 à 0.3. Avec une covariance commune, 3 biais donnent 16,7 % contre 17,5 % pour 4 biais ; un seul biais (0.30) donne 21,7 %.
- La reproduction indépendante utilise ma propre implémentation du bruit de Langevin : l'écart avec 8,9 % peut venir de la manière dont T est appliquée.
- Un résultat antérieur rapporté (43,3 % → 3,3 %) n'est pas reproduit et n'est plus retenu.

Pistes non encore testées : calibration à une température différente de celle du test, covariance commune aux classes, 50 graines de calibration, 500 pas de mesure (dans un test à 12 graines, σ entre graines baisse de ≈ 30 à 40 % entre 150 et 500 pas, mais ne tombe pas à zéro), au moins 120 lectures de test avec intervalle de confiance affiché.

## Limites connues
- Simulation déterministe : seul le bruit initial (σ = 0.01) varie entre graines, plus le bruit thermique ajouté.
- N = 16 et 32 seulement ; dépendance en N non explorée au-delà.
- Pas de désordre, de défauts, ni de bruit de mesure.
- Peu de niveaux testés dans le scanner (3), et peu de lectures de test.
- Résistance à la contrefaçon : non étudiée.
- Lien avec un matériau réel : non établi.

## Historique de corrections du moteur (à lire avant d'utiliser d'anciens résultats)
Les versions initiales avaient : force de signe inversé (la dynamique montait en énergie), `A_x` de mauvaise forme, bords périodiques (`np.roll`) court-circuitant le biais, énergie définie sur les sites. Les résultats antérieurs à la version à bords ouverts et force corrigée ne sont pas valables.

## Reproduire
```bash
pip install -r requirements.txt
python test_v16_precision.py          # courbes I-V
python test_v16c_matrice_confusion.py # séparation des moyennes, 20 graines
python test_v19_temperature.py        # effet de T
python test_v27_scanner_4d.py         # scanner 4 biais (calibration et test à la même T)
```
[À COMPLÉTER : versions de Python et NumPy, durée approximative, graines utilisées.]

## Structure du dépôt
```text
README.md
RAPPORT_PHASE_1.md
requirements.txt
moteur_fluxons_2d.py            # moteur (bords ouverts, force corrigée, bruit de Langevin)
plot_iv.py
test_v16_precision.py           # courbes I-V
test_v16c_matrice_confusion.py  # séparation des moyennes
test_v18_rho_tension.py         # métrique ρ (voir limites)
test_v19_temperature.py         # effet de T
test_v21_cartographie_temp.py
test_v23_scanner_mahalanobis.py
test_v27_scanner_4d.py          # scanner 4 biais, voir section 4
```

## Références
- Tinkham, M., *Introduction to Superconductivity*, 2ᵉ éd., McGraw-Hill, 1996.
- Teitel, S. & Jayaprakash, C., Phys. Rev. B 27, 598 (1983) : contexte sur les modèles XY frustrés (ne fournit pas les résultats ci-dessus).
