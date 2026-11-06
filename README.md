Code-Barres Topologique

De la jonction Josephson à la résonance spectrale

« Signature physique structurée — étude numérique exploratoire »

«Statut : Simulation numérique — aucune validation expérimentale.
Domaines : Physique de la matière condensée · Photonique · PUF · Cryptographie physique.»

---

1. Présentation

Ce projet explore une idée simple mais exigeante : construire une identité à partir de la réponse physique propre d'une structure matérielle, plutôt qu'à partir d'un marquage externe tel qu'une encre, un motif imprimé ou un identifiant électronique conventionnel.

Le principe général est celui d'un code-barres physique :

«une structure matérielle possède une configuration interne ;
cette configuration produit une réponse physique ;
cette réponse est mesurée, transformée en signature numérique puis utilisée pour identifier la structure.»

La question centrale n'est donc pas seulement de produire un signal distinctif, mais d'étudier simultanément quatre propriétés :

- distinctivité — deux structures doivent produire des réponses suffisamment différentes ;
- stabilité — une même structure doit rester identifiable malgré les perturbations de lecture ;
- reproductibilité de lecture — la signature doit pouvoir être retrouvée à partir de mesures indépendantes ;
- difficulté de reproduction — reconstruire volontairement la même réponse doit être plus difficile que simplement reproduire l'algorithme de lecture.

Le projet étudie ainsi le passage :

MICROSTRUCTURE
     ↓
DYNAMIQUE PHYSIQUE
     ↓
RÉPONSE MESURABLE
     ↓
EXTRACTION DE CARACTÉRISTIQUES
     ↓
SIGNATURE
     ↓
CORRECTION / ROBUSTESSE
     ↓
IDENTITÉ PHYSIQUE

La propriété d'identité ne se situe donc pas dans le seul signal numérique final : elle dépend de l'ensemble du couplage entre structure, dynamique physique et protocole de lecture.

---

2. Trois architectures physiques

Trois mécanismes ont été explorés numériquement.

Architecture| Support physique modélisé| Information extraite| Statut
1 — Josephson / RCSJ| Réseau 2D de jonctions frustrées| Réponse dynamique sous biais| Reproduit, limites identifiées
2 — PUF optique| Désordre de phase et speckle| Motif spatial et bits extraits| Reproduit, limites identifiées
3 — Spectrale| Ensemble de résonances fréquentielles| Signature fréquentielle| Résultats rapportés, à reproduire

Ces trois voies ne constituent pas trois variantes d'un même algorithme.

Elles testent trois façons différentes de transformer une structure physique en information :

JOSEPHSON
Dynamique collective
       ↓
Réponse courant–tension


OPTIQUE
Désordre spatial
       ↓
Speckle
       ↓
Extraction de bits


SPECTRALE
Résonances
       ↓
Empreinte fréquentielle
       ↓
Décodage

---

3. Architecture 1 — Josephson / RCSJ

La première architecture utilise un réseau bidimensionnel de jonctions Josephson frustrées.

Le système est étudié sous différentes valeurs de frustration, de biais et de température, avec intégration temporelle de la dynamique des phases.

L'information n'est donc pas codée directement dans une valeur arbitraire : elle est recherchée dans la réponse collective du réseau.

Résultat principal

Les simulations montrent qu'une séparation statistique entre plusieurs états de frustration peut être obtenue après calibration.

Cependant, la lecture sur une mesure unique reste sensible :

- au bruit thermique ;
- aux paramètres de lecture ;
- à la taille du réseau ;
- au choix du biais ;
- aux différences entre calibration et mesure.

Les reproductions indépendantes indiquent des taux d'erreur de classification encore significatifs.

Conclusion : le mécanisme physique est intéressant comme générateur de réponse structurée, mais la robustesse d'une identification unitaire n'est pas encore suffisante.

---

4. Architecture 2 — PUF optique

La deuxième architecture exploite le désordre optique.

Une distribution de phases aléatoires produit, après propagation et transformation de Fourier, un motif de speckle complexe. Des caractéristiques spatiales de ce motif sont ensuite transformées en bits.

Une couche Reed–Solomon est utilisée pour tolérer une partie des erreurs de lecture.

L'étude permet notamment de distinguer :

VARIATION DU BRUIT
        ↓
VARIATION DU SPECKLE
        ↓
ERREURS DE BITS
        ↓
CORRECTION
        ↓
DÉCISION

Résultat principal

La réponse peut être fortement distinctive entre configurations indépendantes.

En revanche, les rotations, le bruit et surtout les transformations géométriques du motif dégradent rapidement la lecture lorsqu'aucune procédure d'alignement adaptée n'est utilisée.

Le problème devient alors un problème de protocole de lecture, et non simplement de génération d'un motif aléatoire.

Conclusion : le désordre optique fournit une source naturelle de complexité, mais l'invariance aux conditions réelles de mesure doit encore être construite.

---

5. Architecture 3 — Signature spectrale

La troisième architecture explore une représentation différente : coder l'information dans un ensemble de résonances fréquentielles.

Le lecteur ne cherche plus un motif spatial, mais une configuration spectrale :

STRUCTURE
   ↓
RÉSONANCES
   ↓
