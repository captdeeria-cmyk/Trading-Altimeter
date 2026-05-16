"""
utils.py — Trading Altimeter
Shared utilities: custom CSS, NSE stock universe (250 liquid stocks),
and general helper functions used across the application.
"""

import streamlit as st


# ---------------------------------------------------------------------------
# CUSTOM CSS — Deep dark aviation theme
# ---------------------------------------------------------------------------

def inject_css():
    """Inject global CSS for the Trading Altimeter PROFESSIONAL LIGHT THEME."""
    st.markdown("""
    <style>
    /* ── FORCE PURE WHITE LIGHT MODE ── */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F3F4F6 !important;
        color: #1F2937 !important;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E7EB !important;
    }
    
    /* ── Cards (White with soft shadows) ── */
    .ta-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* ── Metric cards ── */
    .metric-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        border: 1px solid #E5E7EB;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 0.72rem;
        color: #6B7280;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #111827;
    }
    
    /* ── Signal badges (Clean Colors) ── */
    .badge-bullish {
        background: rgba(22, 163, 74, 0.1);
        color: #16A34A;
        border: 1px solid #16A34A;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-bearish {
        background: rgba(220, 38, 38, 0.1);
        color: #DC2626;
        border: 1px solid #DC2626;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-approaching {
        background: rgba(37, 99, 235, 0.1);
        color: #2563EB;
        border: 1px solid #2563EB;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-neutral {
        background: rgba(107, 114, 128, 0.1);
        color: #6B7280;
        border: 1px solid #6B7280;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    
    /* ── Buttons (Professional Blue) ── */
    .stButton > button {
        background: #2563EB !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.4rem 1.2rem !important;
    }
    .stButton > button:hover { 
        background: #1D4ED8 !important; 
    }
    
    /* ── Sidebar header ── */
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.5rem 0 1rem 0;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }
    .sidebar-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #2563EB;
        letter-spacing: 0.04em;
    }
    .sidebar-sub {
        font-size: 0.65rem;
        color: #9CA3AF;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    
    /* ── Tables ── */
    [data-testid="stDataFrame"] {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
    }
    
    /* ── Inputs ── */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        background: #FFFFFF !important;
        color: #1F2937 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
    }
    
    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] {
        color: #6B7280;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #2563EB !important;
        border-bottom-color: #2563EB !important;
    }
    
    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #F9FAFB !important;
        border-radius: 8px !important;
        border: 1px solid #E5E7EB !important;
        color: #111827 !important;
    }
    
    /* ── Text Helpers ── */
    .bull { color: #16A34A; font-weight: 700; }
    .bear { color: #DC2626; font-weight: 700; }
    .cyan { color: #2563EB; font-weight: 600; }
    
    /* ── Section headings ── */
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-left: 3px solid #2563EB;
        padding-left: 8px;
        margin: 1.2rem 0 0.6rem 0;
    }
    
    /* ── News tags ── */
    .tag-positive { background: rgba(22,163,74,0.1); color: #16A34A; border-radius: 4px; padding: 1px 8px; font-size: 0.72rem; font-weight: 700; }
    .tag-negative { background: rgba(220,38,38,0.1); color: #DC2626; border-radius: 4px; padding: 1px 8px; font-size: 0.72rem; font-weight: 700; }
    .tag-neutral { background: rgba(107,114,128,0.1); color: #6B7280; border-radius: 4px; padding: 1px 8px; font-size: 0.72rem; font-weight: 700; }
    
    /* ── Progress bar ── */
    .stProgress > div > div { background-color: #2563EB !important; }
    
    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #F3F4F6; }
    ::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# NSE STOCK UNIVERSE — 250 highly liquid stocks
# ---------------------------------------------------------------------------

NIFTY_50 = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
    "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN",
    "BAJFINANCE", "NESTLEIND", "WIPRO", "ULTRACEMCO", "ONGC",
    "ADANIENT", "POWERGRID", "NTPC", "JSWSTEEL", "TATAMOTORS",
    "TECHM", "SUNPHARMA", "HCLTECH", "M&M", "BAJAJFINSV",
    "TATASTEEL", "ADANIPORTS", "COALINDIA", "DRREDDY", "CIPLA",
    "DIVISLAB", "APOLLOHOSP", "EICHERMOT", "BPCL", "GRASIM",
    "BRITANNIA", "HEROMOTOCO", "INDUSINDBK", "HINDALCO", "TATACONSUM",
    "SHRIRAMFIN", "SBILIFE", "HDFCLIFE", "BAJAJ-AUTO", "UPL",
]

NIFTY_NEXT_50 = [
    "ADANIGREEN", "ADANITRANS", "AMBUJACEM", "AUROPHARMA", "BANKBARODA",
    "BERGEPAINT", "BIOCON", "BOSCHLTD", "CANBK", "CHOLAFIN",
    "COLPAL", "DABUR", "DLF", "GAIL", "GODREJCP",
    "GODREJPROP", "HAVELLS", "ICICIGI", "ICICIPRULI", "INDHOTEL",
    "INDUSTOWER", "IRCTC", "JINDALSTEL", "LUPIN", "MARICO",
    "MCDOWELL-N", "MUTHOOTFIN", "NAUKRI", "NHPC", "NMDC",
    "OBEROIRLTY", "OFSS", "PAGEIND", "PIIND", "PNB",
    "RECLTD", "SAIL", "SIEMENS", "SRF", "TATACOMM",
    "TORNTPHARM", "TRENT", "TVSMOTOR", "UBL", "UNIONBANK",
    "VEDL", "VOLTAS", "WHIRLPOOL", "YESBANK", "ZYDUSLIFE",
]

FNO_STOCKS = [
    "AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL",
    "ACC", "AFFLE", "AJANTPHARM", "ALKEM", "ALKYLAMINE",
    "AMARAJABAT", "AMBUJACEM", "ANGELONE", "APOLLOTYRE", "ATUL",
    "AUBANK", "AUROPHARMA", "BALRAMCHIN", "BANDHANBNK", "BATAINDIA",
    "BEL", "BHARATFORG", "BHARTIARTL", "BHEL", "BIKAJI",
    "BLUEDART", "CAMS", "CANFINHOME", "CDSL", "CESC",
    "CHAMBLFERT", "COFORGE", "CROMPTON", "CUMMINSIND", "CYIENT",
    "DALBHARAT", "DEEPAKNTR", "DELTACORP", "DIXON", "DMART",
    "ESCORTS", "EXIDEIND", "FEDERALBNK", "FINOLEXIND", "FLUOROCHEM",
    "FSL", "GNFC", "GPPL", "GRANULES", "GSPL",
    "GUJGASLTD", "HAPPSTMNDS", "HFCL", "HIKAL", "HINDPETRO",
    "HUDCO", "IEX", "IFBIND", "IIFL", "INDIANB",
    "INDIAMART", "INDIGO", "INOXWIND", "INTELLECT", "IPCALAB",
    "IRFC", "ISEC", "J&KBANK", "JKCEMENT", "JKLAKSHMI",
    "JKPAPER", "JUBLFOOD", "JUBLINGREA", "JUSTDIAL", "KALYANKJIL",
    "KANSAINER", "KEI", "KFINTECH", "KNR", "KOTAKBANK",
    "KPITTECH", "KRBL", "L&TFH", "LALPATHLAB", "LATENTVIEW",
    "LICHSGFIN", "LINDEINDIA", "LXIT", "MANAPPURAM", "MAPMYINDIA",
    "MCX", "METROPOLIS", "MGL", "MPHASIS", "MSSL",
    "NATIONALUM", "NAUKRI", "NAVINFLUOR", "NBCC", "NESCO",
    "NETWORK18", "NILKAMAL", "NLCINDIA", "NSLNISP", "OBEROIRLTY",
    "OIL", "OLECTRA", "ONGC", "PERSISTENT", "PETRONET",
    "PFIZER", "PHOENIXLTD", "PIDILITIND", "POLYCAB", "POLYMED",
    "PRAJIND", "PVR", "RADICO", "RAJESHEXPO", "RAMCOCEM",
    "RBLBANK", "ROUTE", "SANOFI", "SAPPHIRE", "SCHAEFFLER",
    "SEQUENT", "SHYAMMETL", "SJVN", "SKFINDIA", "SOBHA",
    "SONATSOFTW", "STARHEALTH", "STLTECH", "SUDARSCHEM", "SUMICHEM",
    "SUNTV", "SUPREMEIND", "SUVENPHAR", "TANLA", "TATACHEM",
    "TATAELXSI", "TATAINVEST", "TEAMLEASE", "THYROCARE", "TIMKEN",
    "TTKPRESTIG", "TV18BRDCST", "TVSHLTD", "UJJIVANSFB", "VAIBHAVGBL",
    "VBL", "VGUARD", "VINATIORGA", "VIPIND", "VSTIND",
    "WELCORP", "WELSPUNLIV", "WINDMACHINES", "WIPRO", "ZEEL",
]

# Full 250-stock universe (deduplicated)
NSE_250 = list(dict.fromkeys(NIFTY_50 + NIFTY_NEXT_50 + FNO_STOCKS))[:250]

# Map display name → yfinance ticker (append .NS)
def to_yf_ticker(symbol: str) -> str:
    """Convert NSE symbol to yfinance format, e.g. RELIANCE → RELIANCE.NS"""
    return f"{symbol}.NS"


def format_currency(value: float) -> str:
    """Format a number as Indian Rupees with ₹ symbol and comma separation."""
    if abs(value) >= 1_00_00_000:
        return f"₹{value/1_00_00_000:.2f} Cr"
    elif abs(value) >= 1_00_000:
        return f"₹{value/1_00_000:.2f} L"
    else:
        return f"₹{value:,.2f}"


def color_pnl(value: float) -> str:
    """Return HTML-colored span for P&L values."""
    cls = "bull" if value >= 0 else "bear"
    sign = "+" if value >= 0 else ""
    return f'<span class="{cls}">{sign}{value:.2f}%</span>'


def signal_badge(signal: str) -> str:
    """Return HTML badge for HMA signal."""
    mapping = {
        "BULLISH": ('<span class="badge-bullish">🚀 BULLISH BREAKOUT</span>', ),
        "BEARISH": ('<span class="badge-bearish">💀 BEARISH BREAKDOWN</span>', ),
        "APPROACHING": ('<span class="badge-approaching">👀 APPROACHING HMA</span>', ),
        "NEUTRAL": ('<span class="badge-neutral">— NEUTRAL</span>', ),
    }
    return mapping.get(signal, mapping["NEUTRAL"])[0]


def render_sidebar_header():
    """Render the branded sidebar header with logo and app name."""
    with st.sidebar:
        try:
            from PIL import Image
            import os
            if os.path.exists("assets/logo.png"):
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image("assets/logo.png", width=52)
                with col2:
                    st.markdown("""
                    <div style="padding-top:4px">
                        <div class="sidebar-title">TRADING ALTIMETER</div>
                        <div class="sidebar-sub">NSE Analytics Platform</div>
                    </div>""", unsafe_allow_html=True)
            else:
                raise FileNotFoundError
        except Exception:
            st.markdown("""
            <div class="sidebar-header">
                <div>
                    <div class="sidebar-title">✈ TRADING ALTIMETER</div>
                    <div class="sidebar-sub">NSE Analytics Platform</div>
                </div>
            </div>""", unsafe_allow_html=True)


def render_banner():
    """Render the top banner image or fallback text banner."""
    try:
        import os
        if os.path.exists("assets/banner.png"):
            st.image("assets/banner.png", use_column_width=True)
        else:
            raise FileNotFoundError
    except Exception:
        st.markdown("""
        <div style="background: linear-gradient(135deg,#0D1B2A 0%,#1C1E22 60%,#0B0E11 100%);
                    border: 1px solid #00D4FF33; border-radius:12px; padding:1.5rem 2rem;
                    margin-bottom:1.2rem; text-align:center;">
            <div style="font-size:2rem;font-weight:900;color:#00D4FF;letter-spacing:0.12em">
                ✈ TRADING ALTIMETER
            </div>
            <div style="font-size:0.8rem;color:#8A8D94;letter-spacing:0.2em;margin-top:4px">
                NAVIGATING THE MARKETS WITH COCKPIT DISCIPLINE
            </div>
        </div>""", unsafe_allow_html=True)
