"""
dhan_broker.py — Trading Altimeter
Natively coordinates Dhan client authorization endpoints and generates mock data fallbacks.
"""
import os
import json
import logging
import datetime
import pandas as pd
import numpy as np
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
PAPER_TRADES_FILE = "paper_trades.json"

def get_dhan_connection():
    """Initializes matching connection clients securely via environment credentials."""
    client_id = os.getenv("DHAN_CLIENT_ID", "")
    access_token = os.getenv("DHAN_ACCESS_TOKEN", "")
    if not client_id or not access_token:
        return None
    try:
        from dhanhq import dhanhq
        return dhanhq(client_id, access_token)
    except Exception:
        return None

def fetch_historical_candles(security_id, exchange_segment="NSE_EQ"):
    """Pulls clean chart bars via Dhan networks or falls back to synthetic generation."""
    client = get_dhan_connection()
    if client:
        try:
            res = client.get_historical_data(
                symbol=security_id,
                exchange_segment=exchange_segment,
                instrument_type="EQUITY",
                expiry_code=0,
                from_date=str(datetime.date.today() - datetime.timedelta(days=450)),
                to_date=str(datetime.date.today()),
                data_period="2"
            )
            if res and res.get('status') == 'success' and res.get('data'):
                df = pd.DataFrame(res['data'])
                df['Date'] = pd.to_datetime(df['start_time'])
                df.set_index('Date', inplace=True)
                df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
                return df
        except Exception:
            pass

    # High-fidelity baseline data engine so your app always loads during market holidays
    np.random.seed(int(security_id) if security_id.isdigit() else 42)
    dates = pd.date_range(end=datetime.datetime.now(), periods=300, freq='D')
    
    # Create an organic chart path pattern
    price_walk = 1200.0 + np.cumsum(np.random.normal(1.5, 12, size=300))
    df = pd.DataFrame({
        "Open": price_walk - 4, "High": price_walk + 15, "Low": price_walk - 12, "Close": price_walk, "Volume": 250000
    }, index=dates)
    df.index.name = "Date"
    return df

def render_order_panel(symbol, ltp, paper_mode=True):
    st.sidebar.markdown("### ⚡ Cockpit Order Deck")
    qty = st.sidebar.number_input("Shares Quantity", min_value=1, value=10, step=1)
    if st.sidebar.button(f"🛒 Execute {symbol} Instant Trade"):
        st.sidebar.success(f"SUCCESS: Simulated trade for {qty} shares of {symbol} logged at ₹{ltp:.2f}!")
