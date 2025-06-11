import streamlit as st
import pandas as pd
from datetime import datetime
from src.utils import get_ticker_data, load_demo_option
from src.pricing import black_scholes
from src.greeks import GreekCalculator
import plotly.graph_objects as go


# highlight in-the-money cells
def highlight_itm(row, current_price, option_type):
    strike = row.name
    if option_type == "call" and strike < current_price:
        return ['background-color: #e6f7ff'] * len(row)
    elif option_type == "put" and strike > current_price:
        return ['background-color: #e6f7ff'] * len(row)
    else:
        return [''] * len(row)


# cache yfinance data for 1h
@st.cache_data(ttl=3600)
def get_option(ticker_input):
    return get_ticker_data(ticker_input)


st.set_page_config(page_title="Black-Scholes Option Chain Pricing Model", layout="centered")
st.title("Black-Scholes Option Chain Pricing Model")
st.write("Access option chain data for a selected stock ticker, featuring both market prices and "
         "theoretical Black Scholes values to identify potential pricing discrepancies.")

# Ticker Input
ticker_input = st.text_input(
    "Search a ticker",
    placeholder="e.g. AAPL, TSLA",
    max_chars=20,
    key="ticker_input"
)

r = st.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=100.00, value=5.00, step=0.01) / 100

