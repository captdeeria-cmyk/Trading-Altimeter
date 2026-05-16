"""
watchlist.py — Trading Altimeter
Persistent watchlist management using a local JSON file.
The watchlist survives app restarts because it writes to disk immediately
on every add/remove operation.

File location: watchlist.json in the app's working directory.
"""

import json
import os
import logging

import streamlit as st

from indicators import fetch_live_quote, fetch_ohlcv, add_indicators, classify_hma_signal
from utils import to_yf_ticker

logger = logging.getLogger(__name__)

WATCHLIST_FILE = "watchlist.json"


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def load_watchlist() -> list:
    """Load watchlist symbols from JSON file. Returns empty list if missing."""
    if not os.path.exists(WATCHLIST_FILE):
        return []
    try:
        with open(WATCHLIST_FILE, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [str(s).upper().strip() for s in data if s]
        return []
    except Exception as e:
        logger.warning(f"Failed to load watchlist: {e}")
        return []


def save_watchlist(symbols: list) -> None:
    """Persist watchlist to JSON file immediately."""
    try:
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(symbols, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save watchlist: {e}")


def add_to_watchlist(symbol: str) -> tuple[bool, str]:
    """
    Add a symbol to the watchlist.

    Returns:
        (success: bool, message: str)
    """
    symbol = symbol.upper().strip()
    if not symbol:
        return False, "Please enter a valid symbol."

    watchlist = load_watchlist()

    if symbol in watchlist:
        return False, f"{symbol} is already in your watchlist."

    if len(watchlist) >= 50:
        return False, "Watchlist limit is 50 stocks."

    watchlist.append(symbol)
    save_watchlist(watchlist)
    return True, f"{symbol} added to watchlist."


def remove_from_watchlist(symbol: str) -> None:
    """Remove a symbol from the watchlist and save immediately."""
    watchlist = load_watchlist()
    watchlist = [s for s in watchlist if s != symbol.upper()]
    save_watchlist(watchlist)


# ---------------------------------------------------------------------------
# Watchlist data enrichment
# ---------------------------------------------------------------------------

def get_watchlist_data(symbols: list) -> list:
    """
    For each symbol in the watchlist, fetch:
    - Live LTP and day change %
    - 200 HMA signal (requires fetching 1y of data)

    This is heavier than the dashboard grid — watchlists are typically small
    (< 20 stocks) so full indicator calculation is acceptable.

    Returns:
        list of dicts with enriched data for each symbol.
    """
    results = []
    for symbol in symbols:
        try:
            symbol_ns = to_yf_ticker(symbol)

            # Live quote
            quote = fetch_live_quote(symbol_ns)

            # HMA signal
            df = fetch_ohlcv(symbol_ns, period="1y", interval="1d")
            if not df.empty:
                df = add_indicators(df)
                sig_data = classify_hma_signal(df)
            else:
                sig_data = {
                    "signal": "N/A", "hma_value": 0.0,
                    "distance_pct": 0.0, "above_hma": False,
                }

            results.append({
                "symbol": symbol,
                "ltp": quote["ltp"],
                "change_pct": quote["change_pct"],
                "hma_signal": sig_data.get("signal", "N/A"),
                "hma_value": sig_data.get("hma_value", 0.0),
                "distance_pct": sig_data.get("distance_pct", 0.0),
            })
        except Exception as e:
            logger.warning(f"Watchlist data error for {symbol}: {e}")
            results.append({
                "symbol": symbol,
                "ltp": 0.0,
                "change_pct": 0.0,
                "hma_signal": "ERROR",
                "hma_value": 0.0,
                "distance_pct": 0.0,
            })
    return results


# ---------------------------------------------------------------------------
# Streamlit UI component
# ---------------------------------------------------------------------------

def render_watchlist_page():
    """Render the full Watchlist page in Streamlit."""
    st.markdown('<div class="section-title">⭐ MY WATCHLIST</div>',
                unsafe_allow_html=True)

    # ── Add stock ──────────────────────────────────────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        new_symbol = st.text_input(
            "Add NSE Symbol",
            placeholder="e.g. RELIANCE, HDFCBANK, ZOMATO",
            label_visibility="collapsed",
        )
    with col2:
        add_btn = st.button("➕ Add to Watchlist", use_container_width=True)

    if add_btn and new_symbol:
        ok, msg = add_to_watchlist(new_symbol.strip().upper())
        if ok:
            st.success(msg)
            st.rerun()
        else:
            st.warning(msg)

    # ── Load & display ────────────────────────────────────────────────────
    watchlist = load_watchlist()

    if not watchlist:
        st.markdown("""
        <div class="ta-card" style="text-align:center;padding:2rem;color:#8A8D94">
            <div style="font-size:2rem">⭐</div>
            <div style="margin-top:0.5rem">Your watchlist is empty.</div>
            <div style="font-size:0.8rem;margin-top:0.25rem">
                Add NSE symbols above to track them here.
            </div>
        </div>""", unsafe_allow_html=True)
        return

    # Fetch enriched data
    with st.spinner("Fetching live data for your watchlist..."):
        data = get_watchlist_data(watchlist)

    if not data:
        st.info("Could not fetch data. Please check your internet connection.")
        return

    # ── Render table rows ─────────────────────────────────────────────────
    # Header
    cols = st.columns([2, 2, 2, 3, 2, 1, 1])
    headers = ["Symbol", "LTP (₹)", "Change %", "HMA Signal", "Dist. to HMA", "Analyze", "Remove"]
    for col, hdr in zip(cols, headers):
        col.markdown(f"**{hdr}**")

    st.divider()

    for row in data:
        symbol = row["symbol"]
        change_color = "#00E676" if row["change_pct"] >= 0 else "#FF1744"
        change_sign = "+" if row["change_pct"] >= 0 else ""

        signal_html = {
            "BULLISH":    '<span class="badge-bullish">🚀 BULLISH</span>',
            "BEARISH":    '<span class="badge-bearish">💀 BEARISH</span>',
            "APPROACHING":'<span class="badge-approaching">👀 APPROACHING</span>',
            "NEUTRAL":    '<span class="badge-neutral">— NEUTRAL</span>',
        }.get(row["hma_signal"], f'<span class="badge-neutral">{row["hma_signal"]}</span>')

        dist_color = "#00E676" if row["distance_pct"] >= 0 else "#FF1744"

        c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 2, 2, 3, 2, 1, 1])

        with c1:
            st.markdown(f"**{symbol}**")
        with c2:
            st.markdown(f"₹{row['ltp']:,.2f}")
        with c3:
            st.markdown(
                f'<span style="color:{change_color};font-weight:700">'
                f'{change_sign}{row["change_pct"]:.2f}%</span>',
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(signal_html, unsafe_allow_html=True)
        with c5:
            st.markdown(
                f'<span style="color:{dist_color}">'
                f'{row["distance_pct"]:+.2f}%</span>',
                unsafe_allow_html=True,
            )
        with c6:
            if st.button("📊", key=f"analyze_{symbol}", help=f"Analyze {symbol}"):
                st.session_state["selected_stock"] = symbol
                st.session_state["page"] = "Dashboard"
                st.rerun()
        with c7:
            if st.button("🗑", key=f"remove_{symbol}", help=f"Remove {symbol}"):
                remove_from_watchlist(symbol)
                st.rerun()

        st.markdown('<hr style="margin:4px 0;border-color:#2A2D35">', unsafe_allow_html=True)