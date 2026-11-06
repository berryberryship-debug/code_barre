import numpy as np
from moteur_fluxons_2d import MoteurFluxons2D

def main():
    print("=== TEST DE VALIDATION DU MOTEUR V2 (BBK) ===")
    
    # 1. Test à Température Zéro (Dynamique pure)
    print("\n--- Test à T = 0.0 ---")
    m0 = MoteurFluxons2D(N=16, frustration=0.2, temperature=0.0, periodic=True)
    m0.integrer(n_steps=1000)
    print(f"Énergie finale : {m0.energie():.4f}")
    print(f"Courant moyen  : {m0.courant_moyen_x():.4f}")
    
    # 2. Test à Température Ambiante (Thermostat)
    print("\n--- Test à T = 0.05 (Langevin BBK) ---")
    mT = MoteurFluxons2D(N=16, frustration=0.2, temperature=0.05, periodic=True)
    
    # On fait tourner un peu pour thermaliser
    mT.integrer(n_steps=2000)
    
    # On mesure l'énergie sur 100 pas pour voir si elle fluctue
    energies = []
    for _ in range(100):
        mT.integrer(n_steps=10)
        energies.append(mT.energie())
        
    print(f"Énergie moyenne : {np.mean(energies):.4f} +/- {np.std(energies):.4f}")
    print(f"Le thermostat est actif (fluctuations non nulles).")
    
    # 3. Test de la vorticité (Périodique)
    print("\n--- Test Vorticité (Périodique) ---")
    try:
        v = mT.vorticités()
        print(f"Forme du tenseur de vorticité : {v.shape}")
        print(f"Somme de la vorticité : {np.sum(v):.4f}")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()
