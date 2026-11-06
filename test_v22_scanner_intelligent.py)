import numpy as np
from moteur_fluxons_2d import MoteurFluxons2D

def mesurer_vecteur(f, N, seed, T, biais_list):
    V = []
    for gd in biais_list:
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
    print("=== V22: SMART SCANNER WITH THERMAL COMPENSATION ===")
    
    N = 32
    levels = [0.25, 0.30, 0.35]
    biais = [0.30, 0.36]
    
    # 1. Build the compensation map (Calibration at different temperatures)
    # In a real scenario, this is done once in the factory.
    print("\n1. Building calibration map (T=0.0 and T=0.05)...")
    # We map the vector (V0.30, V0.36) at T=0 and T=0.05
    map_cold = {}
    map_hot = {}
    
    for f in levels:
        vecs_cold = [mesurer_vecteur(f, N, 1000+i, T=0.0, biais_list=biais) for i in range(5)]
        map_cold[f] = np.mean(vecs_cold, axis=0)
        
        vecs_hot = [mesurer_vecteur(f, N, 2000+i, T=0.05, biais_list=biais) for i in range(5)]
        map_hot[f] = np.mean(vecs_hot, axis=0)
    
    # 2. Simulate Unknown Reads (at T=0.05, some noise)
    print("\n2. Testing Unknown reads (Target T=0.05)...")
    errors_naive = 0
    errors_smart = 0
    total = 0
    
    for f in levels:
        # 10 reads with noise
        reads = [mesurer_vecteur(f, N, 3000+i, T=0.05, biais_list=biais) for i in range(10)]
        for v_test in reads:
            total += 1
            
            # --- NAIVE SCANNER (1D) ---
            # Only uses V(0.30), compared to cold thresholds
            th_25_30 = (map_cold[0.25][0] + map_cold[0.30][0]) / 2
            th_30_35 = (map_cold[0.30][0] + map_cold[0.35][0]) / 2
            
            if v_test[0] < th_25_30: guess_naive = 0.25
            elif v_test[0] < th_30_35: guess_naive = 0.30
            else: guess_naive = 0.35
            if guess_naive != f: errors_naive += 1
            
            # --- SMART SCANNER (2D compensation) ---
            # The smart scanner "knows" the material is hot (T=0.05) 
            # and uses the 2D map to find the closest point in the HOT map.
            best_f = None
            min_dist = float('inf')
            for f_candidate in levels:
                target_point = map_hot[f_candidate]
                dist = np.linalg.norm(v_test - target_point) # Euclidean distance in 2D
                if dist < min_dist:
                    min_dist = dist
                    best_f = f_candidate
                    
            if best_f != f: errors_smart += 1

    print("\n3. Results")
    print(f"-> Error Rate (Naive 1D):       {(errors_naive/total)*100:.1f}%")
    print(f"-> Error Rate (Smart 2D Compensation): {(errors_smart/total)*100:.1f}%")
    
    if errors_smart == 0:
        print("-> SUCCESS: Thermal compensation completely eliminates errors!")

if __name__ == "__main__":
    main()
