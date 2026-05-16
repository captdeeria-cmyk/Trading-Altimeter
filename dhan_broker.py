"""
dhan_broker.py — Trading Altimeter
Dhan broker integration via the dhanhq library.

Loads credentials from .env (DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN).
Supports:
 - Fetching account margins
 - Fetching holdings
 - Placing live orders (with confirmation checkbox + margin check)
 - Paper Trading Mode (default ON): intercepts orders, simulates P&L

Paper Trading Storage: paper_trades.json in working directory.
"""

import os
import json
import logging
import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

PAPER_TRADES_FILE = "paper_trades.json"

# ---------------------------------------------------------------------------
# Dhan client initialisation
# ---------------------------------------------------------------------------

def get_dhan_client():
    """
    Initialise and return DhanHQ client.
    Returns None if credentials are missing.
    """
    client_id = os.getenv("DHAN_CLIENT_ID", "")
    access_token = os.getenv("DHAN_ACCESS_TOKEN", "")

    if not client_id or not access_token:
        return None

    try:
        from dhanhq import dhanhq
        client = dhanhq(client_id, access_token)
        return client
    except Exception as e:
        logger.warning(f"Dhan client init error: {e}")
        return None


# ---------------------------------------------------------------------------
# Account data
# ---------------------------------------------------------------------------

def fetch_margins() -> dict:
    """Fetch available margin from Dhan account."""
    client = get_dhan_client()
    if not client:
        return {"available_balance": 0.0, "used_margin": 0.0, "error": "No API credentials"}
    try:
        resp = client.get_fund_limits()
        if isinstance(resp, dict) and resp.get("status") == "success":
            data = resp.get("data", {})
            return {
                "available_balance": float(data.get("availabelBalance", 0) or 0),
                "used_margin": float(data.get("utilizedAmount", 0) or 0),
                "total_balance": float(data.get("sodLimit", 0) or 0),
                "error": None,
            }
        return {"available_balance": 0.0, "used_margin": 0.0, "error": str(resp)}
    except Exception as e:
        return {"available_balance": 0.0, "used_margin": 0.0, "error": str(e)}


def fetch_holdings() -> list:
    """Fetch current holdings from Dhan account."""
    client = get_dhan_client()
    if not client:
        return []
    try:
        resp = client.get_holdings()
        if isinstance(resp, dict) and resp.get("status") == "success":
            return resp.get("data", [])
        return []
    except Exception as e:
        logger.warning(f"Holdings fetch error: {e}")
        return []


# ---------------------------------------------------------------------------
# Paper trading
# ---------------------------------------------------------------------------

