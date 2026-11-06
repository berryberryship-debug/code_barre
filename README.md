# Code-Barres Topologique : Jumeau Numérique (Phase 1)

**Statut du projet :** Phase 1 (Validation Numérique) — ✅ Validée
**Domaine :** Physique de la matière condensée, Réseaux de Josephson, Métrologie numérique.

## 📌 Présentation du Projet
Ce dépôt contient le code source, les modèles mathématiques et les résultats de simulation de la **Phase 1** d'un projet de recherche visant à créer une signature électrodynamique non-linéaire (un "code-barres topologique").
L'objectif à long terme est de développer une méthode d'identification physique infalsifiable, basée sur la structure microscopique (frustration magnétique) d'un matériau plutôt que sur une marque de surface.

Ce jumeau numérique permet de tester la viabilité de l'architecture **avant** toute fabrication physique coûteuse.

## 📊 Résultats Clés (Phase 1)
La simulation démontre qu'un réseau de jonctions Josephson frustré possède une courbe courant-tension (I-V) présentant un seuil de décrochage dépendant de la frustration `f`.

*   **Robustesse d'échelle :** Le passage de N=16 à N=32 réduit le bruit de bord, rendant la signature lisible.
*   **Discrimination (Métrique ρ) :** À un courant de lecture fixe, le ratio signal/bruit atteint ρ = 14.43 pour la frustration f=0.40 sur un réseau N=32, garantissant une séparation nette des lots.

![Courbe I-V](courbe_iv_v16.png)

*(Pour lire l'analyse complète et le cahier des charges pour l'ingénierie, consultez le [RAPPORT_PHASE_1.md](RAPPORT_PHASE_1.md))*

## 📂 Structure du Dépôt
```text
├── README.md                     # Ce fichier
├── RAPPORT_PHASE_1.md            # Rapport technique détaillé
├── requirements.txt              # Dépendances (Numpy, Matplotlib)
├── moteur_fluxons_2d.py          # Cœur physique (Modèle RCSJ, Jauge de Landau)
├── test_v16_precision.py         # Génération des courbes I-V
├── test_v18_rho_tension.py       # Calcul de la métrique de discrimination
├── test_v16c_matrice_confusion.py # Analyse statistique de séparation des lots
├── plot_iv.py                    # Script de visualisation graphique
├── courbe_iv_v16.png             # Graphique généré
└── resultats_v16_N32.npy         # Données brutes de la simulation
