"""
app.py — Trading Altimeter
Main application entry point. Handles routing between pages,
sidebar navigation, and renders all feature modules.

Run with: streamlit run app.py
"""

import datetime
import logging

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ── App config (MUST be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="Trading Altimeter",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils import (
    inject_css, NSE_250, NIFTY_50, to_yf_ticker,
    render_sidebar_header, render_banner, signal_badge, format_currency,
)
from indicators import (
    fetch_ohlcv, fetch_live_quote, add_indicators,
    classify_hma_signal, batch_hma_status,
)
from backtester import run_backtest, build_price_chart, build_equity_curve
from news_sentiment import get_news_with_sentiment
from watchlist import render_watchlist_page
from portfolio import render_portfolio_page
from dhan_broker import render_order_panel

logger = logging.getLogger(__name__)

# ── Inject CSS ────────────────────────────────────────────────────────────
inject_css()

# ── Session state defaults ────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "Dashboard"
if "selected_stock" not in st.session_state:
    st.session_state["selected_stock"] = "RELIANCE"
if "paper_mode" not in st.session_state:
    st.session_state["paper_mode"] = True


# ===========================================================================
# SIDEBAR
# ===========================================================================

render_sidebar_header()

with st.sidebar:
    st.markdown("---")
    pages = ["Dashboard", "Stock Analysis", "Backtester",
             "HMA Scanner", "Watchlist", "Portfolio"]
    icons = ["🏠", "📈", "🔬", "🛰", "⭐", "💼"]
    for icon, page in zip(icons, pages):
        if st.button(f"{icon} {page}", use_container_width=True,
                     key=f"nav_{page}"):
            st.session_state["page"] = page
            st.rerun()

    st.markdown("---")
    # Market clock
    now_ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    market_open = now_ist.replace(hour=9, minute=15, second=0)
    market_close = now_ist.replace(hour=15, minute=30, second=0)
    is_open = (market_open <= now_ist <= market_close
               and now_ist.weekday() < 5)
    mkt_color = "#16A34A" if is_open else "#DC2626" # Light Mode Green / Red
    mkt_label = "● MARKET OPEN" if is_open else "● MARKET CLOSED"
    st.markdown(
        f'<div style="text-align:center;font-size:0.75rem;'
        f'color:{mkt_color};font-weight:700">{mkt_label}</div>'
        f'<div style="text-align:center;font-size:0.7rem;color:#6B7280">' # Soft Grey
        f'IST {now_ist.strftime("%H:%M:%S")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

# Broker order panel (always visible in sidebar)
render_order_panel(symbol=st.session_state.get("selected_stock", ""))

page = st.session_state["page"]


# ===========================================================================
# PAGE: DASHBOARD
# ===========================================================================

def render_dashboard():
    render_banner()

    st.markdown('<div class="section-title">📡 LIVE MARKET OVERVIEW — NSE 250</div>',
                unsafe_allow_html=True)

    # Nifty 50 index quick info (index-level)
    try:
        nifty_data = fetch_live_quote("^NSEI")
        sensex_data = fetch_live_quote("^BSESN")
        col1, col2, col3 = st.columns(3)
        with col1:
            color = "#16A34A" if nifty_data["change_pct"] >= 0 else "#DC2626"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">NIFTY 50</div>
                <div class="metric-value">₹{nifty_data['ltp']:,.2f}</div>
                <div style="color:{color};font-size:0.85rem;font-weight:700">
                    {nifty_data['change_pct']:+.2f}%</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            color = "#16A34A" if sensex_data["change_pct"] >= 0 else "#DC2626"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">SENSEX</div>
                <div class="metric-value">₹{sensex_data['ltp']:,.2f}</div>
                <div style="color:{color};font-size:0.85rem;font-weight:700">
                    {sensex_data['change_pct']:+.2f}%</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            vix_data = fetch_live_quote("^INDIAVIX")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">INDIA VIX</div>
                <div class="metric-value">{vix_data['ltp']:.2f}</div>
                <div style="color:#6B7280;font-size:0.85rem">Volatility Index</div>
            </div>""", unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("<br>", unsafe_allow_html=True)

    # Stock grid — fetch ONLY live price/change (no heavy indicators)
    st.markdown("**Live Prices — click a stock to analyse**")

    # Batch fetch with progress indicator
    selected_batch = st.selectbox(
        "Show stocks from:",
        ["Nifty 50", "Next 50", "F&O Stocks (101-150)", "F&O Stocks (151-200)",
         "F&O Stocks (201-250)"],
        label_visibility="collapsed",
    )
    batch_map = {
        "Nifty 50": NSE_250[:50],
        "Next 50": NSE_250[50:100],
        "F&O Stocks (101-150)": NSE_250[100:150],
        "F&O Stocks (151-200)": NSE_250[150:200],
        "F&O Stocks (201-250)": NSE_250[200:250],
    }
    display_stocks = batch_map[selected_batch]

    quotes = []
    progress = st.progress(0, text="Fetching live prices...")
    for i, sym in enumerate(display_stocks):
        q = fetch_live_quote(to_yf_ticker(sym))
        quotes.append(q)
        progress.progress((i + 1) / len(display_stocks),
                          text=f"Fetching {sym}...")
    progress.empty()

    # Render grid — 5 columns
    num_cols = 5
    for row_start in range(0, len(quotes), num_cols):
        row_quotes = quotes[row_start: row_start + num_cols]
        cols = st.columns(num_cols)
        for col, q in zip(cols, row_quotes):
            with col:
                sym = q["symbol"]
                chg = q["change_pct"]
                ltp = q["ltp"]
                color = "#16A34A" if chg >= 0 else "#DC2626"
                sign = "+" if chg >= 0 else ""
                # Clickable card
                if st.button(
                    f"{sym}\n₹{ltp:,.1f}  {sign}{chg:.2f}%",
                    key=f"grid_{sym}",
                    help=f"Analyse {sym}",
                    use_container_width=True,
                ):
                    st.session_state["selected_stock"] = sym
                    st.session_state["page"] = "Stock Analysis"
                    st.rerun()


# ===========================================================================
# PAGE: STOCK ANALYSIS
# ===========================================================================

def render_stock_analysis():
    render_banner()

    # ── Stock selector ────────────────────────────────────────────────────
    col_search, col_interval = st.columns([3, 1])
    with col_search:
        stock_input = st.selectbox(
            "Select or search NSE stock",
            options=NSE_250,
            index=NSE_250.index(st.session_state["selected_stock"])
                if st.session_state["selected_stock"] in NSE_250 else 0,
        )
    with col_interval:
        interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)

    if stock_input != st.session_state["selected_stock"]:
        st.session_state["selected_stock"] = stock_input

    symbol = st.session_state["selected_stock"]
    symbol_ns = to_yf_ticker(symbol)

    # ── Fetch & compute ───────────────────────────────────────────────────
    with st.spinner(f"Loading {symbol}..."):
        df = fetch_ohlcv(symbol_ns, period="2y", interval=interval)

    if df.empty:
        st.error(f"Could not fetch data for {symbol}. "
                 "The stock may be delisted or yfinance unavailable.")
        return

    df = add_indicators(df)
    sig = classify_hma_signal(df)

    # ── Header: signal + quick stats ──────────────────────────────────────
    quote = fetch_live_quote(symbol_ns)
    chg_color = "#16A34A" if quote["change_pct"] >= 0 else "#DC2626"

    col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{symbol}</div>
            <div class="metric-value">₹{quote['ltp']:,.2f}</div>
            <div style="color:{chg_color};font-size:0.85rem;font-weight:700">
                {quote['change_pct']:+.2f}% today</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">200 HMA</div>
            <div class="metric-value">₹{sig['hma_value']:,.2f}</div>
            <div style="color:#6B7280;font-size:0.75rem">{sig['last_date']}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        dist_color = "#16A34A" if sig["distance_pct"] >= 0 else "#DC2626"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Distance to HMA</div>
            <div class="metric-value" style="color:{dist_color}">
                {sig['distance_pct']:+.2f}%</div>
            <div style="color:#6B7280;font-size:0.75rem">
                {'Above' if sig['above_hma'] else 'Below'} HMA</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(
            f'<div class="ta-card" style="text-align:center;padding:1.2rem">'
            f'<div class="metric-label">HMA SIGNAL</div>'
            f'<div style="margin-top:8px">{signal_badge(sig["signal"])}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main 4-panel chart ────────────────────────────────────────────────
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.15, 0.15, 0.15],
        vertical_spacing=0.02,
        subplot_titles=[f"{symbol} — Price + 200 HMA", "Volume", "RSI (14)", "MACD"],
    )

    # Row 1: Candlestick + HMA + EMA (Light Mode Colors)
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color="#16A34A", # Standard Green
        decreasing_line_color="#DC2626", # Standard Red
        name="Price", showlegend=False,
    ), row=1, col=1)

    # 200 HMA — thick gold/amber (stands out on white)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["HMA_200"],
        line=dict(color="#D97706", width=3),
        name="200 HMA",
    ), row=1, col=1)

    if "EMA_20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["EMA_20"],
            line=dict(color="#2563EB", width=1.2, dash="dot"),
            name="EMA 20",
        ), row=1, col=1)

    if "EMA_50" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["EMA_50"],
            line=dict(color="#F59E0B", width=1.2, dash="dot"),
            name="EMA 50",
        ), row=1, col=1)

    # Annotation arrow for HMA crossover signal
    if sig["signal"] in ("BULLISH", "BEARISH"):
        try:
            last_row = df.dropna(subset=["HMA_200"]).iloc[-1]
            arrow_color = "#16A34A" if sig["signal"] == "BULLISH" else "#DC2626"
            ay_offset = -50 if sig["signal"] == "BULLISH" else 50
            label = "🚀 BREAKOUT" if sig["signal"] == "BULLISH" else "📉 BREAKDOWN"
            fig.add_annotation(
                x=last_row.name,
                y=float(last_row["Close"]),
                text=label,
                showarrow=True,
                arrowhead=2,
                arrowcolor=arrow_color,
                arrowwidth=2,
                ax=0, ay=ay_offset,
                font=dict(color=arrow_color, size=12),
                row=1, col=1,
            )
        except Exception:
            pass

    # Row 2: Volume
    vol_colors = [
        "#16A34A" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#DC2626"
        for i in range(len(df))
    ]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"],
        marker_color=vol_colors,
        name="Volume", showlegend=False,
    ), row=2, col=1)

    # Row 3: RSI
    if "RSI_14" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["RSI_14"],
            line=dict(color="#2563EB", width=1.5),
            name="RSI", showlegend=False,
        ), row=3, col=1)
        fig.add_hline(y=70, line_color="#DC2626", line_dash="dash",
                      line_width=1, row=3, col=1)
        fig.add_hline(y=30, line_color="#16A34A", line_dash="dash",
                      line_width=1, row=3, col=1)

    # Row 4: MACD
    if "MACD" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MACD"],
            line=dict(color="#2563EB", width=1.5),
            name="MACD", showlegend=False,
        ), row=4, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MACD_Signal"],
            line=dict(color="#DC2626", width=1.5),
            name="Signal", showlegend=False,
        ), row=4, col=1)
        hist_colors = [
            "#16A34A" if v >= 0 else "#DC2626"
            for v in df["MACD_Hist"].fillna(0)
        ]
        fig.add_trace(go.Bar(
            x=df.index, y=df["MACD_Hist"],
            marker_color=hist_colors,
            name="MACD Hist", showlegend=False,
        ), row=4, col=1)

    fig.update_layout(
        height=800,
        template="plotly_white",
        paper_bgcolor="#FAF9F6",  # Matches Light Cream
        plot_bgcolor="#FFFFFF",    # White chart area
        font=dict(color="#1F2937", size=11), # Dark grey text
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=20, t=60, b=20),
    )
    # Style subplot title fonts
    for annotation in fig.layout.annotations:
        annotation.font.color = "#6B7280"
        annotation.font.size = 11

    st.plotly_chart(fig, use_container_width=True)

    # ── News & Sentiment ──────────────────────────────────────────────────
    with st.expander("📰 Latest News & Sentiment Analysis", expanded=False):
        with st.spinner("Fetching news..."):
            news = get_news_with_sentiment(symbol)

        if not news:
            st.info("No news found for this stock.")
        else:
            for item in news:
                tag_class = {
                    "POSITIVE": "tag-positive",
                    "NEGATIVE": "tag-negative",
                    "NEUTRAL": "tag-neutral",
                }.get(item.get("label", "NEUTRAL"), "tag-neutral")

                headline = item.get("headline", "")
                source = item.get("source", "")
                date_str = item.get("datetime", "")
                url = item.get("url", "#")

                st.markdown(
                    f'<div style="padding:8px 0;border-bottom:1px solid #E5E7EB">'
                    f'<span class="{tag_class}">{item.get("label", "NEUTRAL")}</span>&nbsp;'
                    f'<a href="{url}" target="_blank" '
                    f'style="color:#1F2937;text-decoration:none;font-size:0.88rem">'
                    f'{headline}</a><br>'
                    f'<span style="font-size:0.72rem;color:#6B7280">'
                    f'{source} · {date_str}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ===========================================================================
# PAGE: BACKTESTER
# ===========================================================================

def render_backtester():
    render_banner()
    st.markdown('<div class="section-title">🔬 STRATEGY BACKTESTER — 200 HMA CROSSOVER</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="ta-card" style="font-size:0.82rem;color:#6B7280">
        <strong style="color:#2563EB">Strategy:</strong>
        Buy when daily close crosses <strong>above</strong> the 200 HMA.
        Sell when it crosses <strong>below</strong>.
        100% capital allocation, compounding, no slippage.
    </div>
    """, unsafe_allow_html=True)

    # ── Inputs ────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        bt_symbol = st.selectbox("Select Stock (Nifty 50)", NIFTY_50)
    with col2:
        bt_start = st.date_input(
            "Start Date",
            value=datetime.date.today() - datetime.timedelta(days=3 * 365),
            min_value=datetime.date(2010, 1, 1),
        )
    with col3:
        bt_end = st.date_input(
            "End Date",
            value=datetime.date.today(),
        )
    with col4:
        capital = st.number_input(
            "Initial Capital (₹)",
            min_value=10_000,
            max_value=10_000_000,
            value=100_000,
            step=10_000,
        )

    run_btn = st.button("▶ Run Backtest", use_container_width=True)

    if not run_btn:
        st.info("Configure inputs above and click **Run Backtest** to begin.")
        return

    with st.spinner(f"Running backtest for {bt_symbol}..."):
        result = run_backtest(
            bt_symbol,
            str(bt_start),
            str(bt_end),
            float(capital),
        )

    if result.get("error"):
        st.error(result["error"])
        return

    metrics = result["metrics"]
    trades_df = result["trades"]
    equity_df = result["equity_curve"]

    # ── Metrics cards ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(6)
    net_color = "#16A34A" if metrics["net_profit_inr"] >= 0 else "#DC2626"
    cards = [
        ("Total Trades", str(metrics["total_trades"]), "#1F2937"),
        ("Win Rate", f"{metrics['win_rate']}%", "#16A34A"),
        ("Avg Win", f"{metrics['avg_win']:+.2f}%", "#16A34A"),
        ("Avg Loss", f"{metrics['avg_loss']:+.2f}%", "#DC2626"),
        ("Max Drawdown", f"{metrics['max_drawdown']:.2f}%", "#DC2626"),
        ("Net P&L",
         f"₹{metrics['net_profit_inr']:,.0f} ({metrics['net_profit_pct']:+.1f}%)",
         net_color),
    ]
    for col, (label, value, color) in zip(cols, cards):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};font-size:1.05rem">{value}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────
    price_fig = build_price_chart(result["df"], trades_df, bt_symbol)
    st.plotly_chart(price_fig, use_container_width=True)

    equity_fig = build_equity_curve(equity_df, float(capital), bt_symbol)
    st.plotly_chart(equity_fig, use_container_width=True)

    # ── Trade log ─────────────────────────────────────────────────────────
    if not trades_df.empty:
        with st.expander("📋 Detailed Trade Log", expanded=False):
            display_df = trades_df.copy()
            display_df["Result"] = display_df["Result"].apply(
                lambda x: "🟢 WIN" if "WIN" in x else "🔴 LOSS"
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True)