def load_paper_trades() -> list:
    if not os.path.exists(PAPER_TRADES_FILE):
        return []
    try:
        with open(PAPER_TRADES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_paper_trades(trades: list) -> None:
    try:
        with open(PAPER_TRADES_FILE, "w") as f:
            json.dump(trades, f, indent=2)
    except Exception as e:
        logger.warning(f"Paper trade save error: {e}")


def paper_trade(symbol: str, qty: int, order_type: str,
                transaction_type: str, price: float = 0.0) -> dict:
    """
    Simulate a paper trade. Stores in paper_trades.json.

    Args:
        symbol         : NSE symbol
        qty            : Number of shares
        order_type     : 'MARKET' or 'LIMIT'
        transaction_type: 'BUY' or 'SELL'
        price          : Limit price (0 for MARKET)

    Returns:
        dict with order_id, status, simulated_price
    """
    from indicators import fetch_live_quote
    from utils import to_yf_ticker

    quote = fetch_live_quote(to_yf_ticker(symbol))
    sim_price = price if (order_type == "LIMIT" and price > 0) else quote["ltp"]

    order = {
        "order_id": f"PAPER-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "symbol": symbol,
        "qty": qty,
        "transaction_type": transaction_type,
        "order_type": order_type,
        "price": round(sim_price, 2),
        "value": round(sim_price * qty, 2),
        "timestamp": str(datetime.datetime.now()),
        "status": "SIMULATED",
    }

    trades = load_paper_trades()
    trades.append(order)
    save_paper_trades(trades)

    return order


# ---------------------------------------------------------------------------
# Live order placement
# ---------------------------------------------------------------------------

def place_live_order(symbol: str, qty: int, order_type: str,
                     transaction_type: str, product: str,
                     price: float = 0.0) -> dict:
    """
    Place a live order via Dhan API.

    Args:
        symbol          : NSE symbol
        qty             : Quantity
        order_type      : 'MARKET' or 'LIMIT'
        transaction_type: 'BUY' or 'SELL'
        product         : 'CNC' (delivery) or 'MIS' (intraday)
        price           : Limit price (0 for MARKET)

    Returns:
        dict with status and order details.
    """
    client = get_dhan_client()
    if not client:
        return {"status": "ERROR", "message": "No Dhan credentials found in .env"}

    try:
        from dhanhq import dhanhq

        resp = client.place_order(
            security_id=symbol,           # Dhan uses security_id; may need ISIN mapping
            exchange_segment=dhanhq.NSE,
            transaction_type=dhanhq.BUY if transaction_type == "BUY" else dhanhq.SELL,
            quantity=qty,
            order_type=dhanhq.MARKET if order_type == "MARKET" else dhanhq.LIMIT,
            product_type=dhanhq.CNC if product == "CNC" else dhanhq.INTRA,
            price=price,
        )
        return {"status": "SUCCESS", "data": resp}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


# ---------------------------------------------------------------------------
# Streamlit UI component
# ---------------------------------------------------------------------------

def render_order_panel(symbol: str = ""):
    """
    Render the broker order panel in the sidebar.

    Args:
        symbol: Pre-fill symbol from current chart view.
    """
    has_creds = bool(os.getenv("DHAN_CLIENT_ID")) and bool(os.getenv("DHAN_ACCESS_TOKEN"))

    # Paper trading toggle
    paper_mode = st.sidebar.toggle(
        "📄 Paper Trading Mode",
        value=st.session_state.get("paper_mode", True),
        help="ON = simulated trades only. OFF = real Dhan orders.",
    )
    st.session_state["paper_mode"] = paper_mode

    mode_label = "PAPER" if paper_mode else "LIVE"
    mode_color = "#00D4FF" if paper_mode else "#FF1744"
    st.sidebar.markdown(
        f'<div style="color:{mode_color};font-weight:700;font-size:0.75rem;'
        f'text-align:center;margin-bottom:8px">MODE: {mode_label}</div>',
        unsafe_allow_html=True,
    )

    with st.sidebar.expander("🛒 PLACE ORDER", expanded=False):
        order_sym = st.text_input("Symbol", value=symbol or "",
                                  placeholder="e.g. RELIANCE").upper()
        col1, col2 = st.columns(2)
        with col1:
            qty = st.number_input("Qty", min_value=1, value=1, step=1)
        with col2:
            order_type = st.selectbox("Type", ["MARKET", "LIMIT"])

        col3, col4 = st.columns(2)
        with col3:
            txn = st.selectbox("Action", ["BUY", "SELL"])
        with col4:
            product = st.selectbox("Product", ["CNC", "MIS"])

        limit_price = 0.0
        if order_type == "LIMIT":
            limit_price = st.number_input("Limit Price (₹)", min_value=0.01,
                                          value=100.0, step=0.5)

        confirm = st.checkbox("✅ I confirm this trade")

        place_btn = st.button("🚀 Place Order", use_container_width=True)

        if place_btn:
            if not confirm:
                st.error("Please confirm the trade first.")
            elif not order_sym:
                st.error("Enter a valid symbol.")
            elif paper_mode:
                result = paper_trade(order_sym, qty, order_type, txn, limit_price)
                st.success(
                    f"📄 Paper order placed!\n"
                    f"{txn} {qty} × {order_sym} @ ₹{result['price']}\n"
                    f"Order ID: {result['order_id']}"
                )
            else:
                if not has_creds:
                    st.error("Live trading requires DHAN_CLIENT_ID and "
                             "DHAN_ACCESS_TOKEN in your .env file.")
                else:
                    # Check margin
                    margins = fetch_margins()
                    if margins.get("error"):
                        st.error(f"Margin check failed: {margins['error']}")
                    else:
                        st.info(f"Available balance: ₹{margins['available_balance']:,.2f}")
                        result = place_live_order(
                            order_sym, qty, order_type, txn, product, limit_price
                        )
                        if result["status"] == "SUCCESS":
                            st.success("✅ Live order placed via Dhan!")
                        else:
                            st.error(f"Order failed: {result.get('message')}")

    # ── Paper trade log ───────────────────────────────────────────────────
    if paper_mode:
        with st.sidebar.expander("📋 Paper Trade Log", expanded=False):
            trades = load_paper_trades()
            if not trades:
                st.caption("No paper trades yet.")
            else:
                for t in reversed(trades[-10:]):
                    color = "#00E676" if t["transaction_type"] == "BUY" else "#FF1744"
                    st.markdown(
                        f'<div style="font-size:0.72rem;padding:4px 0;'
                        f'border-bottom:1px solid #2A2D35">'
                        f'<span style="color:{color};font-weight:700">'
                        f'{t["transaction_type"]}</span> '
                        f'{t["qty"]} × {t["symbol"]} @ ₹{t["price"]}<br>'
                        f'<span style="color:#8A8D94">{t["timestamp"][:16]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )