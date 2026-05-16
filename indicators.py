"""
indicators.py — Trading Altimeter
"""
import warnings
import logging
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.WARNING)

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
    wma_half = _wma(close, half)
    wma_full = _wma(close, length)
    raw = 2 * wma_half - wma_full
    return _wma(raw, sqrt_len)

def calculate_dhan_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or len(df) < HMA_LENGTH:
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
    
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    return df

def classify_dhan_signal(df: pd.DataFrame) -> dict:
    if df.empty or "HMA_200" not in df.columns:
        return _empty_signal()

    recent = df.dropna(subset=["HMA_200", "Close"]).tail(2)
    if len(recent) < 2:
        return _empty_signal()

    prev = recent.iloc[-2]
    curr = recent.iloc[-1]

    hma_curr = curr["HMA_200"]
    close_curr = curr["Close"]
    close_prev = prev["Close"]
    hma_prev = prev["HMA_200"]

    if hma_curr == 0 or np.isnan(hma_curr):
        return _empty_signal()

    distance_pct = ((close_curr - hma_curr) / hma_curr) * 100
    above_hma = close_curr > hma_curr
    was_above = close_prev > hma_prev
    in_near_zone = abs(distance_pct) <= NEAR_ZONE_PCT

    if (not was_above) and above_hma:
        signal = "🚀 BULLISH BREAKOUT"
    elif was_above and (not above_hma):
        signal = "💀 BEARISH BREAKDOWN"
    elif in_near_zone:
        signal = "👀 APPROACHING"
    else:
        signal = "🚀 BULLISH TREND" if above_hma else "💀 BEARISH TREND"

    return {
        "signal": signal,
        "hma_value": float(hma_curr),
        "close_value": float(close_curr),
        "distance_pct": float(distance_pct),
        "above_hma": bool(above_hma),
        "ltp": float(close_curr)
    }

def _empty_signal() -> dict:
    return {"signal": "NEUTRAL", "hma_value": 0.0, "close_value": 0.0, "distance_pct": 0.0, "above_hma": False, "ltp": 0.0}
