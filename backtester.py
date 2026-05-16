"""
backtester.py — Trading Altimeter
Historical backtesting engine for the 200 HMA crossover strategy.

Strategy Logic:
    BUY  signal: Daily Close crosses ABOVE the 200 HMA.
    SELL signal: Daily Close crosses BELOW the 200 HMA.

Capital Management:
    - 100% capital allocation per trade (fully invested or fully cash).
    - Compounding: each trade starts with the ending capital of the previous.
    - No slippage or commission in the base model (conservative assumption).

Metrics Computed:
    - Total Trades, Win Rate, Avg Win %, Avg Loss %
    - Max Drawdown % (peak-to-trough on equity curve)
    - Net Profit/Loss in ₹ and %
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from indicators import calculate_dhan_indicators, compute_hma, HMA_LENGTH


# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------

def run_backtest(symbol: str, start_date: str, end_date: str,
                 initial_capital: float = 100_000.0) -> dict:
    """
    Run the 200 HMA crossover backtest on a given NSE stock.

    Args:
        symbol     : NSE symbol without suffix, e.g. 'RELIANCE'
        start_date : 'YYYY-MM-DD' start of backtest window
        end_date   : 'YYYY-MM-DD' end of backtest window
        initial_capital: Starting capital in ₹ (default ₹1,00,000)

    Returns:
        dict with keys: trades (DataFrame), equity_curve (Series),
                        metrics (dict), df (full OHLCV+HMA DataFrame),
                        error (str or None)
    """
    symbol_ns = to_yf_ticker(symbol)

    # Fetch extra history before start_date for HMA warmup (200 bars needed)
    full_start = (pd.Timestamp(start_date) - pd.DateOffset(years=1)).strftime("%Y-%m-%d")
    df = fetch_ohlcv(symbol_ns, period="5y", interval="1d")

    if df.empty:
        return {"error": f"No data available for {symbol}"}

    # Calculate 200 HMA on full history
    df["HMA_200"] = compute_hma(df["Close"], HMA_LENGTH)
    df = df.dropna(subset=["HMA_200"])

    # Trim to user-selected window
    df = df[(df.index >= pd.Timestamp(start_date)) &
            (df.index <= pd.Timestamp(end_date))].copy()

    if len(df) < 10:
        return {"error": f"Insufficient data in date range for {symbol}"}

    # ── Signal Generation ──────────────────────────────────────────────────
    # 1 = above HMA, 0 = below HMA, crossover = change in state
    df["above_hma"] = (df["Close"] > df["HMA_200"]).astype(int)
    df["signal"] = df["above_hma"].diff()
    # signal = +1 → buy (crossed above), -1 → sell (crossed below)

    # ── Trade Simulation ───────────────────────────────────────────────────
    trades = []
    capital = initial_capital
    position = None   # dict when in trade, None when flat

    equity_series = []  # (date, portfolio_value)

    for i, (date, row) in enumerate(df.iterrows()):
        current_price = float(row["Close"])

        # Mark-to-market equity curve
        if position is not None:
            current_value = capital * (current_price / position["entry_price"])
        else:
            current_value = capital
        equity_series.append({"date": date, "value": current_value})

        sig = row["signal"]

        # BUY signal — enter long position
        if sig == 1 and position is None:
            position = {
                "entry_date": date,
                "entry_price": current_price,
                "capital_in": capital,
            }

        # SELL signal — exit long position
        elif sig == -1 and position is not None:
            pnl_pct = ((current_price - position["entry_price"])
                       / position["entry_price"]) * 100
            pnl_inr = capital * (pnl_pct / 100)
            capital = capital + pnl_inr  # compound

            trades.append({
                "Entry Date": position["entry_date"].date(),
                "Exit Date": date.date(),
                "Entry Price": round(position["entry_price"], 2),
                "Exit Price": round(current_price, 2),
                "P&L %": round(pnl_pct, 2),
                "P&L ₹": round(pnl_inr, 2),
                "Capital After": round(capital, 2),
                "Result": "WIN" if pnl_pct > 0 else "LOSS",
            })
            position = None

    # Close any open position at last price
    if position is not None:
        last_price = float(df["Close"].iloc[-1])
        pnl_pct = ((last_price - position["entry_price"])
                   / position["entry_price"]) * 100
        pnl_inr = capital * (pnl_pct / 100)
        capital = capital + pnl_inr
        trades.append({
            "Entry Date": position["entry_date"].date(),
            "Exit Date": df.index[-1].date(),
            "Entry Price": round(position["entry_price"], 2),
            "Exit Price": round(last_price, 2),
            "P&L %": round(pnl_pct, 2),
            "P&L ₹": round(pnl_inr, 2),
            "Capital After": round(capital, 2),
            "Result": "WIN" if pnl_pct > 0 else "LOSS (OPEN)",
        })

    trades_df = pd.DataFrame(trades)
    equity_df = pd.DataFrame(equity_series).set_index("date")

    metrics = _compute_metrics(trades_df, equity_df, initial_capital, capital)

    return {
        "trades": trades_df,
        "equity_curve": equity_df,
        "metrics": metrics,
        "df": df,
        "error": None,
    }


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _compute_metrics(trades_df: pd.DataFrame, equity_df: pd.DataFrame,
                     initial_capital: float, final_capital: float) -> dict:
    """
    Compute performance metrics from completed trades and equity curve.

    Max Drawdown: The largest peak-to-trough decline in the equity curve,
    expressed as a percentage of the peak value.
    """
    if trades_df.empty:
        return {
            "total_trades": 0, "win_rate": 0.0,
            "avg_win": 0.0, "avg_loss": 0.0,
            "max_drawdown": 0.0,
            "net_profit_inr": 0.0, "net_profit_pct": 0.0,
        }

    wins = trades_df[trades_df["Result"].str.startswith("WIN")]
    losses = trades_df[~trades_df["Result"].str.startswith("WIN")]

    win_rate = (len(wins) / len(trades_df)) * 100 if len(trades_df) else 0
    avg_win = wins["P&L %"].mean() if not wins.empty else 0.0
    avg_loss = losses["P&L %"].mean() if not losses.empty else 0.0

    # Max Drawdown
    eq_values = equity_df["value"]
    rolling_max = eq_values.cummax()
    drawdown = (eq_values - rolling_max) / rolling_max * 100
    max_drawdown = abs(drawdown.min()) if not drawdown.empty else 0.0

    net_profit_inr = final_capital - initial_capital
    net_profit_pct = (net_profit_inr / initial_capital) * 100

    return {
        "total_trades": len(trades_df),
        "win_rate": round(win_rate, 1),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "max_drawdown": round(max_drawdown, 2),
        "net_profit_inr": round(net_profit_inr, 2),
        "net_profit_pct": round(net_profit_pct, 2),
    }


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def build_price_chart(df: pd.DataFrame, trades_df: pd.DataFrame,
                      symbol: str) -> go.Figure:
    """
    Build a Plotly candlestick chart with 200 HMA overlay and
    Buy/Sell signal markers from the backtest.
    """
    fig = go.Figure()

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color="#00E676", decreasing_line_color="#FF1744",
        name="Price", showlegend=False,
    ))

    # 200 HMA line
    fig.add_trace(go.Scatter(
        x=df.index, y=df["HMA_200"],
        line=dict(color="#FFD700", width=2.5),
        name="200 HMA",
    ))

    # Buy markers (green triangles up)
    if not trades_df.empty:
        buy_dates = pd.to_datetime(trades_df["Entry Date"])
        buy_prices = []
        for d in buy_dates:
            row = df[df.index.date == d.date()]
            buy_prices.append(float(row["Close"].iloc[0]) if not row.empty else None)

        fig.add_trace(go.Scatter(
            x=buy_dates,
            y=[p * 0.985 if p else None for p in buy_prices],
            mode="markers",
            marker=dict(symbol="triangle-up", size=14,
                        color="#00E676", line=dict(width=1, color="#FFFFFF")),
            name="BUY",
        ))

        # Sell markers (red triangles down)
        sell_dates = pd.to_datetime(trades_df["Exit Date"])
        sell_prices = []
        for d in sell_dates:
            row = df[df.index.date == d.date()]
            sell_prices.append(float(row["Close"].iloc[0]) if not row.empty else None)

        fig.add_trace(go.Scatter(
            x=sell_dates,
            y=[p * 1.015 if p else None for p in sell_prices],
            mode="markers",
            marker=dict(symbol="triangle-down", size=14,
                        color="#FF1744", line=dict(width=1, color="#FFFFFF")),
            name="SELL",
        ))

    fig.update_layout(
        title=f"{symbol} — 200 HMA Backtest",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        paper_bgcolor="#0B0E11",
        plot_bgcolor="#0B0E11",
        font=dict(color="#E0E0E0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        height=480,
    )
    return fig


def build_equity_curve(equity_df: pd.DataFrame, initial_capital: float,
                       symbol: str) -> go.Figure:
    """Build the cumulative P&L equity curve chart."""
    fig = go.Figure()

    pnl_pct = ((equity_df["value"] - initial_capital) / initial_capital) * 100

    # Color fill: green above 0, red below
    fig.add_trace(go.Scatter(
        x=equity_df.index, y=pnl_pct,
        fill="tozeroy",
        line=dict(color="#00D4FF", width=2),
        fillcolor="rgba(0,212,255,0.12)",
        name="Cumulative P&L %",
    ))

    fig.add_hline(y=0, line_color="#8A8D94", line_dash="dash", line_width=1)

    fig.update_layout(
        title=f"{symbol} — Equity Curve",
        xaxis_title="Date",
        yaxis_title="Return %",
        template="plotly_dark",
        paper_bgcolor="#0B0E11",
        plot_bgcolor="#0B0E11",
        font=dict(color="#E0E0E0"),
        height=300,
    )
    return fig
