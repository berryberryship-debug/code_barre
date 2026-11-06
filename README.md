Code-Barres Topologique

De la jonction Josephson à la résonance spectrale

«Signature physique structurée — étude numérique exploratoire»

Statut : simulation numérique — aucune validation expérimentale
Domaines : physique de la matière condensée · photonique · PUF · cryptographie physique

---

1. Présentation

Ce projet explore la possibilité de construire une signature physique difficile à reproduire, comparable dans sa fonction à un code-barres, mais dont l'information serait portée par la structure physique d'un matériau plutôt que par une encre ou un motif visuel.

L'objectif n'est pas encore de démontrer une signature « infalsifiable ».

La question étudiée est plus fondamentale :

«Une microstructure physique peut-elle produire une réponse mesurable suffisamment stable, distinctive et difficile à reproduire pour constituer une identité physique ?»

Trois architectures ont été explorées numériquement :

Architecture| Principe| Statut
1 — Josephson / RCSJ| Réseau de jonctions frustrées| Reproduit, limites identifiées
2 — PUF optique| Speckle produit par désordre optique| Reproduit, limites identifiées
3 — Spectrale| Codage par résonances fréquentielles| Résultats rapportés, à reproduire

Aucun matériau réel n'a encore été fabriqué ou mesuré.

Le lien entre les paramètres des modèles numériques et une microstructure physique réelle reste donc une hypothèse à établir expérimentalement.

---

2. Architecture générale

Le projet suit trois niveaux de recherche :

STRUCTURE PHYSIQUE
       │
       ▼
RÉPONSE PHYSIQUE
       │
       ▼
LECTURE / EXTRACTION
       │
       ▼
SIGNATURE NUMÉRIQUE
       │
       ▼
CORRECTION D'ERREURS
       │
       ▼
IDENTITÉ PHYSIQUE

Une architecture ne peut être considérée comme une PUF réelle simplement parce qu'elle produit des bits différents en simulation.

Il faut également établir :

- la reproductibilité de la lecture ;
- la stabilité environnementale ;
- l'unicité entre dispositifs ;
- l'entropie effectivement disponible ;
- la résistance aux attaques ;
- la difficulté de fabriquer ou prédire une copie ;
- la stabilité du lien entre microstructure et signature.

---

3. Architecture 1 — Réseau de jonctions Josephson

3.1 Principe

On considère un réseau 2D de phases couplées soumis à une frustration magnétique transverse.

La frustration "f" modifie la dynamique du réseau et donc sa réponse à un courant de lecture.

L'idée explorée est d'utiliser cette réponse comme un alphabet de niveaux physiques.

frustration f
      │
      ▼
réseau de phases
      │
      ▼
dynamique non linéaire
      │
      ▼
tension simulée V
      │
      ▼
classe / signature

Le modèle est apparenté aux modèles de jonctions Josephson de type RCSJ, mais la correspondance quantitative avec un dispositif réel n'est pas établie.

Référence de contexte :

Tinkham, M., Introduction to Superconductivity, 2nd ed., McGraw-Hill, 1996.

---

3.2 Modèle numérique

- réseau "N × N" ;
- dynamique de second ordre amortie ;
- "γ = 0.1" ;
- "dt = 0.05" ;
- intégrateur de type vitesse-Verlet ;
- jauge de Landau :

A_x = -f · i

- bords ouverts ;
- aucun "np.roll" pour les interactions spatiales ;
- biais DC injecté sur la colonne 0 ;
- extraction sur la colonne "N−1".

L'observable utilisée est :

V = | <v(colonne N−1)> − <v(colonne 0)> |

où "V" est exprimé dans les unités du modèle, et non en volts.

«"beta_c" apparaît dans le code mais n'est actuellement pas utilisé dans la dynamique.»

---

4. Résultats de l'architecture Josephson

4.1 Courbe I–V

Le décrochage dépend de "f".

Cependant, le seuil dépend également de la taille du réseau :

- "N = 32", "f = 0.25" : seuil ≈ "0.22"
- "N = 16", "f = 0.25" : seuil ≈ "0.32–0.36"

Le seuil n'est donc pas convergé en taille.

Le seuil indiqué dans les figures ne doit pas être interprété comme une constante physique universelle.

---

4.2 Séparation des niveaux

Pour "N = 32" et 20 graines par niveau, les moyennes de plusieurs classes sont séparées.

Cependant :

