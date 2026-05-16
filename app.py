import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="Trading Altimeter", page_icon="✈", layout="wide", initial_sidebar_state="expanded")
from utils import inject_css, NSE_250, NIFTY_50, to_yf_ticker, render_sidebar_header, render_banner, signal_badge
from indicators import fetch_ohlcv, fetch_live_quote, add_indicators, classify_hma_signal

inject_css()
if "page" not in st.session_state: st.session_state["page"] = "Dashboard"
if "selected_stock" not in st.session_state: st.session_state["selected_stock"] = "RELIANCE"

# ── SIDEBAR ────────────────────────────────────────────────────────────
render_sidebar_header()
with st.sidebar:
    st.markdown("---")
    for icon, page in zip(["🏠","📈","🛰","⭐","💼"], ["Dashboard","Stock Analysis","HMA Scanner","Watchlist","Portfolio"]):
        if st.button(f"{icon} {page}", use_container_width=True, key=f"nav_{page}"): st.session_state["page"] = page; st.rerun()
    st.markdown("---")
    now_ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    is_open = 9 <= now_ist.hour < 15 and now_ist.weekday() < 5
    st.markdown(f"<div style='text-align:center;font-weight:700;color:{'#16A34A' if is_open else '#DC2626'}'>● {'MARKET OPEN' if is_open else 'MARKET CLOSED'}</div><div style='text-align:center;color:#6C757D'>IST {now_ist.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

# ── DASHBOARD ───────────────────────────────────────────────────────────
def render_dashboard():
    render_banner()
    st.markdown('<div class="section-title">Live Market Overview</div>', unsafe_allow_html=True)
    
    selected_batch = st.selectbox("Show stocks:", ["Nifty 50", "Next 50", "F&O 101-150", "F&O 151-250"], label_visibility="collapsed")
    batches = {"Nifty 50": NSE_250[:50], "Next 50": NSE_250[50:100], "F&O 101-150": NSE_250[100:150], "F&O 151-250": NSE_250[150:250]}
    stocks = batches[selected_batch]

    quotes = []
    prog = st.progress(0, text="Fetching...")
    for i, sym in enumerate(stocks):
        q = fetch_live_quote(to_yf_ticker(sym))
        quotes.append(q)
        prog.progress((i+1)/len(stocks), text=f"{sym}...")
    prog.empty()

    # PREMIUM HTML GRID (Fixes the messy text issue)
    cols = st.columns(5)
    for i, q in enumerate(quotes):
        with cols[i % 5]:
            c = "#16A34A" if q["change_pct"] >= 0 else "#DC2626"
            sign = "+" if q["change_pct"] >= 0 else ""
            st.markdown(f"""
            <div class="stock-card" onclick="console.log('click')">
                <div class="stock-name">{q['symbol']}</div>
                <div class="stock-price">₹{q['ltp']:,.2f}</div>
                <div class="{'stock-chg-pos' if c=='#16A34A' else 'stock-chg-neg'}">{sign}{q['change_pct']:.2f}%</div>
            </div>""", unsafe_allow_html=True)
            
            if st.button("Analyze", key=f"grid_{q['symbol']}", use_container_width=True):
                st.session_state["selected_stock"] = q["symbol"]
                st.session_state["page"] = "Stock Analysis"
                st.rerun()

# ── STOCK ANALYSIS (WITH INTRADAY SUPPORT) ───────────────────────────────
def render_stock_analysis():
    render_banner()
    c1, c2 = st.columns([3, 1])
    with c1: stock_input = st.selectbox("Stock", NSE_250, index=NSE_250.index(st.session_state["selected_stock"]) if st.session_state["selected_stock"] in NSE_250 else 0)
    
    # INTRADAY SELECTOR HERE
    with c2: interval = st.selectbox("Interval", ["1d", "1wk", "1mo", "15m", "5m", "3m"], index=0, help="Intraday intervals fetch last 60 days of data.")
    st.session_state["selected_stock"] = stock_input
    sym_ns = to_yf_ticker(stock_input)
    
    with st.spinner(f"Loading {interval} data for {stock_input}..."):
        df = fetch_ohlcv(sym_ns, interval=interval)

    if df.empty: st.error("Failed to fetch data."); return
    df = add_indicators(df)
    sig = classify_hma_signal(df)
    quote = fetch_live_quote(sym
