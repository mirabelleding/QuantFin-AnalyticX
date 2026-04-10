# QuantFin-AnalyticX

An interactive web platform for financial option pricing, risk analytics, and portfolio simulation.

---

*Inspired by the Options and Futures elective course during my undergraduate studies, back when BSM and GBM functions were still calculated by hand.*


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Geometric Brownian Motion (GBM):**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; $dS_t = \mu S_t dt + \sigma S_t dW_t$

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Black–Scholes Formula (for a Call Option):**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; $C(S_t, t) = S_t N(d_1) - K e^{-r(T-t)} N(d_2)$


---

### Feature Functionalities
* **Option Chain Valuation:** Real-time pricing using the Black-Scholes model, datasource from yfinance.
* **Volatility Analysis:** Visualization of implied volatility surfaces.
* **Delta Hedging Simulator:** Stochastic simulation for testing hedging strategies.
* **Risk Dashboard:** Portfolio sensitivity tracking (Δ, Γ, Θ, ν, ρ) with PnL monitoring.
  
Hosted on streamlit: https://quantfin-analyticx.streamlit.app