- "f = 0.05" et "f = 0.10" ne sont pas séparés à un biais de "0.30" ;
- ils constituent donc une seule classe dans cette condition ;
- les écarts observés concernent les moyennes de populations, pas une lecture individuelle.

Pour une lecture unique, l'écart entre niveaux voisins est d'environ :

2 à 3,6 σ

avec :

σ ≈ 0,03–0,045

La probabilité d'erreur entre voisins est alors estimée grossièrement à ≈ 5–18 % par côté.

La métrique "ρ" utilisée précédemment n'est pas retenue comme indicateur fiable de séparation lorsque les tensions sont proches de zéro.

---

5. Température : limite majeure

Un bruit de Langevin introduit une dérive systématique de la réponse.

À :

T = 0.05

la dérive observée est de l'ordre de :

+0.07 à +0.12

en unités du modèle.

Cette variation est comparable à l'écart entre certains niveaux.

Une calibration effectuée à "T = 0" ne peut donc pas être considérée comme représentative d'une lecture à température différente.

Point important

Le modèle utilise un bruit de Langevin.

Il n'est donc pas justifié d'attribuer directement la dérive observée à une « loi d'Arrhenius ».

De même, les chiffres antérieurs annonçant une erreur passant de "2 %" à plus de "50 %" ne sont pas reproduits par le moteur actuel et ne sont plus utilisés comme résultats de référence.

---

6. Scanner multi-biais — V27

Le protocole utilise :

f = 0.25, 0.30, 0.35
biais = 0.24, 0.30, 0.36, 0.42
T = 0.05
15 graines de calibration par niveau
lectures de test indépendantes

La calibration et le test sont effectués à la même température.

Ce protocole mesure donc la classification dans un environnement thermique identique, et ne mesure pas la robustesse à une dérive de température.

Résultats

Expérience| Méthode| Erreur
Rapportée — 45 lectures| MahaDiag| 8,9 %
Rapportée — 45 lectures| Vote| 17,8 %
Reproduction — 45 lectures| MahaDiag| 17,8 %
Reproduction — 45 lectures| KL_NLL| 13,3 %
Reproduction — 120 lectures| MahaDiag| 15,8 %
Reproduction — 120 lectures| KL_NLL| 17,5 %
Reproduction — 120 lectures| Vote| 19,2 %
Reproduction — 120 lectures| Vote + MahaDiag| 15,0 %

Les intervalles de confiance se chevauchent.

Il n'est donc pas possible d'affirmer qu'une méthode de classification est supérieure aux autres sur la base de ces expériences.

---

6.1 Conclusion architecture 1

Le modèle montre une relation exploitable entre frustration et réponse dynamique.

Il montre également des limites importantes :

- dépendance à "N" ;
- séparation insuffisante de certains niveaux ;
- variance entre graines ;
- dérive thermique ;
- classification imparfaite ;
- absence de lien expérimental avec un matériau réel.

Verdict

Architecture intéressante comme modèle physique, mais non validée comme signature robuste en lecture unique.

---

7. Architecture 2 — PUF optique

7.1 Principe

La seconde approche abandonne la réponse Josephson et exploite le désordre optique.

Conceptuellement :

laser
  │
  ▼
matériau désordonné
  │
  ▼
diffraction multiple
  │
  ▼
speckle
  │
  ▼
image caméra
  │
  ▼
extraction de bits
  │
  ▼
Reed–Solomon
  │
  ▼
clé

Le cadre théorique est notamment lié aux travaux sur les PUF optiques et les fuzzy extractors.

Références :

Pappu, R., Recht, B., Taylor, J. & Gershenfeld, N. (2002), Physical One-Way Functions, Science 297, 2026–2030.

Dodis, Y., Reyzin, L. & Smith, A. (2004), travaux sur les fuzzy extractors, EUROCRYPT.

---

8. Modèle optique simulé

Le modèle utilise :

- masque de phase "128 × 128" ;
- phases i.i.d. dans "[0, 2π]" ;
- FFT ;
- intensité normalisée ;
- bruit gaussien de caméra ;
- rotation du masque par interpolation spline.

Extraction :

filtre gaussien σ = 2
        ↓
blocs 4 × 4
        ↓
différences horizontales
        ↓
masque circulaire
        ↓
seuil médian
        ↓
96 bits stables

La correction utilise :

RS(12,6)

soit 12 octets dont 6 octets de données.

