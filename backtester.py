"""
backtester.py — Trading Altimeter
Natively evaluates the historical validity of 200 HMA breakouts across selected chart blocks.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from indicators import calculate_dhan_indicators

def run_backtest(symbol_df: pd.DataFrame, initial_capital: float = 100_000.0) -> dict:
    if symbol_df.empty or len(symbol_df) < 200:
        return {}
        
    df = calculate_dhan_indicators(symbol_df.copy()).dropna(subset=["HMA_200"])
    capital = initial_capital
    position = 0.0
    trades_log = []
    equity_line = []
    
    for idx, row in df.iterrows():
        close = float(row["Close"])
        hma = float(row["HMA_200"])
        
        if close > hma and position == 0:
            position = capital / close
            capital = 0.0
            trades_log.append({"type": "BUY", "date": idx, "price": close})
        elif close < hma and position > 0:
            capital = position * close
            position = 0.0
            trades_log.append({"type": "SELL", "date": idx, "price": close})
            
        current_equity = capital if position == 0 else position * close
        equity_line.append({"date": idx, "value": current_equity})
        
    if not equity_line:
        return {}
        
    eq_df = pd.DataFrame(equity_line).set_index("date")
    return {
        "trades": trades_log, 
        "equity": eq_df, 
        "final_value": float(eq_df["value"].iloc[-1])
    }

def build_price_chart(df: pd.DataFrame, trades: list, symbol: str):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Candlesticks"))
    if "HMA_200" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["HMA_200"], name="200 HMA", line=dict(color="#2563EB", width=2)))
    fig.update_layout(template="plotly_white", height=380, margin=dict(l=10,r=10,t=10,b=10), xaxis_rangeslider_visible=False)
    return fig

def build_equity_curve(equity_df: pd.DataFrame, initial_capital: float, symbol: str):
    fig = go.Figure()
    if not equity_df.empty:
        net_return = ((equity_df["value"] - initial_capital) / initial_capital) * 100
        fig.add_trace(go.Scatter(x=equity_df.index, y=net_return, name="Yield Growth %", fill="tozeroy", line=dict(color="#10B981", width=2)))
    fig.update_layout(template="plotly_white", height=220, margin=dict(l=10,r=10,t=10,b=10))
    return fig
