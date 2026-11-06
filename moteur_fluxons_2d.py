import numpy as np


class MoteurFluxons2D:
    """
    Réseau Josephson 2D avec frustration, jauge de Landau,
    injection DC aux bords et thermostat de Langevin (schéma BBK).

    phi : phases des îlots, en radians.
    v   : dérivées temporelles des phases.
    """

    TWO_PI = 2.0 * np.pi

    def __init__(
        self,
        N=16,
        frustration=0.25,
        seed=42,
        gamma=0.1,
        gamma_dc=0.0,
        temperature=0.0,
        dt=0.05,
        periodic=True,
    ):
        if N < 2:
            raise ValueError("N doit être au moins 2.")
        if dt <= 0:
            raise ValueError("dt doit être positif.")
        if gamma < 0:
            raise ValueError("gamma doit être non négatif.")
        if temperature < 0:
            raise ValueError("temperature doit être non négative.")

        self.N = int(N)
        self.f = float(frustration)
        self.gamma = float(gamma)
        self.gamma_dc = float(gamma_dc)
        self.T = float(temperature)
        self.dt = float(dt)
        self.periodic = bool(periodic)

        self.rng = np.random.default_rng(seed)

        # Phases initiales et vitesses
        self.phi = self.rng.uniform(-np.pi, np.pi, (self.N, self.N))
        self.v = np.zeros((self.N, self.N), dtype=float)

        # Jauge de Landau : A_x(i, j) = -f * i
        # On stocke la jauge sur les liaisons horizontales (i -> i+1).
        rows = np.arange(self.N, dtype=float)[:, None]
        self.A_link_x = -self.f * np.broadcast_to(
            rows, (self.N, self.N - 1)
        ).copy()

        # Amplitude du bruit blanc pour la fluctuation-dissipation :
        # <eta(t) eta(t')> = 2 gamma T delta(t - t')
        self.sigma_noise = (
            np.sqrt(2.0 * self.gamma * self.T / self.dt)
            if self.T > 0.0
            else 0.0
        )

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    @staticmethod
    def _wrap(angle):
        """Ramène un angle dans [-pi, pi)."""
        return (angle + np.pi) % MoteurFluxons2D.TWO_PI - np.pi

    def appliquer_bruit_ci(self, sigma=0.0):
        """Ajoute un bruit initial sur les phases."""
        if sigma > 0:
            self.phi += self.rng.normal(0.0, sigma, self.phi.shape)
            self.phi = self._wrap(self.phi)

    # ------------------------------------------------------------------
    # Dynamique
    # ------------------------------------------------------------------

    def _forces_conservatives(self, phi):
        """
        Forces dérivant de l'énergie de Josephson :
        U = sum_links [1 - cos(delta phi - A)]
        """
        force = np.zeros_like(phi)

        # Liaisons horizontales : (i, j) -> (i, j + 1)
        dphi_x = self._wrap(phi[:, 1:] - phi[:, :-1] - self.A_link_x)
        jx = np.sin(dphi_x)

        force[:, :-1] += jx
        force[:, 1:] -= jx

        # Liaisons verticales : (i, j) -> (i + 1, j)
        if self.periodic:
            dphi_y = self._wrap(np.roll(phi, -1, axis=0) - phi)
            jy = np.sin(dphi_y)

            force += jy
            force -= np.roll(jy, 1, axis=0)
        else:
            dphi_y = self._wrap(phi[1:, :] - phi[:-1, :])
            jy = np.sin(dphi_y)

            force[:-1, :] += jy
            force[1:, :] -= jy

        return force

    def _forces_dc(self):
        """Injection DC aux bords gauche et droit."""
        force_dc = np.zeros_like(self.phi)
        if self.gamma_dc != 0.0:
            force_dc[:, 0] += self.gamma_dc
            force_dc[:, -1] -= self.gamma_dc
        return force_dc

    def _forces(self, phi, noise=None):
        """
        Forces totales.

        Le bruit est passé explicitement par l'intégrateur afin qu'il soit
        tiré une fois par demi-pas, comme l'exige le schéma BBK.
        """
        force = self._forces_conservatives(phi) + self._forces_dc()

        if noise is not None:
            force += noise

        return force

    def _draw_noise(self):
        """Tire un bruit thermique blanc indépendant."""
        if self.sigma_noise == 0.0:
            return None
        return self.rng.normal(
            0.0, self.sigma_noise, self.phi.shape
        )

    def integrer(self, n_steps=1000, record_every=0):
        """
        Intègre la dynamique pendant n_steps pas de temps.

        Schéma BBK / stochastic velocity-Verlet :

            v_half = v_n + dt/2 * [F(phi_n) - gamma v_n + eta_n]
            phi_{n+1} = phi_n + dt * v_half
            v_{n+1} = v_half + dt/2 * [F(phi_{n+1}) - gamma v_half + eta_{n+1/2}]

        Le bruit est tiré indépendamment aux deux demi-pas.
        """
        n_steps = int(n_steps)
        if n_steps < 0:
            raise ValueError("n_steps doit être non négatif.")

        history = [] if record_every else None
        dt = self.dt
        half_dt = 0.5 * dt

        for step in range(n_steps):
            # --- Premier demi-pas ---
            noise_1 = self._draw_noise()
            force_old = self._forces(self.phi, noise=noise_1)

            v_half = self.v + half_dt * (
                force_old - self.gamma * self.v
            )

            # --- Drift ---
            self.phi = self._wrap(self.phi + dt * v_half)

            # --- Second demi-pas ---
            noise_2 = self._draw_noise()
            force_new = self._forces(self.phi, noise=noise_2)

            self.v = v_half + half_dt * (
                force_new - self.gamma * v_half
            )

            if record_every and (step + 1) % record_every == 0:
                history.append(
                    {
                        "step": step + 1,
                        "phi": self.phi.copy(),
                        "v": self.v.copy(),
                        "energy": self.energie(),
                        "current_x": self.courant_moyen_x(),
                    }
                )

        return history

    # ------------------------------------------------------------------
    # Observables
    # ------------------------------------------------------------------

    def energie(self):
        """Énergie de Josephson totale, à une constante additive près."""
        dphi_x = self._wrap(
            self.phi[:, 1:] - self.phi[:, :-1] - self.A_link_x
        )
        energy = np.sum(1.0 - np.cos(dphi_x))

        if self.periodic:
            dphi_y = self._wrap(np.roll(self.phi, -1, axis=0) - self.phi)
        else:
            dphi_y = self._wrap(self.phi[1:, :] - self.phi[:-1, :])

        energy += np.sum(1.0 - np.cos(dphi_y))
        return float(energy)

    def courant_moyen_x(self):
        """
        Courant moyen horizontal, défini comme la moyenne de sin(delta phi - A).
        """
        dphi_x = self._wrap(
            self.phi[:, 1:] - self.phi[:, :-1] - self.A_link_x
        )
        return float(np.mean(np.sin(dphi_x)))

    def vorticités(self):
        """
        Calcule la vorticité plaquette par plaquette :
        somme des différences de phase autour de chaque cellule,
        corrigée par la jauge et divisée par 2 pi.
        """
        phi = self.phi

        if self.periodic:
            dphi_x = self._wrap(np.roll(phi, -1, axis=1) - phi - self.A_link_x)
            dphi_y = self._wrap(np.roll(phi, -1, axis=0) - phi)
            dphi_x_back = self._wrap(
                np.roll(phi, 1, axis=1) - phi + self.A_link_x
            )
            dphi_y_back = self._wrap(np.roll(phi, 1, axis=0) - phi)

            circulation = (
                dphi_x
                + dphi_y
                - dphi_x_back
                - dphi_y_back
            )
        else:
            raise NotImplementedError(
                "Vorticités non périodiques non implémentées."
            )

        return circulation / self.TWO_PI
