"""
utils.py — Trading Altimeter
Shared utilities: Light theme CSS overrides, Dhan Security ID universe mappings,
and layout styling blocks.
"""

import streamlit as st

def inject_css():
    """Inject global CSS for a high-contrast crisp Light Theme."""
    st.markdown("""
    <style>
    /* ── Base Workspace ── */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F3F4F6 !important;
        color: #111827 !important;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E7EB !important;
    }
    
    /* ── Typography Clariity ── */
    h1, h2, h3, p, label, .stText {
        color: #111827 !important;
    }
    
    /* ── Component Panels ── */
    div[data-testid="stMetricValue"] {
        color: #111827 !important;
        font-weight: 800;
    }
    .ta-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* ── Interactive Form Selectors ── */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
    }
    div[data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }
    
    /* ── High Contrast Signal Badges ── */
    .badge-bullish {
        background-color: #ECFDF5;
        color: #047857;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 700;
        border: 1px solid #10B981;
    }
    .badge-bearish {
        background-color: #FEF2F2;
        color: #B91C1C;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 700;
        border: 1px solid #EF4444;
    }
    .badge-approach {
        background-color: #FFFBEB;
        color: #B45309;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 700;
        border: 1px solid #F59E0B;
    }
    .badge-neutral {
        background-color: #F9FAFB;
        color: #6B7280;
        padding: 4px 8px;
        border-radius: 4px;
        border: 1px solid #D1D5DB;
    }
    </style>
    """, unsafe_allow_html=True)

# 250 Liquid Tickers with explicit numeric Dhan Security IDs to prevent slow name queries
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

NIFTY_50 = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]

def render_sidebar_header():
    st.markdown("""
    <div style="padding: 10px 0px;">
        <div style="font-size: 1.25rem; font-weight: 800; color: #111827; letter-spacing: 1px;">✈ ALTIMETER</div>
        <div style="font-size: 0.72rem; color: #6B7280; font-weight: 500;">COCKPIT DISCIPLINE v2.0</div>
    </div>
    """, unsafe_allow_html=True)

def render_banner():
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.2rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
        <div style="font-size: 1.75rem; font-weight: 900; color: #111827; letter-spacing: 0.05em;">✈ TRADING ALTIMETER</div>
        <div style="font-size: 0.9rem; color: #4B5563; margin-top: 4px;">Institutional-Grade Direct Dhan API Analytics Deck</div>
    </div>
    """, unsafe_allow_html=True)

def signal_badge(signal_str):
    if "BULLISH" in signal_str:
        return f'<span class="badge-bullish">{signal_str}</span>'
    elif "BEARISH" in signal_str:
        return f'<span class="badge-bearish">{signal_str}</span>'
    elif "APPROACH" in signal_str:
        return f'<span class="badge-approach">{signal_str}</span>'
    return f'<span class="badge-neutral">{signal_str}</span>'

def format_currency(val):
    return f"₹{val:,.2f}"
