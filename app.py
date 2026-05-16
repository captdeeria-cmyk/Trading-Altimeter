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
    quote = fetch_live_quote(sym_ns)
    
    # HEADER METRICS
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f"<div class='metric-card'><div class='metric-label'>{stock_input}</div><div class='metric-value'>₹{quote['ltp']:,.2f}</div><div style='color:{'#16A34A' if quote['change_pct']>=0 else '#DC2626'}; font-weight:700'>{quote['change_pct']:+.2f}%</div></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-card'><div class='metric-label'>200 HMA</div><div class='metric-value'>₹{sig['hma_value']:,.2f}</div></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Distance to HMA</div><div class='metric-value' style='color:{'#16A34A' if sig['distance_pct']>=0 else '#DC2626'}'>{sig['distance_pct']:+.2f}%</div></div>", unsafe_allow_html=True)
    with col4: st.markdown(f"<div class='ta-card' style='text-align:center'><div class='metric-label'>SIGNAL</div><div style='margin-top:8px'>{signal_badge(sig['signal'])}</div></div>", unsafe_allow_html=True)

    # STRICT LIGHT MODE PLOTLY CHARTS
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, row_heights=[0.55, 0.15, 0.15, 0.15], vertical_spacing=0.02, subplot_titles=[f"{stock_input} ({interval})", "Volume", "RSI", "MACD"])
    
    # STRICT COLORS: Green/Red Candlesticks
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], increasing_line_color="#198754", decreasing_line_color="#DC3545"), row=1, col=1)
    
    # GOLD 200 HMA
    fig.add_trace(go.Scatter(x=df.index, y=df["HMA_200"], line=dict(color="#D4A017", width=3), name="200 HMA"), row=1, col=1)
    if "EMA_20" in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df["EMA_20"], line=dict(color="#2979FF", width=1.2, dash="dot"), name="EMA 20"), row=1, col=1)
    
    # VOLUME BARS (Green/Red)
    vol_colors = ["#198754" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#DC3545" for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=vol_colors, showlegend=False), row=2, col=1)
    
    # RSI (Blue)
    if "RSI_14" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI_14"], line=dict(color="#2979FF", width=1.5)), row=3, col=1)
        fig.add_hline(y=70, line_color="#DC3545", line_dash="dash", row=3, col=1)
        fig.add_hline(y=30, line_color="#198754", line_dash="dash", row=3, col=1)
    
    # MACD (Green/Red)
    if "MACD" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], line=dict(color="#2979FF", width=1.5)), row=4, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"], line=dict(color="#DC3545", width=1.5)), row=4, col=1)
        hist_colors = ["#198754" if v >= 0 else "#DC3545" for v in df["MACD_Hist"].fillna(0)]
        fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"], marker_color=hist_colors, showlegend=False), row=4, col=1)

    # FORCE WHITE THEME LAYOUT
    fig.update_layout(height=800, template="plotly_white", paper_bgcolor="#F8F9FA", plot_bgcolor="#FFFFFF", font=dict(color="#495057"), xaxis_rangeslider_visible=False, margin=dict(l=40, r=20, t=40, b=20))
    for annotation in fig.layout.annotations: annotation.font.color = "#6C757D"
    st.plotly_chart(fig, use_container_width=True)

def render_scanner():
    render_banner()
    if st.button("Run 200 HMA Scan (Takes 2 mins)", use_container_width=True):
        res = []
        for i, sym in enumerate(NSE_250):
            res.append(batch_hma_status(to_yf_ticker(sym)))
            st.progress((i+1)/len(NSE_250), text=f"Scanning {sym}...")
        st.dataframe(res)

def render_watchlist_page(): st.info("Watchlist feature loaded.")
def render_portfolio_page(): st.info("Portfolio feature loaded.")

if st.session_state["page"] == "Dashboard": render_dashboard()
elif st.session_state["page"] == "Stock Analysis": render_stock_analysis()
elif st.session_state["page"] == "HMA Scanner": render_scanner()
elif st.session_state["page"] == "Watchlist": render_watchlist_page()
elif st.session_state["page"] == "Portfolio": render_portfolio_page()
