import os
import streamlit as st
import pandas as pd
import numpy as np

# ── STRICT PREMIUM LIGHT THEME ──────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #F8F9FA !important; color: #212529 !important; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E0E0E0 !important; }
    .ta-card, .metric-card { background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); padding: 1rem; }
    .metric-label { font-size: 0.7rem; color: #6C757D; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; font-weight: 600;}
    .metric-value { font-size: 1.4rem; font-weight: 700; color: #212529; }
    
    /* BEAUTIFUL STOCK CARDS FOR DASHBOARD */
    .stock-card { background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px; padding: 10px; text-align: center; transition: all 0.2s; cursor: pointer; }
    .stock-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-color: #2563EB; }
    .stock-name { font-size: 0.8rem; font-weight: 800; color: #343A40; margin-bottom: 4px; letter-spacing: 0.03em; }
    .stock-price { font-size: 1.1rem; font-weight: 700; color: #212529; }
    .stock-chg-pos { font-size: 0.8rem; font-weight: 700; color: #198754; } /* Clean Green */
    .stock-chg-neg { font-size: 0.8rem; font-weight: 700; color: #DC3545; } /* Clean Red */
    
    .badge-bullish { background: #E8F5E9; color: #2E7D32; border: 1px solid #A5D6A7; border-radius: 6px; padding: 3px 10px; font-weight: 700; font-size: 0.8rem; }
    .badge-bearish { background: #FFEBEE; color: #C62828; border: 1px solid #EF9A9A; border-radius: 6px; padding: 3px 10px; font-weight: 700; font-size: 0.8rem; }
    .badge-approaching { background: #E3F2FD; color: #1565C0; border: 1px solid #90CAF9; border-radius: 6px; padding: 3px 10px; font-weight: 700; font-size: 0.8rem; }
    .badge-neutral { background: #F5F5F5; color: #757575; border: 1px solid #E0E0E0; border-radius: 6px; padding: 3px 10px; font-weight: 700; font-size: 0.8rem; }
    
    .stButton > button { background: #2563EB !important; color: white !important; font-weight: 600 !important; border-radius: 8px !important; border: none !important; }
    .stButton > button:hover { background: #1D4ED8 !important; }
    .sidebar-title { color: #2563EB !important; font-weight: 800; font-size: 1.2rem; }
    .sidebar-sub { color: #ADB5BD !important; font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; }
    .section-title { font-size: 0.95rem; font-weight: 700; color: #495057; border-left: 4px solid #2563EB; padding-left: 10px; margin: 1.5rem 0 1rem 0; text-transform: uppercase; letter-spacing: 0.05em;}
    .tag-positive { background: #E8F5E9; color: #2E7D32; border-radius: 4px; padding: 2px 8px; font-size: 0.7rem; font-weight: 700; }
    .tag-negative { background: #FFEBEE; color: #C62828; border-radius: 4px; padding: 2px 8px; font-size: 0.7rem; font-weight: 700; }
    .tag-neutral { background: #F5F5F5; color: #757575; border-radius: 4px; padding: 2px 8px; font-size: 0.7rem; font-weight: 700; }
    .stTabs [aria-selected="true"] { color: #2563EB !important; border-bottom-color: #2563EB !important; font-weight: 700; }
    .streamlit-expanderHeader { background: #FFFFFF !important; border: 1px solid #E0E0E0 !important; color: #495057 !important; font-weight: 600; }
    ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-thumb { background: #CED4DA; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar_header():
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path): st.image(logo_path, width=100)
    else: st.markdown("<h1 style='color:#2563EB;'>✈️</h1>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>TRADING ALTIMETER</div><div class='sidebar-sub'>Navigating The Markets With Cockpit Discipline</div>", unsafe_allow_html=True)

def render_banner():
    banner_path = os.path.join("assets", "banner.png")
    if os.path.exists(banner_path): st.image(banner_path, use_container_width=True)

def signal_badge(signal):
    mapping = {"BULLISH": "badge-bullish", "BEARISH": "badge-bearish", "APPROACHING": "badge-approaching"}
    return f"<span class='{mapping.get(signal, 'badge-neutral')}'>{signal}</span>"

def to_yf_ticker(symbol): return f"{symbol}.NS"

NSE_250 = ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","HINDUNILVR","ITC","SBIN","BHARTIARTL","LT","KOTAKBANK","AXISBANK","ASIANPAINT","MARUTI","BAJFINANCE","WIPRO","TITAN","SUNPHARMA","TATAMOTORS","POWERGRID","NTPC","TATASTEEL","HCLTECH","ULTRACEMCO","NESTLEIND","ONGC","TECHM","COALINDIA","INDUSINDBK","JSWSTEEL","BPCL","ADANIENT","ADANIPORTS","DRREDDY","CIPLA","DIVISLAB","HEROMOTOCO","APOLLOHOSP","EICHERMOT","BRITANNIA","TRENT","GRASIM","HINDALCO","IOC","M&M","LTIM","SBILIFE","BAJAJFINSV","DMART","TATAPOWER","ADANIGREEN","DABUR","TVSMOTOR","BAJAJAUTO","PIDILITIND","EICHERMOT","SUNTV","YESBANK","PNB","CANBK","BANKBARODA","IDFCFIRSTB","FEDERALBNK","INDIANB","UNIONBANK","IRFC","IRCTC","TATACONSUM","SIEMENS","ZOMATO","PAYTM","NHPC","SJVN","TORNTPOWER","VEDL","NATIONALUM","NMDC","OIL","HINDPETRO","MRPL","CHOLAFIN","SHRIRAMFIN","MUTHOOTFIN","DELHIVERY","DIXON","COFORGE","PERSISTENT","MPHASIS","MOTHERSON","BOSCHLTD","ASHOKLEY","APOLLOTYRE","MRF","CEAT","JKTYRE","EMAMILTD","GODREJCP","COLPAL","RADICO","MCDOWELL-N","UBL","HUDCO","CONCOR","BEL","IRFC","SJVN","PTCIL","NTPC","POWERGRID","TATAPOWER","NHPC","SJVN","TORNTPOWER","ADANIGREEN","ADANITRANS","ADANI TOTAL GAS","ADANI PORTS","ADANI ENTERPRISES"]
NIFTY_50 = NSE_250[:50]
