import streamlit as st
from src.pricing import black_scholes
from src.greeks import GreekCalculator

st.set_page_config(page_title="Black Scholes Calculator", layout="centered")
st.title("Black-Scholes Calculator")
st.write("Calculate fair value and Greeks for a European option.")

# -- Input Section on Main Page --
st.markdown("### Input Parameters")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    S = st.number_input("Stock Price (S)", value=100.0, step=0.5)
    K = st.number_input("Strike Price (K)", value=105.0, step=0.5)

    # Time to maturity & time unit selection
    col_tm, col_unit = st.columns([2, 1])
    with col_tm:
        time_value = st.number_input("Time to Maturity", value=1, min_value=0, step=1)
    with col_unit:
        time_unit = st.selectbox("Unit", ["Years", "Months", "Days"])

with row1_col2:
    r = st.number_input("Risk-Free Rate (r)", value=0.05)
    sigma = st.number_input("Volatility (σ)", value=0.2)
    div = st.number_input("Dividend Yield (%)", value=0.0)


# Convert time to years
if time_unit == "Years":
    T = time_value
elif time_unit == "Months":
    T = time_value / 12
else:  # Days
    T = time_value / 365

# -- Calculation --
call_price = black_scholes(S, K, T, r, sigma, option_type='call', q=div)
put_price  = black_scholes(S, K, T, r, sigma, option_type='put',  q=div)
call_greeks = GreekCalculator(S, K, T, r, sigma, option_type='call')
put_greeks  = GreekCalculator(S, K, T, r, sigma, option_type='put')

st.markdown("---")
# -- Output Section --
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style="line-height: 1.6">
        <h4>📈 Call Option Value: ${call_price:.4f}</h4>
        <p>Delta: {call_greeks.delta():.4f}</p>
        <p>Gamma: {call_greeks.gamma():.4f}</p>
        <p>Theta: {call_greeks.theta():.4f}</p>
        <p>Vega: {call_greeks.vega():.4f}</p>
        <p>Rho: {call_greeks.rho():.4f}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="line-height: 1.6">
        <h4>📉 Put Option Value: ${put_price:.4f}</h4>
        <p>Delta: {put_greeks.delta():.4f}</p>
        <p>Gamma: {put_greeks.gamma():.4f}</p>
        <p>Theta: {put_greeks.theta():.4f}</p>
        <p>Vega: {put_greeks.vega():.4f}</p>
        <p>Rho: {put_greeks.rho():.4f}</p>
    </div>
    """, unsafe_allow_html=True)