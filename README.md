# Code-Barres Topologique : Jumeau Numérique

**Statut du projet :** Phase 1 & Phase 2 — ✅ Validées
**Domaine :** Physique de la matière condensée, Réseaux de Josephson, Métrologie numérique.

## 📌 Présentation du Projet
Ce dépôt contient le code source, les modèles mathématiques et les résultats de simulation d'un projet de recherche visant à créer une signature électrodynamique non-linéaire (un "code-barres topologique"). L'objectif est de développer une méthode d'identification physique infalsifiable, basée sur la structure microscopique d'un matériau (frustration magnétique).

## 📊 Résultats Clés

### Phase 1 : Validation du Concept Physique
*   **Courbe I-V** : Le réseau présente un seuil de décrochage dépendant de la frustration `f`.
*   **Discrimination** : À un courant de lecture fixe (I=0.35) sur un réseau N=32, le ratio signal/bruit atteint ρ = 14.43 pour la frustration f=0.40.
*   ![Courbe I-V](courbe_iv_v16.png)

### Phase 2 : Robustesse Thermique (Le Crash Test)
Le système a été soumis à une dérive thermique (Loi d'Arrhenius). 
*   Un **scanner naïf (1D)** qui lit la tension à un seul biais échoue à **43.3%** à cause du bruit thermique.
*   Un **scanner vectoriel intelligent (V27)** utilisant 4 biais simultanés (0.24, 0.30, 0.36, 0.42) et un système de vote de métriques statistiques (Mahalanobis, KL-NLL) réduit le taux d'erreur à **3.3%**, prouvant la viabilité du concept dans des conditions réelles.

## 📂 Structure du Dépôt
```text
├── README.md                     # Ce fichier
├── RAPPORT_PHASE_1.md            # Rapport technique détaillé
├── requirements.txt              # Dépendances (Numpy, Matplotlib)
├── moteur_fluxons_2d.py          # Cœur physique (Modèle RCSJ, Jauge de Landau)
├── plot_iv.py                    # Script de visualisation graphique
├── test_v16_precision.py         # Génération des courbes I-V
├── test_v18_rho_tension.py       # Calcul de la métrique ρ (Phase 1)
├── test_v21_cartographie_temp.py # Mesure de la dérive thermique
├── test_v23_scanner_mahalanobis.py # Test des métriques de distance
└── test_v27_scanner_4d.py        # Scanner intelligent 4D (Phase 2)