# ===========================================================================
# PAGE: HMA SCANNER
# ===========================================================================

def render_scanner():
    render_banner()
    st.markdown('<div class="section-title">🛰 200 HMA SCANNER — NSE 250</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="ta-card" style="font-size:0.82rem;color:#6B7280">
        Scans all 250 stocks for 200 HMA signals.
        <strong style="color:#DC2626">Heavy operation — may take 2-5 minutes.</strong>
        Results are cached for 5 minutes.
    </div>""", unsafe_allow_html=True)

    filter_col, _ = st.columns([2, 3])
    with filter_col:
        signal_filter = st.multiselect(
            "Filter by signal",
            ["BULLISH", "BEARISH", "APPROACHING"],
            default=["BULLISH", "BEARISH", "APPROACHING"],
        )

    scan_btn = st.button("🔍 Start 200 HMA Scan", use_container_width=False)

    if not scan_btn and "scan_results" not in st.session_state:
        st.info("Click **Start 200 HMA Scan** to scan all 250 stocks.")
        return

    if scan_btn:
        results = []
        progress = st.progress(0, text="Scanning stocks...")
        for i, sym in enumerate(NSE_250):
            data = batch_hma_status(to_yf_ticker(sym))
            results.append(data)
            progress.progress((i + 1) / len(NSE_250),
                              text=f"Scanned {sym} ({i+1}/{len(NSE_250)})")
        progress.empty()
        st.session_state["scan_results"] = results

    results = st.session_state.get("scan_results", [])
    if not results:
        return

    # Filter
    filtered = [r for r in results
                if r.get("signal") in signal_filter]

    bullish = [r for r in filtered if r.get("signal") == "BULLISH"]
    bearish = [r for r in filtered if r.get("signal") == "BEARISH"]
    approaching = [r for r in filtered if r.get("signal") == "APPROACHING"]

    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="metric-card">'
                  f'<div class="metric-label">🚀 Bullish Breakouts</div>'
                  f'<div class="metric-value" style="color:#16A34A">{len(bullish)}</div>'
                  f'</div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card">'
                  f'<div class="metric-label">📉 Bearish Breakdowns</div>'
                  f'<div class="metric-value" style="color:#DC2626">{len(bearish)}</div>'
                  f'</div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card">'
                  f'<div class="metric-label">👀 Approaching HMA</div>'
                  f'<div class="metric-value" style="color:#2563EB">{len(approaching)}</div>'
                  f'</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not filtered:
        st.info("No stocks match the selected filters.")
        return

    # Build display DataFrame
    rows = []
    for r in filtered:
        sig = r.get("signal", "N/A")
        chg = r.get("change_pct", 0)
        rows.append({
            "Symbol": r.get("symbol", ""),
            "Signal": sig,
            "LTP (₹)": r.get("ltp", 0),
            "Day Change %": f"{chg:+.2f}%",
            "HMA Value (₹)": r.get("hma_value", 0),
            "Distance %": f"{r.get('distance_pct', 0):+.2f}%",
            "Above HMA": "✅" if r.get("above_hma") else "❌",
        })

    scan_df = pd.DataFrame(rows)
    scan_df = scan_df.sort_values("Signal")

    st.dataframe(
        scan_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Signal": st.column_config.TextColumn("Signal", width="medium"),
            "LTP (₹)": st.column_config.NumberColumn("LTP (₹)", format="₹%.2f"),
            "HMA Value (₹)": st.column_config.NumberColumn("HMA (₹)", format="₹%.2f"),
        },
    )

    # Analyse button per row
    st.markdown("**Click to analyse a stock from results:**")
    sym_options = [r["Symbol"] for r in rows]
    selected_from_scan = st.selectbox("Jump to analysis", sym_options,
                                      label_visibility="collapsed")
    if st.button(f"📊 Analyse {selected_from_scan}"):
        st.session_state["selected_stock"] = selected_from_scan
        st.session_state["page"] = "Stock Analysis"
        st.rerun()


# ===========================================================================
# ROUTER
# ===========================================================================

if page == "Dashboard":
    render_dashboard()
elif page == "Stock Analysis":
    render_stock_analysis()
elif page == "Backtester":
    render_backtester()
elif page == "HMA Scanner":
    render_scanner()
elif page == "Watchlist":
    render_watchlist_page()
elif page == "Portfolio":
    render_portfolio_page()
