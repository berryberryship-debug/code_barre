import numpy as np
from moteur_fluxons_2d import MoteurFluxons2D

def mesurer_tension_fixe(f, N, seed, biais_fixe=0.35):
    m = MoteurFluxons2D(N=N, frustration=f, seed=seed, gamma_dc=biais_fixe)
    m.appliquer_bruit_ci(0.01)
    
    m.integrer(n_steps=3000 if N==16 else 8000)
    
    v_series = []
    for _ in range(300):
        m.integrer(n_steps=1)
        v_series.append(np.mean(m.v[:, -1] - m.v[:, 0]))
    return abs(np.mean(v_series))

def distance_relative(a, b):
    denom = 0.5 * (abs(a) + abs(b))
    return abs(a - b) / denom if denom >= 1e-12 else 0.0

def calculer_rho(vals_test, vals_ref):
    intra = [distance_relative(vals_test[i], vals_test[k]) 
             for i in range(len(vals_test)) for k in range(i+1, len(vals_test))]
    
    inter = [distance_relative(a, b) for a in vals_test for b in vals_ref]
    
    med_intra = np.median(intra)
    med_inter = np.median(inter)
    
    return med_inter / med_intra if med_intra > 1e-12 else float('inf')

def main():
    print("=== V18 : DISCRIMINATION (RHO) SUR LA TENSION À I=0.35 ===")
    
    frustrations = [0.10, 0.20, 0.25, 0.30, 0.40]
    
    for N in [16, 32]:
        print(f"\n--- Analyse pour N = {N} ---")
        
        ref_vals = [mesurer_tension_fixe(0.25, N, seed=6000+i) for i in range(10)]
        
        print("f      | Tension moy. (std) | rho vs f=0.25")
        
        for f in frustrations:
            test_vals = [mesurer_tension_fixe(f, N, seed=7000+i) for i in range(10)]
            
            if f == 0.25:
                rho = calculer_rho(ref_vals[:5], ref_vals[5:])
                note = "(Test intra)"
            else:
                rho = calculer_rho(test_vals, ref_vals)
                note = ""
                
            print(f"{f:.2f}   | {np.mean(test_vals):.3f} ({np.std(test_vals):.3f})   | {rho:.2f} {note}")

if __name__ == "__main__":
    main()
