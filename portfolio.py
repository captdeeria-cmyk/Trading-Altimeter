"""
portfolio.py — Trading Altimeter
Portfolio holdings management and P&L calculations.
Tracks positions added manually or via paper/live trading.

Storage: portfolio.json in the working directory.

P&L Formulas:
    Unrealised P&L ₹  = (LTP - Avg Buy Price) × Qty
    Unrealised P&L %  = ((LTP - Avg Buy Price) / Avg Buy Price) × 100
    Day P&L ₹         = (LTP - Prev Close) × Qty
    Portfolio Return % = (Current Value - Cost) / Cost × 100
"""

import json
import os
import logging
import datetime

import streamlit as st
import pandas as pd

from indicators import fetch_live_quote
from utils import to_yf_ticker, format_currency

logger = logging.getLogger(__name__)
PORTFOLIO_FILE = "portfolio.json"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_portfolio() -> list:
    """Load portfolio from JSON. Returns list of holding dicts."""
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    try:
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Portfolio load error: {e}")
        return []


def save_portfolio(holdings: list) -> None:
    """Save portfolio list to JSON."""
    try:
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(holdings, f, indent=2)
    except Exception as e:
        logger.warning(f"Portfolio save error: {e}")


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def add_holding(symbol: str, qty: int, avg_price: float) -> tuple[bool, str]:
    """
    Add or update a holding in the portfolio.
    If symbol exists, computes new weighted average price.
    """
    symbol = symbol.upper().strip()
    if qty <= 0 or avg_price <= 0:
        return False, "Quantity and price must be positive."

    holdings = load_portfolio()

    # Check if exists — if so, average down/up
    for h in holdings:
        if h["symbol"] == symbol:
            old_cost = h["avg_price"] * h["qty"]
            new_cost = avg_price * qty
            total_qty = h["qty"] + qty
            h["avg_price"] = round((old_cost + new_cost) / total_qty, 2)
            h["qty"] = total_qty
            h["buy_date"] = h.get("buy_date", str(datetime.date.today()))
            save_portfolio(holdings)
            return True, f"Updated {symbol}: {total_qty} qty @ ₹{h['avg_price']}"

    holdings.append({
        "symbol": symbol,
        "qty": qty,
        "avg_price": round(avg_price, 2),
        "buy_date": str(datetime.date.today()),
    })
    save_portfolio(holdings)
    return True, f"Added {symbol}: {qty} qty @ ₹{avg_price}"


def remove_holding(symbol: str) -> None:
    """Remove a holding from portfolio."""
    holdings = load_portfolio()
    holdings = [h for h in holdings if h["symbol"] != symbol.upper()]
    save_portfolio(holdings)


# ---------------------------------------------------------------------------
# Enrichment
# ---------------------------------------------------------------------------

def get_portfolio_with_pnl() -> list:
    """
    Fetch live prices for all holdings and compute P&L metrics.

    Returns:
        list of dicts with all holding data + live P&L calculations.
    """
    holdings = load_portfolio()
    if not holdings:
        return []

    enriched = []
    for h in holdings:
        symbol = h["symbol"]
        symbol_ns = to_yf_ticker(symbol)
        quote = fetch_live_quote(symbol_ns)
        ltp = quote["ltp"] or h["avg_price"]
        prev_close = quote["prev_close"] or ltp
        qty = h["qty"]
        avg = h["avg_price"]

        invested = avg * qty
        current_value = ltp * qty
        unrealised_inr = current_value - invested
        unrealised_pct = ((ltp - avg) / avg) * 100 if avg > 0 else 0.0
        day_pnl_inr = (ltp - prev_close) * qty

        enriched.append({
            "symbol": symbol,
            "qty": qty,
            "avg_price": avg,
            "ltp": ltp,
            "invested": round(invested, 2),
            "current_value": round(current_value, 2),
            "unrealised_inr": round(unrealised_inr, 2),
            "unrealised_pct": round(unrealised_pct, 2),
            "day_pnl_inr": round(day_pnl_inr, 2),
            "change_pct": quote["change_pct"],
            "buy_date": h.get("buy_date", ""),
        })

    return enriched


def portfolio_summary(enriched: list) -> dict:
    """Compute portfolio-level aggregate metrics."""
    if not enriched:
        return {}

    total_invested = sum(h["invested"] for h in enriched)
    total_current = sum(h["current_value"] for h in enriched)
    total_unrealised = total_current - total_invested
    total_day_pnl = sum(h["day_pnl_inr"] for h in enriched)
    overall_pct = ((total_current - total_invested) / total_invested * 100
                   if total_invested > 0 else 0.0)

    return {
        "total_invested": round(total_invested, 2),
        "total_current": round(total_current, 2),
        "total_unrealised_inr": round(total_unrealised, 2),
        "total_unrealised_pct": round(overall_pct, 2),
        "total_day_pnl": round(total_day_pnl, 2),
        "holdings_count": len(enriched),
    }


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

