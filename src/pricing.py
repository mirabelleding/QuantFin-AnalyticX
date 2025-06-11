import numpy as np
from scipy.stats import norm

"""
Parameters:
    S : float : Current stock price
    K : float : Strike price
    T : float : Time to maturity (in years)
    r : float : Risk-free rate
    sigma : float : Volatility
    option_type : str : 'call' or 'put'
    q : float : Dividend yield
"""


def black_scholes(S, K, T, r, sigma, option_type, q=0):
    for name, val in zip(['S', 'K', 'T', 'r', 'sigma', 'q'], [S, K, T, r, sigma, q]):
        if not isinstance(val, (int, float)):
            raise TypeError(f"{name} must be an int or float, got {type(val).__name__}")
    if option_type not in ['call', 'put']:
        raise ValueError("option_type must be 'call' or 'put'")

    if T <= 0:
        # Option has expired — intrinsic value only
        if option_type == 'call':
            return max(S - K, 0)
        else:
            return max(K - S, 0)

    if sigma <= 0:
        # Zero volatility — option is either in the money or not
        if option_type == 'call':
            return np.exp(-r * T) * max(S - K, 0)
        else:
            return np.exp(-r * T) * max(K - S, 0)

    # BSM formula
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)

    return price

