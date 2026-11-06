import numpy as np
from collections import Counter
from moteur_fluxons_2d import MoteurFluxons2D

# ==========================================
# 1. MOTEUR DE MESURE (4 BIAIS)
# ==========================================
def mesurer_vecteur(f, N, seed, T, biais_list):
    """Mesure le vecteur de tension sur les 4 biais spécifiés."""
    V = []
    for gd in biais_list:
        m = MoteurFluxons2D(N=N, frustration=f, seed=seed, gamma_dc=gd, temperature=T)
        m.appliquer_bruit_ci(0.01)
        m.integrer(n_steps=4000)  # Relaxation
        
        v_series = []
        for _ in range(150):      # Mesure
            m.integrer(n_steps=1)
            v_series.append(np.mean(m.v[:, -1] - m.v[:, 0]))
        V.append(abs(np.mean(v_series)))
    return np.array(V)

# ==========================================
# 2. LES 4 METRIQUES DE DISTANCE
# ==========================================
def dist_mahalanobis(x, mu, cov_inv):
    diff = x - mu
    return np.dot(diff.T, np.dot(cov_inv, diff))

def dist_maha_diag(x, mu, cov):
    diff = x - mu
    # On garde seulement la diagonale (les variances), on ignore les covariances
    return np.sum((diff**2) / np.diag(cov))

def dist_maha_shrink(x, mu, cov, alpha=0.4):
    # On "tire" la matrice vers la matrice identité pour la stabiliser
    cov_shrink = (1 - alpha) * cov + alpha * np.eye(len(mu)) * np.trace(cov) / len(mu)
    cov_inv = np.linalg.inv(cov_shrink)
    return dist_mahalanobis(x, mu, cov_inv)

def dist_kl_nll(x, mu, cov):
    d_maha = dist_mahalanobis(x, mu, np.linalg.inv(cov))
    return 0.5 * d_maha + 0.5 * np.log(np.linalg.det(cov))

# ==========================================
# 3. SCRIPT PRINCIPAL
# ==========================================
def main():
    print("=== V27: SCANNER 4D (VOTE MAJORITAIRE SUR 4 METRIQUES) ===")
    
    N = 32
    levels = [0.25, 0.30, 0.35]
    biais = [0.24, 0.30, 0.36, 0.42]  # <--- LES 4 BIAIS
    T_test = 0.05
    n_calib = 15
    n_tests = 15
    
    print(f"\n1. Calibration (T={T_test}, N={n_calib} graines par niveau)...")
    means = {}
    covs = {}
    cov_invs = {}
    
    for f in levels:
        vecs = np.array([mesurer_vecteur(f, N, seed=1000+i, T=T_test, biais_list=biais) for i in range(n_calib)])
        means[f] = np.mean(vecs, axis=0)
        covs[f] = np.cov(vecs, rowvar=False) + np.eye(4) * 1e-6
        cov_invs[f] = np.linalg.inv(covs[f])
        print(f"  Signature apprise pour f={f:.2f}")

    print(f"\n2. Test aveugle ({n_tests} lectures par niveau)...")
    errors = {"Maha": 0, "MahaDiag": 0, "MahaShrink": 0, "KL_NLL": 0, "Vote": 0, "Conflit": 0}
    total = 0
    
    for f in levels:
        tests = [mesurer_vecteur(f, N, seed=3000+i, T=T_test, biais_list=biais) for i in range(n_tests)]
        
        for v_test in tests:
            total += 1
            guesses = []
            
            # On évalue les 4 métriques
            for metric_name in ["Maha", "MahaDiag", "MahaShrink", "KL_NLL"]:
                scores = {}
                for f_cand in levels:
                    if metric_name == "Maha": 
                        scores[f_cand] = dist_mahalanobis(v_test, means[f_cand], cov_invs[f_cand])
                    elif metric_name == "MahaDiag": 
                        scores[f_cand] = dist_maha_diag(v_test, means[f_cand], covs[f_cand])
                    elif metric_name == "MahaShrink": 
                        scores[f_cand] = dist_maha_shrink(v_test, means[f_cand], covs[f_cand])
                    elif metric_name == "KL_NLL": 
                        scores[f_cand] = dist_kl_nll(v_test, means[f_cand], covs[f_cand])
                
                # Le gagnant pour cette métrique
                best_cand = min(scores, key=scores.get)
                guesses.append(best_cand)
                if best_cand != f: 
                    errors[metric_name] += 1
            
            # --- LE VOTE MAJORITAIRE ---
            vote = Counter(guesses).most_common(1)[0]
            if vote[1] >= 3:  # Au moins 3 métriques sur 4 sont d'accord
                best_vote = vote[0]
            else:
                best_vote = None
                errors["Conflit"] += 1
            
            if best_vote != f: 
                errors["Vote"] += 1

    # ==========================================
    # 4. RESULTATS
    # ==========================================
    print("\n3. Synthèse des performances :")
    print(f"{'Metrique':<15} | {'Erreurs':<8} | {'Taux'}")
    print("-" * 40)
    for k, v in errors.items():
        if k == "Conflit":
            print(f"{k:<15} | {v:<8} | (Pas de majorité)")
        else:
            print(f"{k:<15} | {v:<8} | {(v/total)*100:.1f} %")
    
    print("\nSignatures apprises (moyennes 4D) :")
    for f in levels:
        print(f"  f={f:.2f} : {np.round(means[f], 3)}")

if __name__ == "__main__":
    main()