def render_portfolio_page():
    """Render the Portfolio Holdings & P&L page."""
    st.markdown('<div class="section-title">💼 MY PORTFOLIO</div>',
                unsafe_allow_html=True)

    # ── Add Holding Form ──────────────────────────────────────────────────
    with st.expander("➕ Add / Update Holding", expanded=False):
        c1, c2, c3, c4 = st.columns([2, 1, 2, 1])
        with c1:
            add_sym = st.text_input("NSE Symbol", placeholder="e.g. TCS")
        with c2:
            add_qty = st.number_input("Quantity", min_value=1, value=1, step=1)
        with c3:
            add_price = st.number_input("Avg Buy Price (₹)", min_value=0.01,
                                        value=100.0, step=0.5)
        with c4:
            st.write("")
            st.write("")
            if st.button("Add Holding"):
                if add_sym:
                    ok, msg = add_holding(add_sym, add_qty, add_price)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # ── Load & compute ────────────────────────────────────────────────────
    with st.spinner("Fetching live prices..."):
        holdings = get_portfolio_with_pnl()

    if not holdings:
        st.markdown("""
        <div class="ta-card" style="text-align:center;padding:2rem;color:#8A8D94">
            <div style="font-size:2rem">💼</div>
            <div style="margin-top:0.5rem">No holdings yet.</div>
            <div style="font-size:0.8rem">Add a position using the form above.</div>
        </div>""", unsafe_allow_html=True)
        return

    summary = portfolio_summary(holdings)

    # ── Summary cards ─────────────────────────────────────────────────────
    cols = st.columns(5)
    cards = [
        ("Invested", format_currency(summary["total_invested"]), "#00D4FF"),
        ("Current Value", format_currency(summary["total_current"]), "#00D4FF"),
        ("Unrealised P&L",
         f'{format_currency(summary["total_unrealised_inr"])} '
         f'({summary["total_unrealised_pct"]:+.2f}%)',
         "#00E676" if summary["total_unrealised_inr"] >= 0 else "#FF1744"),
        ("Day P&L",
         f'{format_currency(summary["total_day_pnl"])}',
         "#00E676" if summary["total_day_pnl"] >= 0 else "#FF1744"),
        ("Holdings", str(summary["holdings_count"]), "#8A8D94"),
    ]
    for col, (label, value, color) in zip(cols, cards):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};font-size:1rem">{value}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Holdings table ────────────────────────────────────────────────────
    for h in holdings:
        pnl_color = "#00E676" if h["unrealised_inr"] >= 0 else "#FF1744"
        pnl_sign = "+" if h["unrealised_inr"] >= 0 else ""

        with st.container():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 1, 1, 1, 2, 2, 1])
            with c1:
                st.markdown(f"**{h['symbol']}**<br>"
                            f"<span style='font-size:0.75rem;color:#8A8D94'>"
                            f"Since {h['buy_date']}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"{h['qty']} qty")
            with c3:
                st.markdown(f"₹{h['avg_price']:,.2f}<br>"
                            f"<span style='font-size:0.7rem;color:#8A8D94'>avg cost</span>",
                            unsafe_allow_html=True)
            with c4:
                day_color = "#00E676" if h["change_pct"] >= 0 else "#FF1744"
                st.markdown(f"₹{h['ltp']:,.2f}<br>"
                            f"<span style='font-size:0.7rem;color:{day_color}'>"
                            f"{h['change_pct']:+.2f}% today</span>",
                            unsafe_allow_html=True)
            with c5:
                st.markdown(
                    f'<span style="color:{pnl_color};font-weight:700">'
                    f'{pnl_sign}₹{h["unrealised_inr"]:,.2f}</span><br>'
                    f'<span style="font-size:0.75rem;color:{pnl_color}">'
                    f'{pnl_sign}{h["unrealised_pct"]:.2f}%</span>',
                    unsafe_allow_html=True)
            with c6:
                st.markdown(f"Inv: {format_currency(h['invested'])}<br>"
                            f"Curr: {format_currency(h['current_value'])}",
                            unsafe_allow_html=True)
            with c7:
                if st.button("🗑", key=f"del_{h['symbol']}"):
                    remove_holding(h["symbol"])
                    st.rerun()

        st.markdown('<hr style="margin:4px 0;border-color:#2A2D35">',
                    unsafe_allow_html=True)