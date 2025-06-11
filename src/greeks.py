import numpy as np
from scipy.stats import norm


class GreekCalculator:
    def __init__(self, S, K, T, r, sigma, option_type):
        for name, val in zip(['S', 'K', 'T', 'r', 'sigma'], [S, K, T, r, sigma]):
            if not isinstance(val, (int, float)):
                raise TypeError(f"{name} must be a int or float, got {type(val).__name__}")
        if option_type not in ['call', 'put']:
            raise ValueError("option_type must be 'call' or 'put'")

        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.option_type = option_type
        self.d1, self.d2 = self._compute_d1_d2()

    def _compute_d1_d2(self):
        d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        return d1, d2

    def delta(self):
        return norm.cdf(self.d1) if self.option_type == 'call' else norm.cdf(self.d1) - 1

    def gamma(self):
        return norm.pdf(self.d1) / (self.S * self.sigma * np.sqrt(self.T))

    def vega(self):
        return self.S * norm.pdf(self.d1) * np.sqrt(self.T)

    def theta(self):
        first_term = - (self.S * norm.pdf(self.d1) * self.sigma) / (2 * np.sqrt(self.T))
        if self.option_type == 'call':
            return first_term - self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)
        else:
            return first_term + self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2)

    def rho(self):
        if self.option_type == 'call':
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2)
        else:
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2)

    def to_dict(self):
        return {
            'Delta (Δ)': self.delta(),
            'Gamma (Γ)': self.gamma(),
            'Vega (ν)': self.vega(),
            'Theta (θ)': self.theta(),
            'Rho (ρ)': self.rho()
        }