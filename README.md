# Code-Barres Topologique : Jumeau Numérique (Phase 1)

**Statut du projet :** Phase 1 (Validation Numérique) — ✅ Validée
**Domaine :** Physique de la matière condensée, Réseaux de Josephson, Métrologie numérique.

## 📌 Présentation du Projet
Ce dépôt contient le code source, les modèles mathématiques et les résultats de simulation de la **Phase 1** d'un projet de recherche visant à créer une signature électrodynamique non-linéaire (un "code-barres topologique").
L'objectif à long terme est de développer une méthode d'identification physique infalsifiable, basée sur la structure microscopique (frustration magnétique) d'un matériau plutôt que sur une marque de surface.

Ce jumeau numérique permet de tester la viabilité de l'architecture **avant** toute fabrication physique coûteuse.

## 📊 Résultats Clés (Phase 1)
La simulation démontre qu'un réseau de jonctions Josephson frustré possède une courbe courant-tension (I-V) présentant un seuil de décrochage dépendant de la frustration `f`.

*   **Robustesse d'échelle :** Le passage de N=16 à N=32 réduit le bruit de bord (écart-type divisé par 4), rendant la signature lisible.
*   **Discrimination (Métrique \(\rho\)) :** À un courant de lecture fixe (I=0.35) sur un réseau N=32, le ratio signal/bruit atteint **\(\rho = 14.43\)** pour la frustration \(f=0.40\), garantissant une lecture industrielle infaillible.

![Courbe I-V](results/courbe_iv_v16.png)

*(Pour lire l'analyse complète et le cahier des charges pour l'ingénierie, consultez le [RAPPORT_PHASE_1.md](RAPPORT_PHASE_1.md))*

## 📂 Structure du Dépôt
```text
├── README.md                     # Ce fichier
├── RAPPORT_PHASE_1.md            # Rapport technique détaillé de l'étape 1
├── requirements.txt              # Dépendances Python (Numpy, Matplotlib)
├── src/                          # Code source de la simulation
│   ├── moteur_fluxons_2d.py      # Cœur physique (Modèle RCSJ, Jauge de Landau)
│   ├── test_v16_precision.py     # Génération des courbes I-V (N=16 et N=32)
│   ├── test_v18_rho_tension.py   # Calcul de la métrique de discrimination (rho)
│   └── plot_iv.py                # Script de visualisation graphique
└── results/                      # Dossier des preuves et données
    ├── courbe_iv_v16.png         # Graphique généré
    └── resultats_v16_N32.npy     # Données brutes de la simulation N=32
