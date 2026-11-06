import numpy as np
from moteur_fluxons_2d import MoteurFluxons2D

def mesurer_vecteur(f, N, seed, T, biais_list):
    V = []
    for gd in biais_list:
        m = MoteurFluxons2D(N=N, frustration=f, seed=seed, gamma_dc=gd, temperature=T)
        m.appliquer_bruit_ci(0.01)
        m.integrer(n_steps=4000)  # Relaxation
        
        v_series = []
        # Augmentation du temps de mesure a 500 pas (au lieu de 150)
        for _ in range(500): 
            m.integrer(n_steps=1)
            v_series.append(np.mean(m.v[:, -1] - m.v[:, 0]))
        V.append(abs(np.mean(v_series)))
    return np.array(V)

def dist_maha_diag(x, mu, cov):
    diff = x - mu
    return np.sum((diff**2) / np.diag(cov))

def main():
    print("=== V28: RIGOROUS THERMAL CROSS-TEST ===")
    
    N = 32
    levels = [0.25, 0.30, 0.35]
    biais = [0.24, 0.30, 0.36] # 0.42 removed
    T_cal = 0.0
    T_test = 0.05
    n_calib = 50   # Increased from 15
    n_tests = 40   # Increased from 10 (Total 120 test reads)
    
    # 1. Calibration (Cold)
    print(f"\n1. Calibration at T={T_cal} (N={n_calib} seeds, measure=500 steps)...")
    means = {}
    covs = {}
    
    for f in levels:
        vecs = np.array([mesurer_vecteur(f, N, seed=1000+i, T=T_cal, biais_list=biais) for i in range(n_calib)])
        means[f] = np.mean(vecs, axis=0)
        covs[f] = np.cov(vecs, rowvar=False) + np.eye(3) * 1e-6
        print(f"  Signature learned for f={f:.2f}")

    # 2. Test (Hot)
    print(f"\n2. Blind Test at T={T_test} ({n_tests} reads per level)...")
    errors_naive = 0
    errors_diag = 0
    total = 0
    
    for f in levels:
        tests = [mesurer_vecteur(f, N, seed=3000+i, T=T_test, biais_list=biais) for i in range(n_tests)]
        for v_test in tests:
            total += 1
            
            # Naive 1D (using only biais 0.30)
            th_25_30 = (means[0.25][1] + means[0.30][1]) / 2
            th_30_35 = (means[0.30][1] + means[0.35][1]) / 2
            if v_test[1] < th_25_30: guess_naive = 0.25
            elif v_test[1] < th_30_35: guess_naive = 0.30
            else: guess_naive = 0.35
            if guess_naive != f: errors_naive += 1
            
            # MahaDiag 3D
            scores = {cand: dist_maha_diag(v_test, means[cand], covs[cand]) for cand in levels}
            best_diag = min(scores, key=scores.get)
            if best_diag != f: errors_diag += 1

    # 3. Results with Confidence Intervals (95%)
    def get_ic(err, n):
        p = err / n
        margin = 1.96 * np.sqrt((p * (1 - p)) / n)
        return (max(0, p - margin) * 100, min(1, p + margin) * 100)

    err_naive = (errors_naive / total) * 100
    err_diag = (errors_diag / total) * 100
    ic_naive = get_ic(errors_naive, total)
    ic_diag = get_ic(errors_diag, total)

    print("\n3. Performance Synthesis (T_cal=0.0 -> T_test=0.05) :")
    print(f"-> Error Rate (Naive 1D):        {err_naive:.1f} %  (IC 95%: {ic_naive[0]:.1f} - {ic_naive[1]:.1f} %)")
    print(f"-> Error Rate (MahaDiag 3D):     {err_diag:.1f} %  (IC 95%: {ic_diag[0]:.1f} - {ic_diag[1]:.1f} %)")

if __name__ == "__main__":
    main()