SPECTRE MESURÉ
   ↓
MATCHING / DÉTECTION
   ↓
96 CANAUX
   ↓
SIGNATURE

Cette approche est particulièrement intéressante parce qu'elle transforme directement une structure fréquentielle en espace d'information exploitable.

Les simulations rapportées localement montrent une bonne tolérance simulée au bruit et à certains décalages spectraux, avec utilisation d'un décodage correcteur.

Ces résultats n'ont toutefois pas encore fait l'objet d'une reproduction indépendante complète et ne constituent donc pas une validation expérimentale ou une démonstration de PUF physique.

Point critique

La question essentielle pour cette architecture est la suivante :

«Les fréquences sont-elles une propriété émergente d'une microstructure réelle, ou simplement des paramètres imposés numériquement ?»

Dans le premier cas, elles peuvent constituer une véritable empreinte physique.

Dans le second, elles constituent essentiellement un mécanisme de codage spectral.

La transition entre les deux constitue l'une des étapes expérimentales majeures du projet.

---

6. Du signal à l'identité

Le projet distingue explicitement plusieurs niveaux qui sont souvent confondus dans les systèmes d'identification physique :

Niveau 1 — Information

Le système produit une réponse mesurable.

Niveau 2 — Distinction

Deux configurations produisent des réponses statistiquement séparables.

Niveau 3 — Robustesse

La même configuration reste identifiable malgré le bruit et les perturbations de mesure.

Niveau 4 — Non-clonabilité

La reproduction volontaire de la réponse devient difficile sans accès à la structure physique elle-même.

Niveau 5 — Identité physique

La signature devient alors exploitable comme identité attachée au matériau.

RÉPONSE
  ↓
DISTINCTION
  ↓
ROBUSTESSE
  ↓
NON-CLONABILITÉ
  ↓
IDENTITÉ

Le projet se situe actuellement entre les niveaux 1 à 3 selon l'architecture.

La non-clonabilité physique et l'identité expérimentale restent à démontrer.

---

7. Architecture informationnelle

Une fois la réponse physique acquise, elle peut être traitée comme une chaîne d'information :

              MATÉRIAU
                 │
                 ▼
        ┌─────────────────┐
        │ STRUCTURE       │
        │ PHYSIQUE        │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ DYNAMIQUE /     │
        │ RÉSONANCE       │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ MESURE          │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ EXTRACTION      │
        │ DE CARACTÈRES   │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ SIGNATURE        │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ CORRECTION       │
        │ D'ERREURS        │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ IDENTIFICATION   │
        └─────────────────┘

La correction d'erreurs ne crée pas l'identité physique : elle permet de préserver l'information extraite lorsque la mesure est imparfaite.

---

8. Ce qui est établi et ce qui reste ouvert

Établi dans ce projet

- plusieurs mécanismes physiques peuvent être simulés comme sources de signatures structurées ;
- des réponses distinctives peuvent être obtenues numériquement ;
- les perturbations de lecture peuvent être quantifiées ;
- des mécanismes de correction d'erreurs peuvent améliorer la robustesse de décodage ;
- les trois architectures présentent des compromis physiques différents.

À établir

- fabrication d'une microstructure réelle ;
- correspondance quantitative entre microstructure et paramètres du modèle ;
- stabilité temporelle de la signature ;
- stabilité thermique ;
- reproductibilité expérimentale ;
- modèle d'attaque et de clonage ;
- entropie réellement exploitable ;
- démonstration qu'une signature physique est effectivement difficile à reproduire.

---

9. Statut scientifique

Ce dépôt est un prototype de recherche numérique.

Les résultats présentés ici ne doivent pas être interprétés comme une preuve qu'un code-barres topologique physiquement infalsifiable a été réalisé.

L'hypothèse étudiée est plus précise :

«Une structure matérielle complexe peut-elle transformer ses degrés de liberté physiques en une réponse mesurable, distinctive, robuste et exploitable comme identité ?»

Le projet cherche à répondre à cette question en faisant progressivement passer le problème :

du modèle numérique → au protocole de lecture → au dispositif physique.

---

10. Prochaine étape

La prochaine phase consiste à déterminer quelle architecture possède le meilleur rapport entre :

complexité physique · stabilité · distinctivité · capacité d'extraction · robustesse · difficulté de clonage.

L'architecture spectrale constitue actuellement une voie prioritaire pour cette étude, mais elle doit encore franchir l'étape essentielle du passage simulation → réalisation physique.

---

11. Références principales

- M. Tinkham, Introduction to Superconductivity, 2nd ed., McGraw-Hill, 1996.
- S. Teitel & C. Jayaprakash, Phase transitions in frustrated two-dimensional XY models, Physical Review B, 27, 598–601, 1983.
- R. Pappu, B. Recht, J. Taylor & N. Gershenfeld, Physical One-Way Functions, Science, 297, 2026–2030, 2002.
- Y. Dodis, L. Reyzin & A. Smith, Fuzzy Extractors: How to Generate Strong Keys from Biometrics and Other Noisy Data, EUROCRYPT 2004.

---

Statut du dépôt

Recherche exploratoire · Simulation numérique · Reproductibilité en cours · Validation expérimentale future
