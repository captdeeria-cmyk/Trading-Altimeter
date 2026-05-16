"""
backtester.py — Trading Altimeter
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from indicators import calculate_dhan_indicators

def run_backtest(symbol_df: pd.DataFrame, initial_capital: float = 100_000.0) -> dict:
    if symbol_df.empty or len(symbol_df) < 200:
        return {}
        
    df = calculate_dhan_indicators(symbol_df.copy())
    capital = initial_capital
    position = 0.0
    trades = []
    equity_curve = []
    
    for idx, row in df.iterrows():
        close = row["Close"]
        hma = row["HMA_200"]
        
        if pd.isna(hma):
            equity_curve.append({"date": idx, "value": capital})
            continue
            
        if row["Close"] > row["HMA_200"] and position == 0:
            position = capital / close
            capital = 0.0
            trades.append({"type": "BUY", "date": idx, "price": close})
        elif row["Close"] < row["HMA_200"] and position > 0:
            capital = position * close
            position = 0.0
            trades.append({"type": "SELL", "date": idx, "price": close})
            
        current_val = capital if position == 0 else position * close
        equity_curve.append({"date": idx, "value": current_val})
        
    equity_df = pd.DataFrame(equity_curve).set_index("date")
    return {"trades": trades, "equity": equity_df, "final_value": equity_df["value"].iloc[-1] if not equity_df.empty else initial_capital}

def build_price_chart(df: pd.DataFrame, trades: list, symbol: str):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    if "HMA_200" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["HMA_200"], name="200 HMA", line=dict(color="#2563EB")))
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=10,r=10,t=30,b=10))
    return fig

def build_equity_curve(equity_df: pd.DataFrame, initial_capital: float, symbol: str):
    fig = go.Figure()
    if not equity_df.empty:
        pnl = ((equity_df["value"] - initial_capital) / initial_capital) * 100
        fig.add_trace(go.Scatter(x=equity_df.index, y=pnl, name="Return %", fill="tozeroy", line=dict(color="#10B981")))
    fig.update_layout(template="plotly_white", height=240, margin=dict(l=10,r=10,t=10,b=10))
    return fig