Le code peut corriger jusqu'à 3 octets erronés dans les conditions appropriées.

---

9. Résultats PUF optique

Condition| Puces| BER moyen| Échecs
bruit 0.01, sans rotation| 600| 0 %| 0/600
bruit 0.05, sans rotation| 600| 2,12 %| 77/600
bruit 0.10, sans rotation| 600| 11,4 %| 96,8 %
rotation 1°, sans recalage| 150| 6,5 %| 82 %
rotation 3,5°, sans recalage| 150| 22,2 %| 100 %
rotation 1°, recalage| 150| 5,0 %| 60,7 %
rotation 3,5°, recalage| 150| 3,4 %| 28,7 %
rotation 3,5°, bruit 0.05, recalage| 150| 7,6 %| 84 %

Les intervalles de confiance sont donnés dans le rapport expérimental détaillé.

---

9.1 Ce que ces résultats montrent

Le modèle présente une bonne séparation inter-puces :

distance moyenne ≈ 49,97 %

pour 300 puces simulées.

Cependant, cette valeur est attendue avec des phases i.i.d. et ne constitue donc pas à elle seule une démonstration d'unicité physique.

À bruit "0.05", la reconstruction échoue dans :

77 / 600 = 12,8 %

des essais.

La phrase :

«« la clé est identique à chaque lecture »»

n'est donc pas compatible avec ce résultat.

---

10. Entropie et sécurité

96 bits sont extraits dans le modèle.

Une estimation de type Daugman donne environ :

84 bits indépendants équivalents

Cette valeur n'est pas une estimation de min-entropie.

La clé de preuve de concept est générée à partir de :

np.random.bytes(6)

soit seulement :

48 bits

et non 128 ou 256 bits.

Le générateur utilisé n'est pas présenté comme un générateur cryptographique.

Après retrait de la redondance, l'estimation grossière de l'entropie résiduelle est de l'ordre de :

36–40 bits

Cette estimation doit être considérée comme indicative, pas comme une borne cryptographique.

---

11. Limite importante du recalage

Le recalage actuellement utilisé s'appuie sur l'image de référence d'enrôlement.

Cette référence étant liée à la réponse secrète, la conserver dans un système réel pourrait exposer cette réponse.

Un dispositif déployable nécessiterait plutôt un repère public ou une information d'alignement indépendante du secret.

Cette solution n'a pas encore été testée.

---

12. Verdict architecture 2

La PUF optique simulée est intéressante parce qu'elle combine :

- désordre ;
- réponse complexe ;
- extraction de bits ;
- correction d'erreurs.

Cependant :

- le modèle reste numérique ;
- le bruit est artificiellement choisi ;
- la rotation reste problématique ;
- le recalage actuel n'est pas déployable tel quel ;
- l'attaque par modélisation ou copie n'est pas étudiée ;
- aucune microstructure réelle n'a été fabriquée.

Verdict

Architecture prometteuse pour une étude expérimentale, mais PUF physique non démontrée.

---

13. Architecture 3 — Code-barres spectral

13.1 Changement de représentation

La troisième architecture abandonne le codage spatial.

L'information est représentée par un ensemble de résonances fréquentielles.

             espace
               │
        ┌──────┴──────┐
        │             │
   motif spatial   spectre
        │             │
     rotation      lecture
     sensible      1D

Le principe est de coder 96 bits dans 96 canaux fréquentiels.

Chaque canal est représenté par une résonance de forme lorentzienne.

La lecture peut utiliser :

- détection des pics ;
- assignation au canal le plus proche ;
- ou filtre adapté (matched filter).

---

14. Pourquoi l'architecture spectrale est intéressante

Une représentation spectrale possède une propriété structurelle :

«une rotation dans le plan de lecture ne constitue pas directement une transformation du spectre 1D.»

Cela ne signifie toutefois pas qu'un dispositif réel serait automatiquement invariant à l'orientation.

L'angle d'incidence, la géométrie du matériau, la polarisation et les conditions de mesure peuvent modifier le spectre.

Cette invariance doit donc être mesurée expérimentalement, et non simplement déduite de la représentation numérique.

---

15. Résultats rapportés — à reproduire

Les résultats suivants proviennent de simulations rapportées dans le dépôt mais n'ont pas encore été relus et reproduits indépendamment :

- bruit "0.05" et "0.10" : BER annoncé < 4 % ;
- bruit "0.20" : 11 octets erronés sur 12 ;
- dérive de "2.0" et "4.0" unités : reconstruction annoncée réussie ;
- Monte Carlo : "100/100" reconstructions annoncées réussies ;
- erreur moyenne annoncée : ≈ "1 bit / 96".

Ces résultats sont donc classés :

«RAPPORTÉS — NON REPRODUITS»

et ne doivent pas être présentés comme une validation expérimentale ou numérique indépendante.

---

16. Lecture critique du « 100/100 »

Un résultat de :

100 succès / 100 essais

ne signifie pas mathématiquement que le taux de succès réel est de 100 %.

Avec 100 essais et aucun échec, une borne inférieure approximative du taux de succès à 95 % est de l'ordre de :

96,3 %

Le taux d'échec réel peut donc encore être de plusieurs pourcents.

De plus, si l'on suppose approximativement des erreurs indépendantes et une moyenne d'environ 1 bit erroné par lecture, un modèle de Poisson donne une probabilité non nulle d'obtenir au moins 4 octets erronés après regroupement.

Le résultat "100/100" constitue donc un signal encourageant, pas une démonstration de robustesse.

---

17. Conditions nécessaires avant une conclusion physique

Pour évaluer réellement l'architecture spectrale, il faut documenter :

Spectre

- amplitude des résonances ;
- largeur des pics ;
- espacement entre canaux ;
- rapport signal/bruit ;
- définition exacte du bruit ;
- définition des unités de dérive.

Lecture

- résolution fréquentielle ;
- méthode d'estimation ;
- seuil de détection ;
- algorithme d'assignation ;
- comportement lorsque deux canaux deviennent ambigus.

Stabilité

- température ;
- angle d'incidence ;
- polarisation ;
- vieillissement ;
- répétition de mesure ;
- dispersion entre échantillons.

Sécurité

- taille réelle de la clé ;
- entropie ;
- modèle d'attaquant ;
- possibilité de mesurer puis reproduire le spectre ;
- difficulté de fabriquer une structure présentant les mêmes résonances.

---

18. Attention au statut PUF

Un ensemble de fréquences imposées par le concepteur n'est pas automatiquement une PUF.

Si les 96 fréquences sont simplement choisies par le système et qu'elles peuvent être mesurées puis reproduites, elles constituent essentiellement une étiquette spectrale.

Pour obtenir une véritable fonction physiquement non clonable, il faut établir que la réponse provient d'une microstructure difficile à reproduire et qu'elle présente suffisamment d'entropie imprévisible.

Le problème fondamental devient alors :

microstructure
      ↓
réponse physique
      ↓
signature

et non simplement :

96 bits
      ↓
96 fréquences

---

19. Comparaison des trois architectures

Critère| Josephson| PUF optique| Spectrale
Simulation| ✓| ✓| ✓
Reproduction indépendante| ✓| ✓| ✗
Désordre physique| non| simulé| non établi
Lecture unique robuste| faible| limitée| à déterminer
Sensibilité thermique| forte| modérée dans le modèle| à déterminer
Sensibilité rotation| faible| forte| potentiellement faible
Correction RS| non| ✓| ✓
Entropie étudiée| limitée| partiellement| non établie
Attaque de clonage| non étudiée| non étudiée| non étudiée
Matériau réel| ✗| ✗| ✗

---

20. Conclusion de la phase numérique

Les trois architectures conduisent à une même question : où placer l'information physique pour maximiser stabilité, diversité et difficulté de reproduction ?

Architecture 1 — Josephson

Le modèle produit une réponse dépendante de la frustration, mais la séparation des niveaux et la stabilité thermique restent insuffisantes pour une lecture unique robuste.

Architecture 2 — PUF optique

Le speckle fournit une forte diversité simulée et permet une extraction de bits avec correction d'erreurs, mais la rotation, le bruit et le mécanisme de recalage restent des problèmes ouverts.

Architecture 3 — Spectrale

La représentation fréquentielle paraît particulièrement intéressante pour une lecture compacte et potentiellement moins sensible à l'orientation.

Cependant, sa robustesse n'est pas encore établie par reproduction indépendante.

---

21. Décision de recherche

À l'issue de cette phase numérique :

«L'architecture spectrale est retenue comme piste prioritaire pour une étude numérique approfondie puis, seulement si les critères de validation sont satisfaits, pour une conception expérimentale.»

