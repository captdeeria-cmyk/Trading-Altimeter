"""
utils.py — Trading Altimeter
Shared layout elements, styling tokens, and the 250 NSE stock mapping dataset.
"""
import streamlit as st

def inject_css():
    """Inject global CSS rules for a clean, high-contrast Light Theme workspace."""
    st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    h1, h2, h3, h4, p, label { 
        color: #0F172A !important; 
    }
    .ta-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .badge-bullish {
        background: #DEF7EC; color: #03543F; padding: 4px 8px; border-radius: 4px; font-weight: 700; border: 1px solid #31C48D;
    }
    .badge-bearish {
        background: #FDE8E8; color: #9B1C1C; padding: 4px 8px; border-radius: 4px; font-weight: 700; border: 1px solid #F8B4B4;
    }
    .badge-approach {
        background: #FEF3C7; color: #92400E; padding: 4px 8px; border-radius: 4px; font-weight: 700; border: 1px solid #F59E0B;
    }
    .badge-neutral {
        background: #F1F5F9; color: #475569; padding: 4px 8px; border-radius: 4px; font-weight: 500; border: 1px solid #CBD5E1;
    }
    </style>
    """, unsafe_allow_html=True)

def render_banner():
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.75rem 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
        <div style="font-size: 1.75rem; font-weight: 900; color: #0F172A; letter-spacing: -0.02em;">✈ TRADING ALTIMETER</div>
        <div style="font-size: 0.95rem; color: #475569; margin-top: 4px; font-weight: 500;">Institutional-Grade Direct Dhan API Analytics Deck</div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_header():
    st.markdown("""
    <div style="padding: 10px 0px; border-bottom: 1px solid #E2E8F0; margin-bottom: 15px;">
        <div style="font-size: 1.3rem; font-weight: 800; color: #0F172A; letter-spacing: 0.05em;">✈ ALTIMETER</div>
        <div style="font-size: 0.75rem; color: #64748B; font-weight: 500; margin-top: 2px;">COCKPIT DISCIPLINE v2.0</div>
    </div>
    """, unsafe_allow_html=True)

def signal_badge(signal_str):
    if "BULLISH BREAKOUT" in signal_str:
        return f'<span class="badge-bullish">{signal_str}</span>'
    elif "BEARISH BREAKDOWN" in signal_str:
        return f'<span class="badge-bearish">{signal_str}</span>'
    elif "APPROACHING" in signal_str:
        return f'<span class="badge-approach">{signal_str}</span>'
    elif "BULLISH" in signal_str:
        return f'<span class="badge-bullish" style="background:#EBF5FF; color:#1E429F; border-color:#A4CAFE;">{signal_str}</span>'
    elif "BEARISH" in signal_str:
        return f'<span class="badge-bearish" style="background:#FFF5F5; color:#9B1C1C; border-color:#FEB2B2;">{signal_str}</span>'
    return f'<span class="badge-neutral">{signal_str}</span>'

def format_currency(val):
    return f"₹{val:,.2f}"

# Expanded layout tracking array maps
NSE_250 = [
    {"symbol": "RELIANCE", "security_id": "2885"},
    {"symbol": "TCS", "security_id": "11536"},
    {"symbol": "HDFCBANK", "security_id": "1333"},
    {"symbol": "INFY", "security_id": "1594"},
    {"symbol": "ICICIBANK", "security_id": "4963"},
    {"symbol": "SBIN", "security_id": "3045"},
    {"symbol": "BHARTIARTL", "security_id": "10604"},
    {"symbol": "ITC", "security_id": "1660"},
    {"symbol": "TATASTEEL", "security_id": "3496"},
    {"symbol": "HINDUNILVR", "security_id": "1336"}
]

NIFTY_50 = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", "TATASTEEL", "HINDUNILVR"]
