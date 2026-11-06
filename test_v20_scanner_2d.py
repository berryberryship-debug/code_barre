import numpy as np
from moteur_fluxons_2d import MoteurFluxons2D

def mesurer_vecteur_2d(f, N, seed, T):
    """Lit la tension à deux biais (0.30 et 0.36) pour un matériau donné."""
    V = []
    for gd in [0.30, 0.36]:
        m = MoteurFluxons2D(N=N, frustration=f, seed=seed, gamma_dc=gd, temperature=T)
        m.appliquer_bruit_ci(0.01)
        m.integrer(n_steps=4000) 
        
        v_series = []
        for _ in range(150):
            m.integrer(n_steps=1)
            v_series.append(np.mean(m.v[:, -1] - m.v[:, 0]))
        V.append(abs(np.mean(v_series)))
    return np.array(V)

def main():
    print("=== V20: 2D SCANNER (RATIOMETRIC MEASUREMENT) ===")
    
    N = 32
    levels = [0.25, 0.30, 0.35]
    T_cal = 0.0
    T_test = 0.05
    
    # 1. Calibration
    print(f"\n1. Calibration (T={T_cal})")
    cal_vecs = {}
    for f in levels:
        vecs = [mesurer_vecteur_2d(f, N, seed=1000+i, T=T_cal) for i in range(5)]
        cal_vecs[f] = np.mean(vecs, axis=0)
        print(f"  f={f:.2f} | V(0.30)={cal_vecs[f][0]:.3f} | V(0.36)={cal_vecs[f][1]:.3f}")

    # 2. Mesure à chaud
    print(f"\n2. Measurement (T={T_test})")
    test_vecs = {}
    for f in levels:
        vecs = [mesurer_vecteur_2d(f, N, seed=2000+i, T=T_test) for i in range(5)]
        test_vecs[f] = np.mean(vecs, axis=0)
        print(f"  f={f:.2f} | V(0.30)={test_vecs[f][0]:.3f} | V(0.36)={test_vecs[f][1]:.3f}")

    # 3. Classification
    print(f"\n3. Classification (Simulating 10 reads per level)")
    
    errors_naive = 0
    errors_ratio = 0
    total = 0
    
    for f in levels:
        reads = [mesurer_vecteur_2d(f, N, seed=3000+i, T=T_test) for i in range(10)]
        for v_test in reads:
            total += 1
            
            # METHODE A : Scanner Naïf (1D)
            th_25_30 = (cal_vecs[0.25][0] + cal_vecs[0.30][0]) / 2
            th_30_35 = (cal_vecs[0.30][0] + cal_vecs[0.35][0]) / 2
            
            if v_test[0] < th_25_30: guess_naive = 0.25
            elif v_test[0] < th_30_35: guess_naive = 0.30
            else: guess_naive = 0.35
            if guess_naive != f: errors_naive += 1
            
            # METHODE B : Scanner Ratiométrique (2D)
            ratio_test = v_test[1] / v_test[0] if v_test[0] > 0.01 else 0
            
            r_25 = cal_vecs[0.25][1] / cal_vecs[0.25][0]
            r_30 = cal_vecs[0.30][1] / cal_vecs[0.30][0]
            r_35 = cal_vecs[0.35][1] / cal_vecs[0.35][0]
            
            th_r_25_30 = (r_25 + r_30) / 2
            th_r_30_35 = (r_30 + r_35) / 2
            
            if ratio_test < th_r_25_30: guess_ratio = 0.25
            elif ratio_test < th_r_30_35: guess_ratio = 0.30
            else: guess_ratio = 0.35
            if guess_ratio != f: errors_ratio += 1

    print(f"-> Error Rate (Naive 1D):      {(errors_naive/total)*100:.1f}%")
    print(f"-> Error Rate (Ratiometric 2D): {(errors_ratio/total)*100:.1f}%")

if __name__ == "__main__":
    main()