Cette décision est une orientation de recherche, et non la conclusion que la technologie est déjà démontrée.

---

22. Critères de passage à une phase expérimentale

Une phase matérielle ne devrait être engagée qu'après obtention d'un protocole numérique reproductible montrant au minimum :

- un ensemble d'échantillons indépendants ;
- des lectures répétées ;
- une séparation inter/intra-échantillon ;
- une température contrôlée et documentée ;
- une analyse statistique préenregistrée ;
- une estimation d'entropie adaptée ;
- un protocole d'attaque ;
- une définition précise du taux d'erreur ;
- une démonstration que le signal n'est pas simplement une donnée imposée par le concepteur.

---

23. Historique des corrections du moteur

Les premières versions du modèle Josephson comportaient plusieurs problèmes structurels :

- force de signe inversé ;
- dynamique pouvant augmenter artificiellement l'énergie ;
- "A_x" de mauvaise forme ;
- bords périodiques via "np.roll" ;
- court-circuit potentiel du biais ;
- énergie définie sur les sites plutôt que sur les interactions.

Les résultats antérieurs à la version corrigée à bords ouverts et force corrigée ne sont donc pas considérés comme des résultats de référence.

---

24. Reproduction

pip install -r requirements.txt
pip install reedsolo

Josephson

python test_v16_precision.py
python test_v16c_matrice_confusion.py
python test_v19_temperature.py
python test_v27_scanner_4d.py

PUF optique

python test_v33_vrai_fuzzy.py
python test_puf_rotation.py

Spectre

python test_resonance_spectrale.py
python test_monte_carlo_spectral.py

«Les deux derniers scripts doivent encore être relus et reproduits avant que leurs résultats puissent être intégrés au bilan quantitatif.»

---

25. Structure du dépôt

README.md
RAPPORT_PHASE_1.md
requirements.txt

moteur_fluxons_2d.py

plot_iv.py

test_v16_precision.py
test_v16c_matrice_confusion.py
test_v18_rho_tension.py
test_v19_temperature.py
test_v21_cartographie_temp.py
test_v23_scanner_mahalanobis.py
test_v27_scanner_4d.py

test_v28_*.py

test_v33_vrai_fuzzy.py
test_puf_rotation.py

test_resonance_spectrale.py
test_monte_carlo_spectral.py

---

26. Dépendances

À compléter avec les versions effectivement utilisées :

Python : à documenter
NumPy  : à documenter
SciPy  : à documenter
reedsolo : à documenter

La durée approximative d'exécution et les graines utilisées doivent également être documentées afin de rendre les résultats pleinement reproductibles.

---

27. Références

Jonctions Josephson / modèles XY

Tinkham, M. (1996).
Introduction to Superconductivity, 2nd ed. McGraw-Hill.

Teitel, S. & Jayaprakash, C. (1983).
Phys. Rev. B 27, 598.

PUF optiques

Pappu, R., Recht, B., Taylor, J. & Gershenfeld, N. (2002).
Physical One-Way Functions.
Science 297, 2026–2030.

Fuzzy extractors

Dodis, Y., Reyzin, L. & Smith, A. (2004).
Travaux fondateurs sur les fuzzy extractors, EUROCRYPT.

Ces références fournissent le cadre scientifique des architectures. Elles ne constituent pas une validation des résultats numériques présentés dans ce dépôt.

---

28. Statut scientifique

Élément| Statut
Modèle Josephson| reproduit
Limites thermiques Josephson| observées dans le modèle
PUF optique Monte Carlo| reproduite
Extraction RS| testée en simulation
Unicité optique| observée dans le modèle
Résistance au clonage| non étudiée
Architecture spectrale| exploratoire
Monte Carlo spectral| à reproduire
Matériau réel| non réalisé
PUF physique réelle| non démontrée
Infalsifiabilité| non démontrée

---

État actuel

Phase 1 — exploration numérique : architectures comparées et limites identifiées.

Piste prioritaire : architecture spectrale.

Prochaine étape scientifique : reproduire intégralement les simulations spectrales, verrouiller les unités et paramètres du modèle, augmenter le nombre d'essais, puis tester explicitement la stabilité, l'entropie et le modèle d'attaque avant toute extrapolation vers un matériau réel.

«Le projet ne prétend pas encore avoir construit un code-barres infalsifiable. Il cherche à déterminer quelles conditions physiques et informationnelles pourraient rendre une telle signature possible.»
