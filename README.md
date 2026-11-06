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
- Température : bruit ajouté à la dynamique ; [À COMPLÉTER : forme exacte du bruit et unités de T].

## Résultats (simulation)

**1. Courbe I-V.** Le décrochage dépend de `f` (voir `courbe_iv_v16.png`). Le seuil dépend aussi de N : à f = 0.25, ≈ 0.22 pour N = 32 contre ≈ 0.32–0.36 pour N = 16. Le seuil n'est donc pas convergé. Le trait rouge de la figure est un seuil arbitraire.

**2. Séparation des niveaux (N = 32, 20 graines par f).** Intervalles « moyenne ± 3σ/√n » à deux biais de lecture (0.30 et 0.36) :
- Les moyennes de 8 classes sont séparées. f = 0.05 et f = 0.10 ne le sont pas (V = 0 à 0.30), elles forment une seule classe.
- Cela concerne la différence entre **moyennes sur 20 réseaux**, pas une lecture unique. En lecture unique, l'écart entre niveaux voisins est de ≈ 2 à 3,6 σ (σ ≈ 0.03–0.045 par graine) : erreur de classement estimée de ≈ 5 à 18 % par côté entre voisins, d'après les valeurs affichées.
- La métrique ρ (médiane des distances relatives) n'est pas une mesure fiable de séparation : pour des valeurs proches de 0 elle vaut ≈ 1 même lorsque les niveaux sont très éloignés.

**3. Température.** Avec un bruit de Langevin, la tension dérive de façon systématique (de l'ordre de +0.07 à +0.12 à T = 0.05 en unités du modèle). Cette dérive est comparable à l'écart entre niveaux voisins. Un lecteur calibré à T = 0 se trompe donc d'environ un niveau. Un classement par ratio V(0.36)/V(0.30) n'annule pas cette dérive (les ratios convergent vers ≈ 1.38).

**4. Scanner multi-biais (V27).** Résultat rapporté : erreur de 43,3 % (1D naïf) → 3,3 % (4 biais, vote Mahalanobis / KL-NLL). **Non reproduit indépendamment.** À documenter avant d'interpréter : nombre de lectures (3,3 % = 1/30 ou 2/60 : intervalle de confiance très large), niveaux testés, température de calibration, séparation stricte entre graines de calibration et de test.

## Limites connues
- Simulation déterministe : seul le bruit initial (σ = 0.01) varie entre graines, plus le bruit thermique ajouté.
- N = 16 et 32 seulement ; dépendance en N non explorée au-delà.
- Pas de désordre, de défauts, ni de bruit de mesure.
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
```
[À COMPLÉTER : versions de Python et NumPy, durée approximative, graines utilisées.]

## Structure du dépôt
```text
README.md
RAPPORT_PHASE_1.md
requirements.txt
moteur_fluxons_2d.py            # moteur (bords ouverts, force corrigée)
plot_iv.py
test_v16_precision.py           # courbes I-V
test_v16c_matrice_confusion.py  # [à ajouter] matrice de séparation
test_v18_rho_tension.py         # métrique ρ (voir limites)
test_v19_temperature.py         # [à ajouter] effet de T
test_v21_cartographie_temp.py
test_v23_scanner_mahalanobis.py
test_v27_scanner_4d.py          # résultat rapporté, non reproduit
```

## Références
- Tinkham, M., *Introduction to Superconductivity*, 2ᵉ éd., McGraw-Hill, 1996.
- Teitel, S. & Jayaprakash, C., Phys. Rev. B 27, 598 (1983) : contexte sur les modèles XY frustrés (ne fournit pas les résultats ci-dessus).
