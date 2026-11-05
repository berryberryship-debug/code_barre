import numpy as np
import matplotlib.pyplot as plt

# 1. Charger les résultats sauvegardés par test_v16_precision.py
# (allow_pickle=True est nécessaire car c'est un dictionnaire)
resultats = np.load('resultats_v16_N32.npy', allow_pickle=True).item()

# 2. Créer la figure
plt.figure(figsize=(10, 6))

# 3. Tracer une courbe pour chaque frustration (f)
for f, data in resultats.items():
    # Extraire les biais et les tensions moyennes
    biais = [d[0] for d in data]
    tensions = [abs(d[1]) for d in data] # Valeur absolue pour voir le décrochage
    
    # Tracer la ligne avec des points
    plt.plot(biais, tensions, marker='o', label=f'Frustration f = {f}')

# 4. Ajouter des détails visuels
plt.axhline(y=0.05, color='r', linestyle='--', label='Seuil arbitraire de décrochage')
plt.xlabel('Biais injecté (gamma_dc)', fontsize=12)
plt.ylabel('Tension aux bords |V|', fontsize=12)
plt.title('Courbe I-V : Transition du réseau de Josephson (N=32)', fontsize=14)
plt.legend()
plt.grid(True)

# 5. Sauvegarder l'image et l'afficher
plt.savefig('courbe_iv_v16.png', dpi=300)
print("Graphique sauvegardé dans 'courbe_iv_v16.png'")
plt.show()
