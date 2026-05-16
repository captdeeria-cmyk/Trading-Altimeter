"""
indicators.py — Trading Altimeter
Core mathematical indicators and breakout rules processed natively.
"""
import warnings
import logging
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HMA_LENGTH = 200          
NEAR_ZONE_PCT = 1.5       

def _wma(series: pd.Series, length: int) -> pd.Series:
    """Calculates Weighted Moving Average efficiently without pandas_ta dependencies."""
    if len(series) < length:
        return pd.Series(np.nan, index=series.index)
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )

def compute_hma(close: pd.Series, length: int = HMA_LENGTH) -> pd.Series:
    """Mathematical execution block generating clean 200 Hull Moving Average data curves."""
    if close.empty or len(close) < length:
        return pd.Series(np.nan, index=close.index)
    half = length // 2
    sqrt_len = int(np.floor(np.sqrt(length)))
    
    wma_half = _wma(close, half)
    wma_full = _wma(close, length)
    raw_hma = 2 * wma_half - wma_full
    return _wma(raw_hma, sqrt_len)

def calculate_dhan_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Appends all required moving averages, RSI, and MACD columns onto the workspace DataFrame."""
    if df.empty:
        return df
        
    close = df["Close"]
    df["HMA_200"] = compute_hma(close, HMA_LENGTH)
    df["EMA_200"] = close.ewm(span=200, adjust=False).mean()
    
    # RSI (14) Relative Strength Matrix calculations
    delta = close.diff()
    gain = (delta.clip(lower=0)).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI_14"] = 100 - (100 / (1 + rs))
    df["RSI_14"] = df["RSI_14"].fillna(50)
    
    # Standard MACD Vectors
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema_12 - ema_26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    
    return df

def classify_dhan_signal(df: pd.DataFrame) -> dict:
    """Analyzes the relation between current closing prices and the 200 HMA line vector."""
    if df.empty or "HMA_200" not in df.columns:
        return _empty_signal(0.0)

    # Filter out initialization rows where HMA isn't fully built yet
    valid_df = df.dropna(subset=["HMA_200", "Close"])
    if len(valid_df) < 2:
        return _empty_signal(df["Close"].iloc[-1] if not df.empty else 0.0)

    curr = valid_df.iloc[-1]
    prev = valid_df.iloc[-2]

    hma_curr, close_curr = float(curr["HMA_200"]), float(curr["Close"])
    hma_prev, close_prev = float(prev["HMA_200"]), float(prev["Close"])
    
    distance_pct = ((close_curr - hma_curr) / hma_curr) * 100
    above_hma = close_curr > hma_curr
    was_above = close_prev > hma_prev
    
    if not was_above and above_hma:
        signal = "🚀 BULLISH BREAKOUT"
    elif was_above and not above_hma:
        signal = "💀 BEARISH BREAKDOWN"
    elif abs(distance_pct) <= NEAR_ZONE_PCT:
        signal = "👀 APPROACHING"
    else:
        signal = "🚀 BULLISH TREND" if above_hma else "💀 BEARISH TREND"

    return {
        "signal": signal, "hma_value": hma_curr, "close_value": close_curr,
        "distance_pct": distance_pct, "above_hma": above_hma, "ltp": close_curr
    }

def _empty_signal(fallback_price) -> dict:
    return {"signal": "NEUTRAL", "hma_value": fallback_price, "close_value": fallback_price, "distance_pct": 0.0, "above_hma": False, "ltp": fallback_price}
