import numpy as np
from moteur_fluxons_2d import MoteurFluxons2D

def mesurer_tension_thermique(f, N, seed, T, gamma_dc=0.35):
    m = MoteurFluxons2D(N=N, frustration=f, seed=seed, gamma_dc=gamma_dc, temperature=T)
    m.appliquer_bruit_ci(0.01)
    
    # Relaxation
    m.integrer(n_steps=3000 if N==16 else 8000)
    
    # Mesure
    v_series = []
    for _ in range(300):
        m.integrer(n_steps=1)
        v_series.append(np.mean(m.v[:, -1] - m.v[:, 0]))
    return abs(np.mean(v_series))

def distance_relative(a, b):
    denom = 0.5 * (abs(a) + abs(b))
    return abs(a - b) / denom if denom >= 1e-12 else 0.0

def calculer_rho(vals_test, vals_ref):
    intra = [distance_relative(vals_test[i], vals_test[k]) for i in range(len(vals_test)) for k in range(i+1, len(vals_test))]
    inter = [distance_relative(a, b) for a in vals_test for b in vals_ref]
    return np.median(inter) / np.median(intra) if np.median(intra) > 1e-12 else float('inf')

def main():
    print("=== V19 : IMPACT DE LA TEMPÉRATURE SUR LE CODE-BARRES (N=32) ===")
    
    temperatures = [0.0, 0.005, 0.01, 0.02, 0.05]
    n_runs = 5 # Réduit pour que le test aille vite
    N = 32
    
    for T in temperatures:
        print(f"\n--- Température T = {T} ---")
        
        # Référence f = 0.25
        ref_vals = [mesurer_tension_thermique(0.25, N, seed=6000+i, T=T) for i in range(n_runs)]
        
        for f in [0.10, 0.40]:
            test_vals = [mesurer_tension_thermique(f, N, seed=7000+i, T=T) for i in range(n_runs)]
            rho = calculer_rho(test_vals, ref_vals)
            
            print(f"f={f:.2f} | Tension: {np.mean(test_vals):.3f} ± {np.std(test_vals):.3f} | rho vs 0.25: {rho:.2f}")

if __name__ == "__main__":
    main()
