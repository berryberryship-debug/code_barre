import numpy as np

class MoteurFluxons2D:
    def __init__(self, N=16, frustration=0.25, seed=42, gamma_dc=0.0):
        self.N = N
        self.f = frustration
        self.rng = np.random.default_rng(seed)
        
        self.beta_c = 0.5
        self.gamma = 0.1
        self.gamma_dc = gamma_dc
        self.dt = 0.05
        
        self.phi = self.rng.uniform(-np.pi, np.pi, (N, N))
        self.v = np.zeros((N, N))
        
        # CORRECTION : Forme (N,N) pour A_x
        self.A_x = -self.f * np.arange(N)[:, None] * np.ones((1, N))

    def appliquer_bruit_ci(self, sigma=0.0):
        if sigma > 0:
            self.phi += self.rng.normal(0, sigma, self.phi.shape)

    def _forces(self, phi):
        force = np.zeros_like(phi)
        
        # Liaisons verticales
        dphi_y = phi[1:, :] - phi[:-1, :]
        dphi_y = (dphi_y + np.pi) % (2 * np.pi) - np.pi
        jy = np.sin(dphi_y)
        # CORRECTION : Signe pour minimiser l'énergie
        force[1:, :] -= jy
        force[:-1, :] += jy

        # Liaisons horizontales avec jauge
        dphi_x = phi[:, 1:] - phi[:, :-1] - self.A_x[:, :-1]
        dphi_x = (dphi_x + np.pi) % (2 * np.pi) - np.pi
        jx = np.sin(dphi_x)
        # CORRECTION : Signe
        force[:, 1:] -= jx
        force[:, :-1] += jx
        
        # Injection DC aux bords
        if self.gamma_dc != 0:
            force[:, 0] += self.gamma_dc
            force[:, -1] -= self.gamma_dc
            
        return force

    def calculer_vorticite(self):
        p = self.phi
        d1 = (p[1:, :-1] - p[:-1, :-1] + np.pi) % (2*np.pi) - np.pi
        d2 = (p[1:, 1:]  - p[1:, :-1] - self.A_x[:-1, 1:] + np.pi) % (2*np.pi) - np.pi
        d3 = (p[:-1, 1:] - p[1:, 1:]   + np.pi) % (2*np.pi) - np.pi
        d4 = (p[:-1, :-1]- p[:-1, 1:]  + self.A_x[:-1, :-1] + np.pi) % (2*np.pi) - np.pi
        
        total = d1 + d2 + d3 + d4
        return -np.round(total / (2 * np.pi))

    def integrer(self, n_steps=1000):
        # Retourne la vitesse moyenne (tension) sur les derniers pas
        v_series = []
        for t in range(n_steps):
            force = self._forces(self.phi)
            self.v += 0.5 * self.dt * (force - self.gamma * self.v)
            self.phi += self.dt * self.v
            force_new = self._forces(self.phi)
            self.v += 0.5 * self.dt * (force_new - self.gamma * self.v)
            
            if t >= n_steps - 200: # On garde les 200 derniers pas pour la moyenne
                v_series.append(np.mean(self.v))
                
        return float(np.mean(v_series))
