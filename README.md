Code-Barres Topologique : Étude Numérique Exploratoire

Statut : Simulation numérique uniquement — aucune validation expérimentale.
Domaines : Physique de la matière condensée · Photonique · PUF · Cryptographie physique.

---

📌 1. Présentation et Objectif

Ce projet explore la possibilité de construire une signature physique difficile à reproduire, comparable dans sa fonction à un code-barres, mais dont l'information serait portée par la structure physique d'un matériau plutôt que par une encre ou un motif visuel.

La question fondamentale étudiée est :

«« Une microstructure physique peut-elle produire une réponse mesurable suffisamment stable, distinctive et difficile à reproduire pour constituer une identité physique ? »»

Trois architectures ont été explorées numériquement afin d'identifier la piste la plus viable avant toute fabrication matérielle.

---

🔬 2. Les Trois Architectures Explorées

Architecture 1 : Réseau RCSJ — Jonctions Josephson

* Principe : Réseau 2D de phases couplées soumis à une frustration magnétique, avec jauge de Landau et bords ouverts.
* Résultat principal : Le modèle reproduit une relation entre la frustration "f" et la réponse dynamique du réseau, notamment sur les courbes I–V.
* Limites : La séparation entre niveaux voisins reste insuffisante pour une lecture unique, avec une erreur estimée d'environ 5 à 18 % par côté selon les conditions. La température introduit également une dérive comparable à l'écart entre certains niveaux.
* Verdict : Modèle physique intéressant, mais signature non suffisamment robuste en lecture unique dans les conditions étudiées.

---

Architecture 2 : PUF Optique — Speckle

* Principe : Diffraction d'un champ optique sur un masque de phase aléatoire, production d'un motif de speckle, extraction de bits et correction d'erreurs par Reed–Solomon.
* Résultat principal : Très bonne diversité inter-puces simulée, avec une distance moyenne d'environ 49,97 % entre 300 puces.
* Résultat complémentaire : Avec recalage, le BER simulé descend jusqu'à 3,4 % à 3,5° de rotation dans une condition donnée.
* Limites : Le recalage actuel utilise l'image de référence d'enrôlement et n'est donc pas encore déployable tel quel. À un bruit de "0.05", environ 12,8 % des reconstructions échouent. L'entropie résiduelle estimée de la preuve de concept est seulement de l'ordre de 36–40 bits.
* Verdict : Architecture prometteuse pour une étude expérimentale, mais PUF physique non démontrée.

---

Architecture 3 : Code-Barres Spectral — Résonances

🌟 PISTE RETENUE POUR LA SUITE

* Principe : Au lieu d'utiliser un motif spatial sensible à l'orientation, l'information est encodée dans 96 canaux de fréquences de résonance. La lecture exploite un filtre adapté (Matched Filter) afin de détecter les signatures malgré le bruit et une dérive fréquentielle.
* Résultats rapportés : Une expérience Monte Carlo de 100 simulations rapporte 100/100 reconstructions réussies, avec une erreur moyenne annoncée d'environ 1 bit sur 96 avant correction Reed–Solomon.
* Statut de ces résultats : Ces scripts n'ont pas encore été relus et reproduits indépendamment. Le résultat "100/100" est donc conservé comme résultat rapporté, et non comme validation indépendante.
* Limites : L'invariance à la rotation reste à vérifier expérimentalement. Les paramètres physiques des résonances, l'entropie, la résistance au clonage et le lien avec une microstructure réelle ne sont pas encore établis.
* Verdict : La représentation spectrale est retenue comme piste prioritaire pour la suite du projet.

---

📊 3. Tableau Comparatif

Critère| Josephson| PUF Optique| Spectrale
Simulation| ✓| ✓| ✓
Reproduction indépendante| ✓| ✓| À faire
Désordre physique| Non| Simulé| À établir
Lecture unique robuste| Faible| Limitée| À déterminer
Sensibilité thermique| Forte| Modérée| À déterminer
Sensibilité à la rotation| Faible| Forte| Potentiellement faible
Correction Reed–Solomon| Non| ✓| ✓
Matériau réel| ✗| ✗| ✗
Résistance au clonage| Non étudiée| Non étudiée| Non étudiée

---

🏁 4. Décision de Recherche

À l'issue de cette phase numérique, l'architecture spectrale est retenue comme piste prioritaire.

Cette décision constitue une orientation de recherche, et non la démonstration que la technologie est déjà validée.

L'hypothèse de travail est qu'une signature fréquentielle pourrait offrir un compromis intéressant entre :

- stabilité de lecture ;
- tolérance au bruit ;
- tolérance à la dérive ;
- faible dépendance à l'orientation ;
- extraction numérique ;
- correction d'erreurs.

---

🔭 5. Prochaines Étapes — Phase 2

Avant toute fabrication ou validation expérimentale :

1. Reproduire indépendamment les simulations spectrales Monte Carlo.
2. Documenter précisément les unités, amplitudes, largeurs et espacements des résonances.
3. Augmenter le nombre d'essais et établir des intervalles de confiance robustes.
4. Tester la stabilité en fonction du bruit, de la température et des paramètres de lecture.
5. Quantifier l'entropie de la signature réellement exploitable.
6. Définir un modèle d'attaque : mesure, prédiction, imitation et clonage.
7. Vérifier que les fréquences observées proviennent d'une structure physique non triviale, plutôt que d'une information imposée artificiellement par le concepteur.

---

⚙️ 6. Reproduction et Dépendances

Environnement de référence : Python 3.11 · NumPy · SciPy · "reedsolo"

# Installation
pip install -r requirements.txt
pip install reedsolo

# Architecture 1 — Josephson
python test_v16_precision.py
python test_v27_scanner_4d.py

# Architecture 2 — PUF optique
python test_v33_vrai_fuzzy.py
python test_puf_rotation.py

# Architecture 3 — Spectrale
python test_resonance_spectrale.py
python test_monte_carlo_spectral.py

---

📂 7. Structure du Projet

README.md
RAPPORT_PHASE_1.md
requirements.txt

moteur_fluxons_2d.py

test_v16_precision.py
test_v27_scanner_4d.py

test_v33_vrai_fuzzy.py
test_puf_rotation.py

test_resonance_spectrale.py
test_monte_carlo_spectral.py

---

🧭 8. Statut du Projet

PHASE 1
Étude numérique
      │
      ├── Josephson ───────► limites identifiées
      │
      ├── PUF optique ─────► piste expérimentale possible
      │
      └── Spectrale ────────► ★ piste prioritaire
                                  │
                                  ▼
                              PHASE 2
                         validation numérique
                              approfondie
                                  │
                                  ▼
                         conception matérielle
                              éventuelle

État actuel : exploration numérique.
Aucun dispositif physique n'a encore été réalisé.
L'infalsifiabilité de la signature n'est pas démontrée.