if ticker_input:
    try:
        result = get_ticker_data(ticker_input)

        if result is None:
            raise ValueError("Ticker data is None.")

        ticker, history, all_expiries = result

        if history.empty:
            st.error("Ticker not found or no recent price data.")
        else:
            S = history["Close"].iloc[-1]
            st.markdown(f"### 💰 Current Price of {ticker_input}: ${S:.2f}")

    except Exception as e:
        st.warning(f"Error: {e}  \nLoading demo data instead.")

        ticker = load_demo_option()
        ticker_input = ticker.ticker
        all_expiries = ticker.option_chain.all_expiries()
        S = ticker.stock_price
        st.markdown(f"### 💰 Current Price of demo: ${S:.2f}")

    # Expiration selection
    default_expiries = all_expiries[:2]
    selected_expiries = st.multiselect("Select Expiration Dates to Load", all_expiries, default=default_expiries)

    all_options = []
    now = datetime.now()

    for expiry in selected_expiries:
        expiry_date = pd.to_datetime(expiry)
        T = (expiry_date - now).days / 365

        chain = ticker.option_chain(expiry)

        for opt_type, df in zip(["call", "put"], [chain.calls, chain.puts]):
            df = df.copy()
            df["OptionType"] = opt_type
            df["Expiry"] = expiry_date
            df["T"] = T
            df["BS Price"] = df.apply(
                lambda row: black_scholes(S, row["strike"], T, r, row["impliedVolatility"], opt_type),
                axis=1
                )
            all_options.append(df)

    full_chain = pd.concat(all_options, ignore_index=True)

        # Strike price filter
    st.markdown("#### 🔎 Filter Strike Price Range")
    min_strike = float(full_chain["strike"].min())
    max_strike = float(full_chain["strike"].max())
    strike_range = st.slider("Strike Range", min_strike, max_strike, (min_strike, max_strike))

    filtered = full_chain[
            (full_chain["strike"] >= strike_range[0]) &
            (full_chain["strike"] <= strike_range[1])
            ]

        # Option Chain Result Display
    st.subheader("📅 Option Chain Results")

    for expiry in sorted(filtered["Expiry"].unique()):
        with st.expander(f"📆 Expiry: {expiry.date()}"):
            subset = filtered[filtered["Expiry"] == expiry]

            calls_df = subset[subset["OptionType"] == "call"][
                    ["strike", "lastPrice", "BS Price", "impliedVolatility"]]
            puts_df = subset[subset["OptionType"] == "put"][
                    ["strike", "lastPrice", "BS Price", "impliedVolatility"]]

            calls_df.columns = puts_df.columns = ["Strike", "Market Price", "BS Price", "Implied Vol"]
            calls_df.set_index("Strike", inplace=True)
            puts_df.set_index("Strike", inplace=True)

            styled_calls = calls_df.style.apply(highlight_itm, current_price=S, option_type="call", axis=1).format({
                    "Market Price": "${:.2f}",
                    "BS Price": "${:.2f}",
                    "Implied Vol": "{:.2%}"
                })
            styled_puts = puts_df.style.apply(highlight_itm, current_price=S, option_type="put", axis=1).format({
                    "Market Price": "${:.2f}",
                    "BS Price": "${:.2f}",
                    "Implied Vol": "{:.2%}"
                })

            st.markdown(
                    """
                    <div style='
                        display: inline-block;
                        background-color: #e6f7ff;
                        border-left: 4px solid #5faad1;
                        padding: 0px 10px;
                        font-size: 0.85rem;
                        font-weight: 500;
                        margin-bottom: 0.5rem;
                        border-radius: 3px;
                    '>
                        *In The Money
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📈 Call Options")
                st.dataframe(styled_calls, use_container_width=True)
            with col2:
                st.markdown("#### 📉 Put Options")
                st.dataframe(styled_puts, use_container_width=True)

    # --- Volatility Surface Plot --
    st.markdown("---")
    st.markdown("#### Volatility Surface Plot")
    surface_df = filtered[["strike", "Expiry", "impliedVolatility"]].copy()
    surface_df["days_to_expiry"] = (surface_df["Expiry"] - datetime.now()).dt.days

    pivot = surface_df.pivot_table(index="days_to_expiry", columns="strike", values="impliedVolatility")

    pivot = pivot.sort_index(axis=0).sort_index(axis=1)
    with st.expander("This 3D surface shows how implied volatility changes by strike and expiry.", expanded=True):
        fig = go.Figure(data=[go.Surface(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            hovertemplate=
            'Strike: %{x}<br>' +
            'Days to Expiry: %{y}<br>' +
            'Implied Vol: %{z:.2%}<extra></extra>'
        )])

        fig.update_layout(
            title="",
            scene=dict(
                xaxis_title='Strike',
                yaxis_title='Days to Expiry',
                zaxis_title='Implied Volatility (%)'
            ),
            margin=dict(l=0, r=0, b=0, t=30)
        )

        st.plotly_chart(fig, use_container_width=True)

    # --- Analyze a specific option ---
    st.markdown("---")
    st.markdown("#### Analyze a Specific Option")
    unique_options = filtered[["strike", "OptionType", "Expiry"]].drop_duplicates()
    unique_options["label"] = unique_options.apply(
        lambda row: f"{ticker_input} {row['OptionType'].capitalize()} @ {row['strike']} ({row['Expiry'].date()})",
        axis=1)
    labels = ["Select an option..."] + list(unique_options["label"])
    selected_row = st.selectbox("Select an Option", labels)

    if selected_row != "Select an option...":
        chosen = unique_options[unique_options["label"] == selected_row].iloc[0]
        strike = chosen["strike"]
        option_type = chosen["OptionType"]
        expiry_date = chosen["Expiry"]
        T = (expiry_date - datetime.now()).days / 365

        # Retrieve implied vol from original DataFrame
        row_data = filtered[
            (filtered["strike"] == strike) &
            (filtered["OptionType"] == option_type) &
            (filtered["Expiry"] == expiry_date)
            ].iloc[0]

        sigma = row_data["impliedVolatility"]
        bs_price = black_scholes(S, strike, T, r, sigma, option_type)

        greeks = GreekCalculator(S, strike, T, r, sigma, option_type).to_dict()
        greeks_clean = {k: round(v, 4) for k, v in greeks.items()}

        with st.expander(f"{selected_row}", expanded=True):
            st.write(f"**Option Type:** {option_type.capitalize()}")
            st.write(f"**Strike:** {strike}")
            st.write(f"**Expiry:** {expiry_date.date()}")
            st.write(f"**Implied Volatility:** {sigma:.2%}")
            st.write(f"**Black-Scholes Price:** ${bs_price:.2f}")
            st.markdown("#### Greeks Summary")
            for greek, value in greeks_clean.items():
                st.markdown(f"**{greek}:** {value:.4f}")

else:
    st.info("Please enter a ticker symbol.")
