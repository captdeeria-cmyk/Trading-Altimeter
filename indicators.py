"""
indicators.py — Trading Altimeter
Core analytics engine: data fetching via yfinance, 200-period Hull Moving
Average (HMA) calculation, and signal classification logic.

Hull Moving Average (HMA) Formula:
    HMA(n) = WMA(2 * WMA(n/2) - WMA(n), sqrt(n))
    where WMA = Weighted Moving Average.
    The HMA significantly reduces lag compared to SMA/EMA while remaining
    smooth, making it ideal for trend detection.

pandas_ta implements this as hma(close, length=n).
"""

import warnings
import logging
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st

try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HMA_LENGTH = 200          # HMA period
NEAR_ZONE_PCT = 1.5       # "Approaching" threshold — within 1.5% of HMA
DEFAULT_INTERVAL = "1d"   # Daily candles
DEFAULT_PERIOD = "2y"     # 2 years for HMA warmup


# ---------------------------------------------------------------------------
# Data Fetching
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300)
def fetch_ohlcv(symbol_ns: str, period: str = DEFAULT_PERIOD,
                interval: str = DEFAULT_INTERVAL) -> pd.DataFrame:
    """
    Fetch OHLCV data from yfinance for a single NSE stock.

    Args:
        symbol_ns: yfinance symbol with .NS suffix, e.g. 'RELIANCE.NS'
        period: yfinance period string e.g. '2y', '1y', '6mo'
        interval: candle interval e.g. '1d', '1h', '15m'

    Returns:
        DataFrame with columns [Open, High, Low, Close, Volume] or empty DF.
    """
    try:
        df = yf.download(symbol_ns, period=period, interval=interval,
                         auto_adjust=True, progress=False)
        if df.empty or len(df) < 10:
            logger.warning(f"No data returned for {symbol_ns}")
            return pd.DataFrame()
        # Flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        logger.warning(f"Error fetching {symbol_ns}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_live_quote(symbol_ns: str) -> dict:
    """
    Fetch only the latest price and day change for a stock (lightweight).
    Used for the 250-stock dashboard grid — does NOT calculate HMA.

    Returns:
        dict with keys: symbol, ltp, change_pct, prev_close
    """
    try:
        ticker = yf.Ticker(symbol_ns)
        info = ticker.fast_info
        ltp = getattr(info, "last_price", None) or getattr(info, "regularMarketPrice", None)
        prev = getattr(info, "previous_close", None) or getattr(info, "regularMarketPreviousClose", None)
        if ltp and prev:
            change_pct = ((ltp - prev) / prev) * 100
        else:
            change_pct = 0.0
        return {
            "symbol": symbol_ns.replace(".NS", ""),
            "ltp": round(ltp, 2) if ltp else 0.0,
            "change_pct": round(change_pct, 2),
            "prev_close": round(prev, 2) if prev else 0.0,
        }
    except Exception as e:
        logger.warning(f"Live quote error for {symbol_ns}: {e}")
        return {"symbol": symbol_ns.replace(".NS", ""), "ltp": 0.0, "change_pct": 0.0, "prev_close": 0.0}


# ---------------------------------------------------------------------------
# HMA Calculation
# ---------------------------------------------------------------------------

def _wma(series: pd.Series, length: int) -> pd.Series:
    """
    Compute Weighted Moving Average (WMA) manually.
    Weights are linearly increasing: most recent bar has highest weight.
    """
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )


