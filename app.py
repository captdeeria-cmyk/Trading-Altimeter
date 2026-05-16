"""
app.py — Trading Altimeter
Central application engine routing and dispatch control desk.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── App configuration (CRITICAL: MUST run first) ─────────────────────────────
st.set_page_config(
    page_title="Trading Altimeter",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Import local code modules smoothly ────────────────────────────────────────
from utils import inject_css, NSE_250, render_sidebar_header, render_banner, signal_badge
from dhan_broker import fetch_historical_candles, get_dhan_connection, render_order_panel
from indicators import calculate_dhan_indicators, classify_dhan_signal
from backtester import run_backtest, build_price_chart, build_equity_curve
from watchlist import render_watchlist_page
from portfolio import render_portfolio_page

# Inject Light Theme canvas layout rules
inject_css()

# ── Sidebar Cockpit Panel ──
with st.sidebar:
    render_sidebar_header()
    page = st.radio("Navigation Menu", ["🏠 Live Dashboard", "🔬 Strategy Backtester", "🛰 Watchlist Engine", "💼 Asset Ledger"])
    st.markdown("---")
    
    # Connection Validation
    if get_dhan_connection():
        st.markdown('<div class="badge-bullish" style="display:block; text-align:center;">● DHAN DATA: SECURE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-neutral" style="display:block; text-align:center;">○ DHAN DATA: DEMO CHANNELS</div>', unsafe_allow_html=True)

# ── Page Routing Execution ──
if page == "🏠 Live Dashboard":
    render_banner()
    
    c1, c2 = st.columns([4, 6])
    with c1:
        st.subheader("200 HMA Proximity Alerts")
        # Load the default core profile tracking asset
        df_candles = fetch_historical_candles("2885")
        if not df_candles.empty:
            df_proc = calculate_dhan_indicators(df_candles)
            profile = classify_dhan_signal(df_proc)
            
            st.markdown(f"""
            <div class="ta-card">
                <div style='font-size:1.2rem; font-weight:800; color:#0F172A;'>RELIANCE INDUSTRIES</div>
                <div style='margin:8px 0;'>Altimeter Vector: {signal_badge(profile['signal'])}</div>
                <div style='font-size:1.6rem; font-weight:900; color:#0F172A;'>₹{profile['ltp']:.2f}</div>
                <div style='font-size:0.8rem; color:#64748B; margin-top:4px;'>Distance: {profile['distance_pct']:+.2f}% from HMA (₹{profile['hma_value']:.2f})</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Draw individual sidebar panel tools
            render_order_panel("RELIANCE", profile['ltp'])
            
    with c2:
        st.subheader("Active Analytics Horizon Chart")
        if not df_candles.empty:
            fig = build_price_chart(df_candles.tail(120), [], "RELIANCE")
            st.plotly_chart(fig, use_container_width=True)

elif page == "🔬 Strategy Backtester":
    st.title("🔬 200 HMA Crossover Backtest Rig")
    st.caption("Evaluates compounding growth strategies across historical daily price candles.")
    
    selected_stock = st.selectbox("Select Tracking Target symbol:", [item["symbol"] for item in NSE_250])
    target_id = next(item["security_id"] for item in NSE_250 if item["symbol"] == selected_stock)
    
    df_candles = fetch_historical_candles(target_id)
    if not df_candles.empty:
        results = run_backtest(df_candles)
        if results:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Final Account Valuation Value", f"₹{results['final_value']:,.2f}")
            with col2:
                # Calculate return margin percentages safely
                profit_pct = ((results['final_value'] - 100000.0) / 100000.0) * 100
                st.metric("Net Run Yield %", f"{profit_pct:+.2f}%")
                
            fig_curve = build_equity_curve(results['equity'], 100_000.0, selected_stock)
            st.plotly_chart(fig_curve, use_container_width=True)

elif page == "🛰 Watchlist Engine":
    render_watchlist_page()

elif page == "💼 Asset Ledger":
    render_portfolio_page()
