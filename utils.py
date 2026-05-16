"""
utils.py — Trading Altimeter
"""
import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F3F4F6 !important;
        color: #111827 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E7EB !important;
    }
    h1, h2, h3, h4, p, label { color: #111827 !important; }
    .ta-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def render_banner():
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.2rem;">
        <div style="font-size: 1.75rem; font-weight: 900; color: #111827; letter-spacing: 0.05em;">✈ TRADING ALTIMETER</div>
        <div style="font-size: 0.9rem; color: #4B5563; margin-top: 4px;">Direct Institutional Dhan Stream Cockpit</div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_header():
    st.markdown('<div style="font-size: 1.25rem; font-weight: 800; color: #111827;">✈ ALTIMETER</div>', unsafe_allow_html=True)

def signal_badge(signal_str):
    if "BULLISH" in signal_str:
        return f'<span style="background:#ECFDF5; color:#047857; padding:4px 8px; border-radius:4px; font-weight:700; border:1px solid #10B981;">{signal_str}</span>'
    elif "BEARISH" in signal_str:
        return f'<span style="background:#FEF2F2; color:#B91C1C; padding:4px 8px; border-radius:4px; font-weight:700; border:1px solid #EF4444;">{signal_str}</span>'
    return f'<span style="background:#FFFBEB; color:#B45309; padding:4px 8px; border-radius:4px; font-weight:700; border:1px solid #F59E0B;">{signal_str}</span>'

def format_currency(val):
    return f"₹{val:,.2f}"

NSE_250 = [
    {"symbol": "RELIANCE", "security_id": "2885"},
    {"symbol": "TCS", "security_id": "11536"},
    {"symbol": "HDFCBANK", "security_id": "1333"},
    {"symbol": "INFY", "security_id": "1594"},
    {"symbol": "ICICIBANK", "security_id": "4963"}
]
NIFTY_50 = ["RELIANCE", "TCS", "HDFCBANK"]