def compute_hma(close: pd.Series, length: int = HMA_LENGTH) -> pd.Series:
    """
    Compute Hull Moving Average.

    HMA(n) = WMA(2*WMA(n/2) - WMA(n), floor(sqrt(n)))

    Args:
        close: Series of closing prices.
        length: HMA period (default 200).

    Returns:
        pd.Series of HMA values aligned to close's index.
    """
    if HAS_PANDAS_TA:
        try:
            hma = ta.hma(close, length=length)
            if hma is not None and not hma.isna().all():
                return hma
        except Exception:
            pass  # Fall back to manual calculation

    # Manual fallback
    half = length // 2
    sqrt_len = int(np.floor(np.sqrt(length)))
    wma_half = _wma(close, half)
    wma_full = _wma(close, length)
    raw = 2 * wma_half - wma_full
    return _wma(raw, sqrt_len)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all technical indicators to an OHLCV DataFrame.

    Adds: HMA_200, EMA_20, EMA_50, RSI_14, MACD, MACD_Signal, MACD_Hist

    Args:
        df: DataFrame with at minimum a 'Close' column.

    Returns:
        DataFrame with indicator columns appended.
    """
    if df.empty or len(df) < HMA_LENGTH:
        return df

    close = df["Close"]

    # 200 HMA — core signal
    df["HMA_200"] = compute_hma(close, HMA_LENGTH)

    # EMA overlays
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
        # Pure pandas fallback
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


# ---------------------------------------------------------------------------
# Signal Classification
# ---------------------------------------------------------------------------

def classify_hma_signal(df: pd.DataFrame) -> dict:
    """
    Classify the 200 HMA signal based on the last 2 CLOSED candles.

    Signals (in priority order):
      BULLISH  — Close crossed from below to above HMA, or was in Near Zone
                 and closed above HMA.
      BEARISH  — Close crossed from above to below HMA, or was in Near Zone
                 and closed below HMA.
      APPROACHING — Within NEAR_ZONE_PCT% of HMA but no confirmed cross.
      NEUTRAL  — No significant interaction.

    Returns:
        dict with keys: signal, hma_value, close_value, distance_pct,
                        last_date, above_hma
    """
    if df.empty or "HMA_200" not in df.columns:
        return _empty_signal()

    # Use last 3 rows to evaluate 2 closed candles + context
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

    # Determine signal
    crossed_above = (not was_above) and above_hma      # prev below, curr above
    crossed_below = was_above and (not above_hma)       # prev above, curr below
    near_zone_close_above = in_near_zone and above_hma
    near_zone_close_below = in_near_zone and (not above_hma)

    if crossed_above or near_zone_close_above:
        signal = "BULLISH"
    elif crossed_below or near_zone_close_below:
        signal = "BEARISH"
    elif in_near_zone:
        signal = "APPROACHING"
    else:
        signal = "NEUTRAL"

    return {
        "signal": signal,
        "hma_value": round(float(hma_curr), 2),
        "close_value": round(float(close_curr), 2),
        "distance_pct": round(float(distance_pct), 2),
        "last_date": str(recent.index[-1].date()),
        "above_hma": bool(above_hma),
    }


def _empty_signal() -> dict:
    return {
        "signal": "NEUTRAL",
        "hma_value": 0.0,
        "close_value": 0.0,
        "distance_pct": 0.0,
        "last_date": "N/A",
        "above_hma": False,
    }


# ---------------------------------------------------------------------------
# Batch screener — used by the Scanner tab
# ---------------------------------------------------------------------------

def batch_hma_status(symbol_ns: str) -> dict:
    """
    Lightweight HMA signal fetcher for batch scanning.
    Fetches 1 year of daily data and returns the signal dict.
    """
    try:
        df = fetch_ohlcv(symbol_ns, period="1y", interval="1d")
        if df.empty:
            return {"symbol": symbol_ns.replace(".NS", ""), "signal": "ERROR"}
        df = add_indicators(df)
        sig = classify_hma_signal(df)
        sig["symbol"] = symbol_ns.replace(".NS", "")
        quote = fetch_live_quote(symbol_ns)
        sig["ltp"] = quote["ltp"]
        sig["change_pct"] = quote["change_pct"]
        return sig
    except Exception as e:
        logger.warning(f"batch_hma_status error {symbol_ns}: {e}")
        return {"symbol": symbol_ns.replace(".NS", ""), "signal": "ERROR"}