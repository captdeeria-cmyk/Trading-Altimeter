import pandas as pd
import pandas_ta as ta

def calculate_indicators(df):
    """
    Accepts a Dhan DataFrame and processes Cockpit technical indicators.
    """
    if df.empty or len(df) < 200:
        return df
    
    # 1. 200 Hull Moving Average (HMA)
    df['HMA_200'] = ta.hma(df['Close'], length=200)
    
    # 2. 200 Exponential Moving Average (EMA) for validation
    df['EMA_200'] = ta.ema(df['Close'], length=200)
    
    # 3. RSI (14)
    df['RSI_14'] = ta.rsi(df['Close'], length=14)
    
    # 4. MACD
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_Signal'] = macd['MACDs_12_26_9']
    
    return df

def generate_hma_signal(df):
    """
    Evaluates current price action relative to the 200 HMA.
    """
    if df.empty or 'HMA_200' not in df.columns:
        return "NO_SIGNAL", 0.0
        
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    current_price = latest['Close']
    current_hma = latest['HMA_200']
    prev_price = prev['Close']
    prev_hma = prev['HMA_200']
    
    # Strategy Rules
    if prev_price <= prev_hma and current_price > current_hma:
        return "🚀 BULLISH BREAKOUT", current_price
    elif prev_price >= prev_hma and current_price < current_hma:
        return "💀 BEARISH BREAKDOWN", current_price
    
    # Proximity Alert (Within 1.5%)
    proximity = abs(current_price - current_hma) / current_hma
    if proximity <= 0.015:
        return "👀 APPROACHING 200 HMA", current_price
        
    return "STABLE_TREND", current_price
