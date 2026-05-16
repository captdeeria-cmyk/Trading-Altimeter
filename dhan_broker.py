"""
dhan_broker.py — Trading Altimeter
Direct system integration hook into the dhanhq library framework.
"""

import os
import json
import datetime
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
PAPER_FILE = "paper_trades.json"

def get_dhan_connection():
    cid = os.getenv("DHAN_CLIENT_ID", "")
    tok = os.getenv("DHAN_ACCESS_TOKEN", "")
    if not cid or not tok:
        return None
    try:
        from dhanhq import dhanhq
        return dhanhq(cid, tok)
    except Exception:
        return None

def fetch_historical_candles(security_id, exchange_segment="NSE_EQ"):
    """Fetches lightning fast analytical structures from Dhan infrastructure."""
    dhan = get_dhan_connection()
    if not dhan:
        return pd.DataFrame()
        
    try:
        # Request daily historical framework
        res = dhan.get_historical_data(
            symbol=security_id,
            exchange_segment=exchange_segment,
            instrument_type="EQUITY",
            expiry_code=0,
            from_date="2024-05-16",
            to_date="2026-05-16",
            data_period="2" # Daily interval chart
        )
        if res and res.get('status') == 'success':
            raw = res.get('data', [])
            if not raw:
                return pd.DataFrame()
            df = pd.DataFrame(raw)
            df['Date'] = pd.to_datetime(df['start_time'])
            df.set_index('Date', inplace=True)
            df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
            return df
    except Exception:
        pass
    return pd.DataFrame()

def route_instant_trade(symbol, qty, side, paper_mode=True):
    """Executes trades or logs simulated orders natively."""
    price = 1500.00  # Fallback sample quote anchor value
    
    if paper_mode:
        trades = []
        if os.path.exists(PAPER_FILE):
            try:
                with open(PAPER_FILE, 'r') as f: trades = json.load(f)
            except: pass
        entry = {
            "symbol": symbol, "qty": qty, "transaction_type": side,
            "price": price, "timestamp": str(datetime.datetime.now())
        }
        trades.append(entry)
        with open(PAPER_FILE, 'w') as f: json.dump(trades, f, indent=4)
        return {"status": "SUCCESS", "msg": "Paper trade processed."}
    return {"status": "FAILED", "msg": "Live integration active; balance authorization required."}
