import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

st.set_page_config(page_title="Delta Hedging Simulator", layout="centered")

st.title("Delta Hedging Strategy Simulation")
st.write(
    "This simulation models a **dynamic delta hedging strategy**, where the position in the underlying asset "
    "is rebalanced at each time step to match the Black-Scholes delta. This minimizes market exposure and "
    "aims to replicate the theoretical option payoff over time."
)

# --- User Inputs ---
st.subheader("Simulation Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    S0 = st.number_input("Initial Stock Price (S₀)", value=100.0)
with col2:
    mu = st.number_input("Expected Return (μ)", value=0.05)
with col3:
    sigma = st.number_input("Volatility (σ)", value=0.2)

col4, col5, col6 = st.columns(3)
with col4:
    option_type = st.selectbox("Option Type", ["call", "put"])
with col5:
    strike = st.number_input("Option Strike", value=100.0)
with col6:
    premium = st.number_input("Premium Paid", value=5.0)

col7, col8, col9 = st.columns(3)
with col7:
    T_input = st.text_input("Time to Maturity (years)", "1.0")
    T = float(T_input) if T_input.replace('.', '', 1).isdigit() else 1.0
with col8:
    qty = st.number_input("Quantity", value=1, step=1)
with col9:
    r = st.number_input("Risk-Free Rate (%)", value=5.0) / 100

N = st.slider("Number of Time Steps", min_value=10, max_value=500, value=252)
M = st.slider("Number of Simulations", min_value=100, max_value=1000, value=300)


# --- Black-Scholes Delta ---
def bs_delta(S, K, T, r, sigma, option_type):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return norm.cdf(d1) if option_type == "call" else -norm.cdf(-d1)

# --- Run Simulation ---
if st.button("Run Simulation"):
    dt = T / N
    t_vals = np.linspace(0, T, N + 1)

    dW = np.random.normal(0, np.sqrt(dt), size=(M, N))
    W = np.cumsum(dW, axis=1)
    W = np.concatenate([np.zeros((M, 1)), W], axis=1)
    S_paths = S0 * np.exp((mu - 0.5 * sigma**2) * t_vals + sigma * W)

    pnl_paths = []
    stock_paths = []
    delta_paths = []

    for path in S_paths:
        cash_account = 0
        delta_prev = 0
        deltas = []
        stock_track = []

        for i in range(N):
            S_t = path[i]
            tau = T - i * dt
            if tau <= 0:
                break
            delta = bs_delta(S_t, strike, tau, r, sigma, option_type)
            d_delta = delta - delta_prev
            cash_account -= d_delta * S_t
            cash_account *= np.exp(r * dt)
            delta_prev = delta

            deltas.append(delta)
            stock_track.append(S_t)

        S_T = path[-1]
        payoff = max(S_T - strike, 0) if option_type == "call" else max(strike - S_T, 0)
        hedge_value = delta_prev * S_T + cash_account
        pnl = (hedge_value - payoff) * qty - premium * qty

        pnl_paths.append(pnl)
        stock_paths.append(stock_track)
        delta_paths.append(deltas)

    # Save to session state
    st.session_state['t_vals'] = t_vals
    st.session_state['stock_paths'] = stock_paths
    st.session_state['delta_paths'] = delta_paths
    st.session_state['pnl_paths'] = pnl_paths
    st.session_state['sim_ran'] = True

# --- Visualizations ---
if st.session_state.get('sim_ran', False):
    t_vals = st.session_state['t_vals']
    stock_paths = st.session_state['stock_paths']
    delta_paths = st.session_state['delta_paths']
    pnl_paths = st.session_state['pnl_paths']

    # --- Stock Price Paths ---
    with st.expander("Stock Price Over Time", expanded=True):
        view_option = st.radio("Viewing Mode", options=["Single Path", "Multiple Paths"], horizontal=True)

        fig_price = go.Figure()
        if view_option == "Single Path":
            S_path = stock_paths[0]
            fig_price.add_trace(go.Scatter(
                x=t_vals[:len(S_path)],
                y=S_path,
                mode='lines',
                line=dict(color="orange", width=2.5)
            ))
            fig_price.update_layout(title="Simulated Stock Price Over Time (1 Path)")
        else:
            for i, path in enumerate(stock_paths[:20]):
                fig_price.add_trace(go.Scatter(
                    x=t_vals[:len(path)],
                    y=path,
                    mode='lines',
                    line=dict(width=1, color="orange"),
                    showlegend=False
                ))
            fig_price.update_layout(title="Simulated Stock Price Paths Over Time (Multiple Paths)")

        fig_price.update_layout(
            xaxis_title="Time (Years)",
            yaxis_title="Stock Price",
            template='plotly_white',
            margin=dict(l=30, r=30, t=50, b=30),
            font=dict(family="Arial", size=14),
            height=400
        )
        st.plotly_chart(fig_price, use_container_width=True)

    # --- Hedging PnL Distribution ---
    with st.expander("Hedging PnL", expanded=True):
        mean_pnl = np.mean(pnl_paths)
        fig_pnl = go.Figure()
        fig_pnl.add_trace(go.Histogram(
            x=pnl_paths,
            nbinsx=50,
            name="PnL",
            marker_color="steelblue",
            opacity=0.75
        ))
        fig_pnl.add_vline(
            x=mean_pnl,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean PnL: ${mean_pnl:.2f}",
            annotation_position="top right"
        )
        fig_pnl.update_layout(
            title="Net Profit and Loss Distribution",
            xaxis_title="Hedging PnL",
            yaxis_title="Frequency",
            template="plotly_white",
            margin=dict(l=30, r=30, t=50, b=30)
        )
        st.plotly_chart(fig_pnl, use_container_width=True)

    # --- Delta Over Time ---
    with st.expander("Delta Over Time", expanded=True):
        deltas = delta_paths[0]
        fig_delta = go.Figure()
        fig_delta.add_trace(go.Scatter(
            x=t_vals[:len(deltas)],
            y=deltas,
            mode='lines',
            name='Delta',
            line=dict(color="cadetblue")
        ))
        fig_delta.update_layout(
            title="Delta Exposure vs. Time",
            xaxis_title="Time (Years)",
            yaxis_title="Delta",
            template='plotly_white',
            margin=dict(l=30, r=30, t=50, b=30)
        )
        st.plotly_chart(fig_delta, use_container_width=True)