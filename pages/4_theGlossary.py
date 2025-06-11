import streamlit as st


st.set_page_config(page_title="The Glossary", layout="centered")
st.title("theGlossary")

# Option Basics
st.markdown("---")
st.markdown("#### Option Basics")
st.markdown("""
- **Call/Put Option**: Right (but not obligation) to **buy/sell** the underlying asset at a specific price before or at expiration.
- **Strike Price (K)**: Price at which the option can be exercised.
- **Expiry Date**: The date the option expires and becomes invalid.
- **Quantity**: Number of option contracts.
- **Position (Long/Short)**: Long = buyer/holder; Short = seller/writer.
""")

# Market Inputs
st.markdown("---")
st.markdown("#### Market Inputs")
st.markdown("""
- **Underlying Price (S₀)**: Current market price of the asset.
- **Implied Volatility (σ)**: Market expectation of future volatility, implied by option prices.
- **Risk-Free Rate (r)**: Yield on a zero-risk investment (e.g., government bonds).
- **Expected Return (μ)**: Anticipated asset return used in simulations.
""")

# Black-Scholes
st.markdown("---")
st.markdown("#### Option Valuation: Black-Scholes Model")
st.markdown("The Black-Scholes Model is used in the **Option Chain Pricing Model** and **Black Scholes Calculator** "
            "to compute the theoretical price and Greeks for European options under standard assumptions (constant "
            "volatility, no dividends, etc.)")
st.caption("The Black-Scholes forumla:")
st.latex(r"C = N(d_1) \cdot S_t - N(d_2) \cdot K e^{-rt}")
st.latex(r"d_1 = \frac{\ln(S_t / K) + \left(r + \frac{\sigma^2}{2} \right)t}{\sigma \sqrt{t}}")
st.latex(r"d_2 = d_1 - \sigma \sqrt{t}")
st.markdown("""
**Where:**

C = call option price  
N = CDF of the normal distribution  
Sₜ = spot price of an asset  
K = strike price  
r = risk-free interest rate  
t = time to maturity  
σ = volatility of the underlying asset  
""")


# GBM
st.markdown("---")
st.markdown("#### Monte Carlo Price Simulation: GBM")
st.markdown("Monte Carlo simulation models the probabilistic evolution of asset prices by generating multiple random "
            "paths from a stochastic process. In finance, prices are often assumed to follow "
            "**Geometric Brownian Motion (GBM)**, which captures both drift and volatility in returns.")
st.caption("The GBM Model:")
st.latex(r"S_{t+\Delta t} = S_t \cdot \exp\left[\left(\mu - \frac{1}{2}\sigma^2\right)\Delta t + \sigma \sqrt{\Delta t} \cdot Z\right]")
st.markdown("""
**Where:**

Sₜ = asset price at time t  
μ = expected rate of return of the asset  
σ = volatility of the asset  
Δt = length of the time interval  
Z = standard normal random variable, Z~N(0, 1)
""")


# Greeks
st.markdown("---")
st.markdown("#### Greeks")
st.markdown("The Greeks are derived from the Black-Scholes pricing formula using partial differentiation. "
            "Each Greek represents the rate of change of the option’s value with respect to a specific input "
            "variable. ")
st.markdown("- **Delta (Δ)**∂C⁄∂S: Sensitivity of option price to changes in underlying asset price.")
st.markdown("- **Gamma (Γ)**: Sensitivity of delta to changes in underlying asset price.")
st.markdown("- **Theta (Θ)**: Sensitivity of option price to time decay.")
st.markdown("- **Vega (ν)**: Sensitivity of option price to changes in implied volatility.")
st.markdown("- **Rho (ρ)**: Sensitivity of option price to changes in interest rates.")


st.markdown("---")