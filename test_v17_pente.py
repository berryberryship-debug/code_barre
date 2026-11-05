import numpy as np
from moteur_fluxons_2d import MoteurFluxons2D

def mesurer_courbe_iv(f, N, n_runs=5):
    biais_list = np.arange(0.20, 0.46, 0.02)
    V_moy = []
    
    for gd in biais_list:
        tensions = []
        for seed in range(6000, 6000 + n_runs):
            m = MoteurFluxons2D(N=N, frustration=f, seed=seed, gamma_dc=gd)
            m.appliquer_bruit_ci(0.01)
            
            # Relaxation (plus longue pour N=32)
            m.integrer(n_steps=3000 if N==16 else 8000)
            
            # Mesure
            v_series = []
            for _ in range(300):
                m.integrer(n_steps=1)
                v_series.append(np.mean(m.v[:, -1] - m.v[:, 0]))
            tensions.append(np.mean(v_series))
            
        V_moy.append(np.mean(tensions))
        
    return biais_list, np.abs(V_moy)

def extraire_pente_max(biais, tensions):
    pentes = np.diff(tensions) / np.diff(biais)
    return np.max(pentes)

def main():
    print("=== V17 : ROBUSTESSE DE LA SIGNATURE (N=16 vs N=32) ===")
    frustrations = [0.10, 0.25, 0.40]
    
    for N in [16, 32]:
        print(f"\n--- Analyse pour N = {N} ---")
        print("f      | Pente max (dV/dI) | Tension à I=0.35")
        
        for f in frustrations:
            biais, v_moy = mesurer_courbe_iv(f, N, n_runs=5)
            
            # Métrique 1 : Pente maximale
            pente = extraire_pente_max(biais, v_moy)
            
            # Métrique 2 : Tension à biais fixe 0.35
            idx_035 = np.argmin(np.abs(biais - 0.35))
            v_035 = v_moy[idx_035]
            
            print(f"{f:.2f}   | {pente:.3f}           | {v_035:.3f}")

if __name__ == "__main__":
    main()
