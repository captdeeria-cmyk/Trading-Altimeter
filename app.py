"""
app.py — Trading Altimeter
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── RULE 1: MUST RUN FIRST ──
st.set_page_config(
    page_title="Trading Altimeter",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils import inject_css, NSE_250, render_sidebar_header, render_banner, signal_badge
from dhan_broker import fetch_historical_candles, get_dhan_connection
from indicators import calculate_dhan_indicators, classify_dhan_signal
from backtester import run_backtest, build_price_chart, build_equity_curve
from watchlist import render_watchlist_page
from portfolio import render_portfolio_page

# Trigger style engine
inject_css()

with st.sidebar:
    render_sidebar_header()
    st.markdown("---")
    page = st.radio("Navigation Menu", ["🏠 Live Cockpit Dashboard", "🔬 Strategy Backtester", "🛰 Watchlist Engine", "💼 Asset Ledger"])
    st.markdown("---")
    
    if get_dhan_connection():
        st.markdown('<div style="color: #047857; font-weight:700;">● DHAN ENGINE: CONNECTED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color: #6B7280; font-weight:700;">○ DHAN ENGINE: OFFLINE</div>', unsafe_allow_html=True)

if page == "🏠 Live Cockpit Dashboard":
    render_banner()
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("200 HMA Track Alerts")
        df_candles = fetch_historical_candles("2885")
        if not df_candles.empty:
            df_proc = calculate_dhan_indicators(df_candles)
            profile = classify_dhan_signal(df_proc)
            st.markdown(f"""
            <div style='background:#FFFFFF; padding:1.2rem; border:1px solid #E5E7EB; border-radius:8px;'>
                <span style='font-weight:800; font-size:1.1rem;'>RELIANCE</span><br>
                <small style='color:#6B7280;'>Signal Matrix Status Check:</small> {signal_badge(profile['signal'])}<br><br>
                <span style='font-size:1.4rem; font-weight:800;'>₹{profile['ltp']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
    with c2:
        st.subheader("Active Chart Horizon")
        if not df_candles.empty:
            fig = build_price_chart(df_candles.tail(90), [], "RELIANCE")
            st.plotly_chart(fig, use_container_width=True)

elif page == "🔬 Strategy Backtester":
    st.title("🔬 200 HMA Crossover Backtest Rig")
    df_candles = fetch_historical_candles("2885")
    if not df_candles.empty:
        results = run_backtest(df_candles)
        if results:
            st.metric("Final Capital Account Valuation", f"₹{results['final_value']:,.2f}")
            fig_curve = build_equity_curve(results['equity'], 100_000.0, "RELIANCE")
            st.plotly_chart(fig_curve, use_container_width=True)

elif page == "🛰 Watchlist Engine":
    render_watchlist_page()

elif page == "💼 Asset Ledger":
    render_portfolio_page()
