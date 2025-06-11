import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.greeks import GreekCalculator
import plotly.graph_objects as go

st.set_page_config(layout="wide")

demo_portfolio = [
    {
        "option_type": "call",
        "strike": 100,
        "qty": 1,
        "expiry": (datetime.now() + timedelta(days=60)).date(),
        "implied_volatility": 0.25,
        "premium": 5.0
    },
    {
        "option_type": "put",
        "strike": 90,
        "qty": -1,
        "expiry": (datetime.now() + timedelta(days=60)).date(),
        "implied_volatility": 0.30,
        "premium": 4.0
    }
]

if "portfolio" not in st.session_state:
    st.session_state.portfolio = demo_portfolio

st.title("Portfolio Sensitivity Dashboard")
st.write("Evaluate the impact of market movements on portfolio performance by monitoring aggregated "
         "Greeks and net exposures. ")

# Layout with input on the left, output on the right
left, right = st.columns([1, 2])


with left:
    st.subheader("Construct Your Portfolio")
    col1, col2 = st.columns([1, 1])
    with col1:
        option_type = st.selectbox("Option Type", ["call", "put"])
    with col2:
        strike = st.number_input("Strike", value=100.0, step=5.0)

    col3, col4 = st.columns([1, 1])
    with col3:
        qty_input = st.number_input("Quantity", min_value=1, value=1, step=1)
    with col4:
        position_type = st.radio("Position", ["Long", "Short"], horizontal=True)

    qty = qty_input if position_type == "Long" else -qty_input
    expiry = st.date_input("Expiry Date")
    iv = st.slider("Implied Volatility (%)", min_value=5.0, max_value=200.0, value=25.0)
    premium = st.number_input("Premium (Option Cost)", value=5.0, step=0.5)

    button1, button2 = st.columns([1, 1])
    with button1:
        if st.button("Add to Portfolio"):
            st.session_state.portfolio.append({
                "option_type": option_type,
                "strike": strike,
                "qty": qty,
                "expiry": expiry,
                "implied_volatility": iv,
                "premium": premium
            })
    with button2:
        if st.button("Clear Portfolio"):
            st.session_state.portfolio = []


if st.session_state.portfolio:
    df_portfolio = pd.DataFrame(st.session_state.portfolio)

    # Display portfolio table
    with right:
        st.subheader("Current Portfolio")
        st.dataframe(df_portfolio)

    strikes = df_portfolio["strike"].astype(float)
    S_min = max(1, strikes.min() * 0.6)
    S_max = strikes.max() * 1.4
    S_range = np.linspace(S_min, S_max, 200)
    r = 0.05
    total_delta = np.zeros_like(S_range)
    total_gamma = np.zeros_like(S_range)
    total_vega = np.zeros_like(S_range)
    total_theta = np.zeros_like(S_range)
    total_rho = np.zeros_like(S_range)
    total_payoff = np.zeros_like(S_range)

    for option in st.session_state.portfolio:
        o_type = option["option_type"]
        K = float(option["strike"])
        q = int(option["qty"])
        sigma = float(option["implied_volatility"])
        prem = float(option["premium"])
        expiry_date = datetime.combine(option["expiry"], datetime.min.time())
        T = max((expiry_date - datetime.now()).days / 365, 1e-6)

        for i, S in enumerate(S_range):
            greek = GreekCalculator(S, K, T, r, sigma, o_type)
            intrinsic_value = max(S - K, 0) if o_type == "call" else max(K - S, 0)
            total_payoff[i] += q * (intrinsic_value - prem)
            total_delta[i] += q * greek.delta()
            total_gamma[i] += q * greek.gamma()
            total_vega[i] += q * greek.vega()
            total_theta[i] += q * greek.theta()
            total_rho[i] += q * greek.rho()

    # ===== Dashboard =====

    st.markdown("---")
    # st.subheader("Portfolio Sensitivity")
    with st.expander("Net PnL", expanded=True):

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=S_range,
            y=total_payoff,
            mode='lines',
            name='Net PnL',
            line=dict(color='mediumseagreen', width=3)
        ))

        fig.add_hline(y=0, line=dict(dash='dash', color='gray'))

        fig.update_layout(
            title="Net Profit and Loss vs. Stock Price at Expiry",
            xaxis_title="Stock Price at Expiry",
            yaxis_title="Profit / Loss",
            template="plotly_white",
            height=400,
            margin=dict(l=30, r=30, t=50, b=30),
        )

        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Greeks Exposure", expanded=True):
        greek_choice = st.radio(
            label="Greek Selection",
            options=["Delta", "Gamma", "Vega", "Theta", "Rho"],
            horizontal=True,
            label_visibility="collapsed"
        )
        greek_data = {
            "Delta": total_delta,
            "Gamma": total_gamma,
            "Vega": total_vega,
            "Theta": total_theta,
            "Rho": total_rho
        }

        color_map = {
            "Delta": "#1f77b4",
            "Gamma": "#ff7f0e",
            "Vega": "#17becf",
            "Theta": "#d62728",
            "Rho": "#9467bd"
        }

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=S_range,
            y=greek_data[greek_choice],
            mode='lines',
            name=greek_choice,
            line=dict(color=color_map[greek_choice], width=3)
        ))

        fig.add_hline(y=0, line=dict(dash='dash', color='gray'))

        fig.update_layout(
            title=f"{greek_choice} Exposure vs. Stock Price",
            xaxis_title="Stock Price",
            yaxis_title=f"{greek_choice} Exposure",
            template="plotly_white",
            height=400,
            margin=dict(l=30, r=30, t=50, b=30),
        )

        st.plotly_chart(fig, use_container_width=True)


else:
    st.info("Add at least one option to visualize Delta and Payoff.")