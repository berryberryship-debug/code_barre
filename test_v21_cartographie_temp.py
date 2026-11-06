import numpy as np
from moteur_fluxons_2d import MoteurFluxons2D

def cartographie_temperature():
    print("=== V21: THERMAL CARTOGRAPHY V(T) ===")
    
    N = 32
    f_ref = 0.30
    temperatures = np.linspace(0.0, 0.10, 11)  # 11 points (0.00 to 0.10)
    bias_list = [0.30, 0.36]
    n_seeds = 5

    resultats = {b: [] for b in bias_list}

    for T in temperatures:
        print(f"Measuring at T = {T:.2f}...")
        for gd in bias_list:
            v_runs = []
            for s in range(n_seeds):
                m = MoteurFluxons2D(N=N, frustration=f_ref, seed=5000 + s, gamma_dc=gd, temperature=T)
                m.appliquer_bruit_ci(0.01)
                m.integrer(n_steps=4000)
                
                v_series = []
                for _ in range(150):
                    m.integrer(n_steps=1)
                    v_series.append(np.mean(m.v[:, -1] - m.v[:, 0]))
                v_runs.append(abs(np.mean(v_series)))
            
            v_mean = np.mean(v_runs)
            v_std = np.std(v_runs)
            resultats[gd].append((v_mean, v_std))

    print("\n--- RESULTS FOR FIT ---")
    print("T\tV(0.30)\t\tV(0.36)")
    for idx, T in enumerate(temperatures):
        v30 = resultats[0.30][idx][0]
        v36 = resultats[0.36][idx][0]
        print(f"{T:.2f}\t{v30:.4f}\t\t{v36:.4f}")

if __name__ == "__main__":
    cartographie_temperature()
