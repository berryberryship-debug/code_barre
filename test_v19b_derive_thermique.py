import numpy as np
from moteur_fluxons_2d import MoteurFluxons2D

def mesurer_tension(f, N, seed, T, gamma_dc=0.35):
    m = MoteurFluxons2D(N=N, frustration=f, seed=seed, gamma_dc=gamma_dc, temperature=T)
    m.appliquer_bruit_ci(0.01)
    m.integrer(n_steps=8000)
    
    v_series = []
    for _ in range(300):
        m.integrer(n_steps=1)
        v_series.append(np.mean(m.v[:, -1] - m.v[:, 0]))
    return abs(np.mean(v_series))

def main():
    print("=== V19b: THERMAL DRIFT AND CLASSIFICATION ERROR (N=32) ===")
    
    N = 32
    n_runs = 10
    T_cal = 0.0      # Calibration temperature
    T_test = 0.05    # Hot material temperature
    
    # We test 3 close levels to see if they blend together
    levels = [0.25, 0.30, 0.35]
    
    # Step 1: Calibration at T_cal = 0.0
    print(f"\n1. Calibration at T = {T_cal} (10 seeds per level)")
    cal_data = {}
    for f in levels:
        vals = [mesurer_tension(f, N, seed=1000+i, T=T_cal) for i in range(n_runs)]
        cal_data[f] = {"mean": np.mean(vals), "std": np.std(vals)}
        print(f"  f={f:.2f} | Mean V: {cal_data[f]['mean']:.3f} +/- {cal_data[f]['std']:.3f}")

    # Step 2: Measurement of hot material at T_test = 0.05
    print(f"\n2. Measurement at T = {T_test} (10 seeds per level)")
    test_data = {}
    for f in levels:
        vals = [mesurer_tension(f, N, seed=2000+i, T=T_test) for i in range(n_runs)]
        test_data[f] = {"mean": np.mean(vals), "std": np.std(vals)}
        print(f"  f={f:.2f} | Mean V: {test_data[f]['mean']:.3f} +/- {test_data[f]['std']:.3f}")

    # Step 3: Naive Classification (using T=0 thresholds on T=0.05 data)
    print("\n3. Naive Scanner Error (Calibrated at T=0, reading at T=0.05)")
    # We find the middle point between calibration means to set the threshold
    thresh_25_30 = (cal_data[0.25]["mean"] + cal_data[0.30]["mean"]) / 2
    thresh_30_35 = (cal_data[0.30]["mean"] + cal_data[0.35]["mean"]) / 2
    
    errors = 0
    total_reads = 0
    
    # Simulate reading the hot material
    for f in levels:
        # We generate 100 reads for this level at T=0.05
        reads = [mesurer_tension(f, N, seed=3000+i, T=T_test) for i in range(100)]
        for v in reads:
            total_reads += 1
            # Scanner guesses based on T=0 thresholds
            if v < thresh_25_30: guess = 0.25
            elif v < thresh_30_35: guess = 0.30
            else: guess = 0.35
            
            if guess != f:
                errors += 1
                
    error_rate = (errors / total_reads) * 100
    print(f"-> Classification Error Rate: {error_rate:.1f}%")
    
    if error_rate > 5.0:
        print("-> WARNING: Thermal drift corrupts the barcode. Compensation needed.")
    else:
        print("-> ACCEPTABLE: Barcode is robust to this temperature shift.")

if __name__ == "__main__":
    main()
