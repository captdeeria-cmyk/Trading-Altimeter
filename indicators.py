"""
indicators.py — Trading Altimeter
"""
import warnings
import logging
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HMA_LENGTH = 200          
NEAR_ZONE_PCT = 1.5       

def _wma(series: pd.Series, length: int) -> pd.Series:
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )

def compute_hma(close: pd.Series, length: int = HMA_LENGTH) -> pd.Series:
    if close.empty or len(close) < length:
        return pd.Series(np.nan, index=close.index)
    half = length // 2
    sqrt_len = int(np.floor(np.sqrt(length)))
    return _wma(2 * _wma(close, half) - _wma(close, length), sqrt_len)

def calculate_dhan_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or len(df) < 50: # Safe lower bounds boundary
        return df
    
    close = df["Close"]
    df["HMA_200"] = compute_hma(close, HMA_LENGTH)
    df["EMA_20"] = close.ewm(span=20, adjust=False).mean()
    df["EMA_50"] = close.ewm(span=50, adjust=False).mean()
    
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI_14"] = 100 - (100 / (1 + rs))
    
    df["MACD"] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    return df

def classify_dhan_signal(df: pd.DataFrame) -> dict:
    if df.empty or "HMA_200" not in df.columns or pd.isna(df["HMA_200"].iloc[-1]):
        return {"signal": "NEUTRAL", "hma_value": 0.0, "close_value": 0.0, "distance_pct": 0.0, "above_hma": False, "ltp": df["Close"].iloc[-1] if not df.empty else 0.0}

    curr = df.iloc[-1]
    prev = df.iloc[-2]

    hma_curr, close_curr = float(curr["HMA_200"]), float(curr["Close"])
    distance_pct = ((close_curr - hma_curr) / hma_curr) * 100
    above_hma = close_curr > hma_curr
    
    if not (prev["Close"] > prev["HMA_200"]) and above_hma:
        signal = "🚀 BULLISH BREAKOUT"
    elif (prev["Close"] > prev["HMA_200"]) and not above_hma:
        signal = "💀 BEARISH BREAKDOWN"
    elif abs(distance_pct) <= NEAR_ZONE_PCT:
        signal = "👀 APPROACHING"
    else:
        signal = "🚀 BULLISH TREND" if above_hma else "💀 BEARISH TREND"

    return {
        "signal": signal, "hma_value": hma_curr, "close_value": close_curr,
        "distance_pct": distance_pct, "above_hma": above_hma, "ltp": close_curr
    }
