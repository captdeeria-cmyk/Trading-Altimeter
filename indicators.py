import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# Manual HMA calculation (No pandas_ta needed, won't crash Streamlit Cloud)
def calculate_hma(close, period=200):
    half_period = int(period / 2)
    sqrt_period = int(np.sqrt(period))
    wma_half = close.ewm(span=half_period, adjust=False).mean()
    wma_full = close.ewm(span=period, adjust=False).mean()
    raw_hma = (2 * wma_half) - wma_full
    hma = raw_hma.ewm(span=sqrt_period, adjust=False).mean()
    return hma

def fetch_ohlcv(symbol, period="1y", interval="1d"):
    end_date = datetime.datetime.now()
    if interval in ["3m", "5m", "15m", "30m", "60m", "1m"]:
        # yfinance strict rule: Intraday max period is 60 days
        start_date = end_date - datetime.timedelta(days=60)
        period = f"{(end_date - start_date).days}d" 
    df = yf.download(symbol, start=period, end=end_date, interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
    if df.empty: return pd.DataFrame()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df.dropna()

def add_indicators(df):
    if df.empty: return df
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["HMA_200"] = calculate_hma(df["Close"], 200)
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0.0)).fillna(0)
    loss = (-delta.where(delta < 0, 0.0)).fillna(0)
    avg_gain = gain.ewm(comspan=14, adjust=False).mean()
    avg_loss = loss.ewm(comspan=14, adjust=False).mean()
    rs = avg_gain / avg_loss
    df["RSI_14"] = 100 - (100 / (1 + rs))
    ema_12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema_12 - ema_26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    return df

def classify_hma_signal(df):
    if df.empty or "HMA_200" not in df: return {"signal": "N/A", "hma_value": 0, "distance_pct": 0, "above_hma": False, "last_date": "N/A"}
    df_clean = df.dropna(subset=["HMA_200", "Close"]).copy()
    if len(df_clean) < 2: return {"signal": "N/A", "hma_value": 0, "distance_pct": 0, "above_hma": False, "last_date": "N/A"}
    last = df_clean.iloc[-1]
    prev = df_clean.iloc[-2]
    hma_val = last["HMA_200"]
    dist = ((last["Close"] - hma_val) / hma_val) * 100
    above = last["Close"] > hma_val
    
    if prev["Close"] <= prev["HMA_200"] and last["Close"] > hma_val: signal = "BULLISH"
    elif prev["Close"] >= prev["HMA_200"] and last["Close"] < hma_val: signal = "BEARISH"
    elif abs(dist) <= 1.5: signal = "APPROACHING"
    else: signal = "NEUTRAL"
    return {"signal": signal, "hma_value": hma_val, "distance_pct": dist, "above_hma": above, "last_date": str(last.name.date())}

def fetch_live_quote(symbol):
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="2d")
        if hist.empty: return {"symbol": symbol.replace(".NS",""), "ltp": 0, "change_pct": 0}
        ltp = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2]
        return {"symbol": symbol.replace(".NS",""), "ltp": ltp, "change_pct": ((ltp - prev_close)/prev_close)*100}
    except: return {"symbol": symbol.replace(".NS",""), "ltp": 0, "change_pct": 0}

def batch_hma_status(symbol): return {**fetch_live_quote(symbol), **classify_hma_signal(add_indicators(fetch_ohlcv(symbol, period="1y")))}
