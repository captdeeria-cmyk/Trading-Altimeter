"""
app.py — Trading Altimeter
Central high-performance router panel driving structural processing components.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import inject_css, NSE_250, render_sidebar_header, render_banner, signal_badge
from dhan_broker import fetch_historical_candles, get_dhan_connection, route_instant_trade
from indicators import calculate_dhan_indicators, classify_dhan_signal

st.set_page_config(
    page_title="Trading Altimeter",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enforce clean Light styling engine rules instantly
inject_css()

# ── Sidebar Control Desk ──
with st.sidebar:
    render_sidebar_header()
    st.markdown("---")
    page = st.radio("Navigation Deck", ["🏠 Live Dashboard", "🛰 HMA Live Scanner", "💼 My Portfolio"])
    
    st.markdown("---")
    paper_mode = st.toggle("Simulated Paper Engine", value=True)
    
    # Live Dhan Diagnostics Monitor Panel
    dhan_conn = get_dhan_connection()
    if dhan_conn:
        st.markdown('<div style="color: #047857; font-weight:700;">● DHAN API: CONNECTED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color: #B91C1C; font-weight:700;">○ DHAN API: DISCONNECTED</div>', unsafe_allow_html=True)

# ── Feature Workspace Routes ──
if page == "🏠 Live Dashboard":
    render_banner()
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Critical Trend Flags")
        # Process a quick data sample block from your workspace configuration
        sample_df = fetch_historical_candles("2885") # RELIANCE Security ID
        if not sample_df.empty:
            analyzed = calculate_dhan_indicators(sample_df)
            metrics = classify_dhan_signal(analyzed)
            
            st.markdown(f"""
            <div class="ta-card">
                <span style="font-weight:800; font-size:1.1rem; color:#111827;">RELIANCE</span><br>
                <span style="font-size:0.85rem; color:#4B5563;">Current Position Status Flag:</span> {signal_badge(metrics['signal'])}<br><br>
                <span style="font-size:1.25rem; font-weight:800; color:#111827;">₹{metrics['ltp']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            
    with c2:
        st.subheader("Focused Profile Chart")
        if not sample_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sample_df.index[-120:], y=sample_df['Close'].tail(120), name="Price", line=dict(color="#10B981", width=2)))
            fig.add_trace(go.Scatter(x=sample_df.index[-120:], y=sample_df['HMA_200'].tail(120), name="200 HMA", line=dict(color="#2563EB", width=2, dash='dash')))
            fig.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=240, margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)

elif page == "🛰 HMA Live Scanner":
    st.title("🛰 Institutional Breakout Scanner")
    st.caption("Direct Dhan pipeline verification matrix scanning across multiple sector tracks.")
    
    scan_rows = []
    progress = st.progress(0)
    
    # Process lookups across your 250 data universe arrays efficiently
    for idx, item in enumerate(NSE_250):
        raw_candles = fetch_historical_candles(item['security_id'])
        if not raw_candles.empty:
            df_proc = calculate_dhan_indicators(raw_candles)
            profile = classify_dhan_signal(df_proc)
            scan_rows.append({
                "Symbol": item['symbol'],
                "LTP": f"₹{profile['ltp']:.2f}",
                "Distance to HMA": f"{profile['distance_pct']:+.2f}%",
                "Signal Matrix": profile['signal']
            })
        progress.progress((idx + 1) / len(NSE_250))
        
    if scan_rows:
        st.dataframe(pd.DataFrame(scan_rows), use_container_width=True, hide_index=True)

elif page == "💼 My Portfolio":
    st.title("💼 Real-Time Portfolio Ledger")
    st.caption("Active tracking computations derived from continuous execution loops.")
    st.info("System operational. Add structural lines via your trade confirmation inputs.")
