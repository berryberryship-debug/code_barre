import numpy as np
from moteur_fluxons_2d import MoteurFluxons2D

def mesurer_vecteur(f, N, seed, T, biais_list):
    """Mesure le vecteur de tension macroscopique V aux biais spécifiés."""
    V = []
    for gd in biais_list:
        m = MoteurFluxons2D(N=N, frustration=f, seed=seed, gamma_dc=gd, temperature=T)
        m.appliquer_bruit_ci(0.01)
        m.integrer(n_steps=4000)  # Etablissement du regime permanent
        
        v_series = []
        for _ in range(150):
            m.integrer(n_steps=1)
            v_series.append(np.mean(m.v[:, -1] - m.v[:, 0]))
        V.append(abs(np.mean(v_series)))
    return np.array(V)

def distance_mahalanobis(x, mean, cov_inv):
    """Calcule la distance de Mahalanobis au carre : (x - mu)^T * Sigma^(-1) * (x - mu)."""
    diff = x - mean
    return np.dot(diff.T, np.dot(cov_inv, diff))

def main():
    print("=== V23: SCANNER MULTIVARIE OPTIMAL (DISTANCE DE MAHALANOBIS) ===")
    
    N = 32
    levels = [0.25, 0.30, 0.35]
    biais = [0.30, 0.36]
    T_test = 0.05
    n_calib = 15   # Nombre de graines accru pour stabiliser l'estimation de covariance
    n_tests = 10   # Echantillons de validation par niveau
    
    # -------------------------------------------------------------
    # 1. Etalonnage statistique a T = 0.05
    # -------------------------------------------------------------
    print(f"\n1. Apprentissage des signatures statistiques a T = {T_test} (N={n_calib} graines)...")
    
    means = {}
    cov_invs = {}
    
    for f in levels:
        vecs = np.array([
            mesurer_vecteur(f, N, seed=1000 + i, T=T_test, biais_list=biais) 
            for i in range(n_calib)
        ])
        
        # Vecteur moyen mu_f
        mu_f = np.mean(vecs, axis=0)
        means[f] = mu_f
        
        # Matrice de covariance empirique Sigma_f (2x2)
        # On ajoute une regularisation de Tikhonov (1e-6) pour eviter toute singularite numerique
        cov_f = np.cov(vecs, rowvar=False) + np.eye(2) * 1e-6
        cov_invs[f] = np.linalg.inv(cov_f)
        
        var_v30 = cov_f[0, 0]
        var_v36 = cov_f[1, 1]
        print(f"  f={f:.2f} | mu=[{mu_f[0]:.3f}, {mu_f[1]:.3f}] | Var(0.30)={var_v30:.2e} | Var(0.36)={var_v36:.2e}")

    # -------------------------------------------------------------
    # 2. Phase de test et comparaison des metriques
    # -------------------------------------------------------------
    print(f"\n2. Test de lecture aveugle ({n_tests} lectures par niveau)...")
    
    errors_euclid = 0
    errors_mahalanobis = 0
    total = 0
    
    for f in levels:
        tests = [
            mesurer_vecteur(f, N, seed=3000 + i, T=T_test, biais_list=biais) 
            for i in range(n_tests)
        ]
        
        for v_test in tests:
            total += 1
            
            # --- METHODE 1 : Distance Euclidienne 2D (Scanner V22) ---
            best_f_euclid = min(levels, key=lambda cand: np.linalg.norm(v_test - means[cand]))
            if best_f_euclid != f:
                errors_euclid += 1
            
            # --- METHODE 2 : Distance de Mahalanobis (Scanner V23) ---
            best_f_maha = min(levels, key=lambda cand: distance_mahalanobis(v_test, means[cand], cov_invs[cand]))
            if best_f_maha != f:
                errors_mahalanobis += 1

    # -------------------------------------------------------------
    # 3. Resultats
    # -------------------------------------------------------------
    err_rate_e = (errors_euclid / total) * 100
    err_rate_m = (errors_mahalanobis / total) * 100
    
    print("\n3. Synthese des performances :")
    print(f"-> Taux d'erreur Euclidien 2D (V22) :    {err_rate_e:.1f} %")
    print(f"-> Taux d'erreur Mahalanobis 2D (V23) :  {err_rate_m:.1f} %")
    
    if err_rate_m == 0:
        print("-> OBJECTIF ATTEINT : 0.0 % d'erreur (discrimination parfaite du materiau).")

if __name__ == "__main__":
    main()
