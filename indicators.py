"""
indicators.py — Trading Altimeter
Core analytics engine: Data processing, 200-period Hull Moving
Average (HMA) calculation, and Dhan-aligned signal classification logic.
"""

import warnings
import logging
import numpy as np
import pandas as pd
import streamlit as st

try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Constants
HMA_LENGTH = 200          # HMA period
NEAR_ZONE_PCT = 1.5       # "Approaching" threshold — within 1.5% of HMA

def _wma(series: pd.Series, length: int) -> pd.Series:
    """Compute Weighted Moving Average (WMA) manually if pandas_ta fails."""
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )

def compute_hma(close: pd.Series, length: int = HMA_LENGTH) -> pd.Series:
    """Compute Hull Moving Average cleanly."""
    if HAS_PANDAS_TA:
        try:
            hma = ta.hma(close, length=length)
            if hma is not None and not hma.isna().all():
                return hma
        except Exception:
            pass

    # Manual fallback execution pipeline
    half = length // 2
    sqrt_len = int(np.floor(np.sqrt(length)))
    wma_half = _wma(close, half)
    wma_full = _wma(close, length)
    raw = 2 * wma_half - wma_full
    return _wma(raw, sqrt_len)

def calculate_dhan_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Appends 200 HMA, EMA, RSI, and MACD indicators to the incoming Dhan DataFrame.
    """
    if df.empty or len(df) < HMA_LENGTH:
        return df

    close = df["Close"]
    df["HMA_200"] = compute_hma(close, HMA_LENGTH)

    if HAS_PANDAS_TA:
        df["EMA_20"] = ta.ema(close, length=20)
        df["EMA_50"] = ta.ema(close, length=50)
        rsi = ta.rsi(close, length=14)
        df["RSI_14"] = rsi if rsi is not None else pd.Series(np.nan, index=df.index)
        macd_df = ta.macd(close, fast=12, slow=26, signal=9)
        if macd_df is not None and not macd_df.empty:
            df["MACD"] = macd_df.iloc[:, 0]
            df["MACD_Signal"] = macd_df.iloc[:, 2]
            df["MACD_Hist"] = macd_df.iloc[:, 1]
        else:
            df["MACD"] = df["MACD_Signal"] = df["MACD_Hist"] = np.nan
    else:
        # Pure pandas fallback framework
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
    """
    Classifies trend directions based on the latest calculated 200 HMA bars.
    """
    if df.empty or "HMA_200" not in df.columns:
        return _empty_signal()

    recent = df.dropna(subset=["HMA_200", "Close"]).tail(3)
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

    # Determine structural breakout signal metrics
    crossed_above = (not was_above) and above_hma
    crossed_below = was_above and (not above_hma)

    if crossed_above:
        signal = "🚀 BULLISH BREAKOUT"
    elif crossed_below:
        signal = "💀 BEARISH BREAKDOWN"
    elif in_near_zone:
        signal = "👀 APPROACHING"
    else:
        signal = "🚀 BULLISH TREND" if above_hma else "💀 BEARISH TREND"

    return {
        "signal": signal,
        "hma_value": round(float(hma_curr), 2),
        "close_value": round(float(close_curr), 2),
        "distance_pct": round(float(distance_pct), 2),
        "last_date": str(recent.index[-1].date()),
        "above_hma": bool(above_hma),
        "ltp": round(float(close_curr), 2)
    }

def _empty_signal() -> dict:
    return {
        "signal": "NEUTRAL", "hma_value": 0.0, "close_value": 0.0,
        "distance_pct": 0.0, "last_date": "N/A", "above_hma": False, "ltp": 0.0
    }
