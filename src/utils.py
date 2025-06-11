import yfinance as yf
from types import SimpleNamespace
from datetime import datetime, timedelta
import json
import os
import pandas as pd
import requests


def get_ticker_data(ticker_input):
    # Attempt yfinance first
    try:
        ticker = yf.Ticker(ticker_input)
        history = ticker.history(period="5d")
        expiries = ticker.options

        if history.empty or not expiries:
            raise ValueError("yFinance returned empty history or no expiries")

        return ticker, history, expiries

    except Exception as e_yf:
        print(f"[yfinance error] {e_yf}")

    # Attempt API fallback
    try:
        url = f"https://option-backend-api.onrender.com/option_data?ticker={ticker_input}"
        res = requests.get(url)
        if res.status_code != 200:
            raise ValueError(f"API status code {res.status_code}")

        data = res.json()
        if not all(k in data for k in ["price", "expires"]):
            raise ValueError("Missing keys in API response")

        # Build dummy replacements
        class DummyTicker:
            def __init__(self):
                self.ticker = ticker_input
                self.stock_price = data["price"]
                self.option_chain = type("Chain", (), {"all_expiries": lambda: data["expires"]})()

        dummy_history = pd.DataFrame({
            "Close": [data["price"]]
        })

        return DummyTicker(), dummy_history, data["expires"]

    except Exception as e_api:
        print(f"[API fallback error] {e_api}")
        raise RuntimeError(f"Both yFinance and API failed: {e_api}")


class OptionChain:
    def __init__(self, option_data, reference_date=None):
        self.reference_date = reference_date or datetime.today().date()
        self.expiries = {}

        for label, contracts in option_data.items():
            if label.startswith("today + "):
                days = int(label.split("+")[1].strip())
                actual_date = self.reference_date + timedelta(days=days)
                date_key = str(actual_date)
            else:
                date_key = label

            calls_df = pd.DataFrame(contracts["calls"])
            puts_df = pd.DataFrame(contracts["puts"])

            for df in [calls_df, puts_df]:
                df.rename(columns={
                    "Strike": "strike",
                    "Implied Volatility": "impliedVolatility",
                    "Last Price": "lastPrice"
                }, inplace=True)

                if "impliedVolatility" in df.columns and df["impliedVolatility"].dtype == object:
                    df["impliedVolatility"] = df["impliedVolatility"].str.rstrip('%').astype(float) / 100

            self.expiries[date_key] = SimpleNamespace(
                calls=calls_df,
                puts=puts_df
            )

    def __call__(self, expiry):
        expiry_str = expiry.strftime('%Y-%m-%d') if isinstance(expiry, datetime) else str(expiry)
        return self.expiries[expiry_str]

    def all_expiries(self):
        return list(self.expiries.keys())

    def __getitem__(self, expiry):
        return self.__call__(expiry)


class Ticker:
    def __init__(self, data):
        self.ticker = data["ticker"]
        self.stock_price = data["stock_price"]
        self.option_chain = OptionChain(data["option_chain"])


current_dir = os.path.dirname(__file__)
json_path = os.path.join(current_dir, "..", "demo_data", "demo_option.json")


def load_demo_option(path=json_path, reference_date=None):
    with open(path, "r") as f:
        data = json.load(f)
    return Ticker(data)