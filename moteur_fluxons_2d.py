import numpy as np

class MoteurFluxons2D:
    def __init__(self, N=16, frustration=0.25, seed=42, gamma_dc=0.0, temperature=0.0):
        self.N = N
        self.f = frustration
        self.rng = np.random.default_rng(seed)
        
        self.beta_c = 0.5
        self.gamma = 0.1
        self.gamma_dc = gamma_dc
        self.T = temperature # <--- Nouveau paramètre
        self.dt = 0.05
        
        self.phi = self.rng.uniform(-np.pi, np.pi, (N, N))
        self.v = np.zeros((N, N))
        
        # Jauge de Landau
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
        force[1:, :] -= jy
        force[:-1, :] += jy

        # Liaisons horizontales avec jauge
        dphi_x = phi[:, 1:] - phi[:, :-1] - self.A_x[:, :-1]
        dphi_x = (dphi_x + np.pi) % (2 * np.pi) - np.pi
        jx = np.sin(dphi_x)
        force[:, 1:] -= jx
        force[:, :-1] += jx
        
        # Injection DC aux bords
        if self.gamma_dc != 0:
            force[:, 0] += self.gamma_dc
            force[:, -1] -= self.gamma_dc
            
        # NOUVEAU : Ajout du bruit thermique (Théorème de Fluctuation-Dissipation)
        if self.T > 0:
            # L'amplitude du bruit dépend de la température et de la viscosité (gamma)
            sigma_bruit = np.sqrt(2 * self.gamma * self.T / self.dt)
            force += self.rng.normal(0, sigma_bruit, phi.shape)
            
        return force

    def integrer(self, n_steps=1000):
        for _ in range(n_steps):
            force = self._forces(self.phi)
            self.v += 0.5 * self.dt * (force - self.gamma * self.v)
            self.phi += self.dt * self.v
            force_new = self._forces(self.phi)
            self.v += 0.5 * self.dt * (force_new - self.gamma * self.v)
