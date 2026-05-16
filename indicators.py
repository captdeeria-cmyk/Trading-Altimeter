"""
indicators.py — Trading Altimeter
Core analytical calculations using rapid DataFrame transformations over Dhan streaming objects.
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
import logging

logger = logging.getLogger(__name__)

HMA_LENGTH = 200
NEAR_ZONE_PCT = 1.5

def calculate_dhan_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Computes mathematical vectors over clean Dhan candle maps."""
    if df.empty or len(df) < HMA_LENGTH:
        return df
    
    # Calculate Hull Moving Average
    df['HMA_200'] = ta.hma(df['Close'], length=HMA_LENGTH)
    df['EMA_200'] = ta.ema(df['Close'], length=HMA_LENGTH)
    df['RSI_14'] = ta.rsi(df['Close'], length=14)
    
    macd_df = ta.macd(df['Close'])
    if macd_df is not None and not macd_df.empty:
        df['MACD'] = macd_df.iloc[:, 0]
        df['MACD_Signal'] = macd_df.iloc[:, 1]
    else:
        df['MACD'] = 0.0
        df['MACD_Signal'] = 0.0
        
    return df

def classify_dhan_signal(df: pd.DataFrame) -> dict:
    """Labels trend position metrics."""
    if df.empty or 'HMA_200' not in df.columns or pd.isna(df['HMA_200'].iloc[-1]):
        return _empty_profile()
        
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    c_close, c_hma = float(curr['Close']), float(curr['HMA_200'])
    p_close, p_hma = float(prev['Close']), float(prev['HMA_200'])
    
    distance = ((c_close - c_hma) / c_hma) * 100
    
    if p_close <= p_hma and c_close > c_hma:
        sig = "🚀 BULLISH BREAKOUT"
    elif p_close >= p_hma and c_close < c_hma:
        sig = "💀 BEARISH BREAKDOWN"
    elif abs(distance) <= NEAR_ZONE_PCT:
        sig = "👀 APPROACHING"
    else:
        sig = "🚀 BULLISH TREND" if c_close > c_hma else "💀 BEARISH TREND"
        
    return {
        "signal": sig,
        "ltp": c_close,
        "hma": c_hma,
        "distance_pct": distance,
        "above_hma": c_close > c_hma
    }

def _empty_profile():
    return {"signal": "NEUTRAL", "ltp": 0.0, "hma": 0.0, "distance_pct": 0.0, "above_hma": False}
