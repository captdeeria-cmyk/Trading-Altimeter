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
    """Inject global CSS for the Trading Altimeter aviation dark theme."""
    st.markdown("""
    <style>
    /* ── Base ── */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0B0E11 !important;
        color: #E0E0E0 !important;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #0D1117 !important;
        border-right: 1px solid #1C1E22;
    }
    /* ── Cards ── */
    .ta-card {
        background: #1C1E22;
        border: 1px solid #2A2D35;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    /* ── Metric cards ── */
    .metric-card {
        background: #1C1E22;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        border: 1px solid #2A2D35;
        text-align: center;
    }
    .metric-label {
        font-size: 0.72rem;
        color: #8A8D94;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    /* ── Signal badges ── */
    .badge-bullish {
        background: rgba(0,230,118,0.15);
        color: #00E676;
        border: 1px solid #00E676;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-bearish {
        background: rgba(255,23,68,0.15);
        color: #FF1744;
        border: 1px solid #FF1744;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-approaching {
        background: rgba(0,212,255,0.15);
        color: #00D4FF;
        border: 1px solid #00D4FF;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-neutral {
        background: rgba(138,141,148,0.15);
        color: #8A8D94;
        border: 1px solid #8A8D94;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    /* ── Buttons ── */
    .stButton > button {
        background: #00D4FF !important;
        color: #0B0E11 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.4rem 1.2rem !important;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85 !important; }
    /* ── Sidebar header ── */
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.5rem 0 1rem 0;
        border-bottom: 1px solid #2A2D35;
        margin-bottom: 1rem;
    }
    .sidebar-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #00D4FF;
        letter-spacing: 0.04em;
    }
    .sidebar-sub {
        font-size: 0.65rem;
        color: #8A8D94;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    /* ── Tables ── */
    [data-testid="stDataFrame"] {
        background: #1C1E22 !important;
    }
    /* ── Selectbox / Input ── */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        background: #1C1E22 !important;
        color: #E0E0E0 !important;
        border: 1px solid #2A2D35 !important;
        border-radius: 8px !important;
    }
    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] {
        color: #8A8D94;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #00D4FF !important;
        border-bottom-color: #00D4FF !important;
    }
    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #1C1E22 !important;
        border-radius: 8px !important;
        color: #00D4FF !important;
    }
    /* ── Positive / Negative text helpers ── */
    .bull { color: #00E676; font-weight: 700; }
    .bear { color: #FF1744; font-weight: 700; }
    .cyan { color: #00D4FF; font-weight: 600; }
    /* ── Section headings ── */
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #00D4FF;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-left: 3px solid #00D4FF;
        padding-left: 8px;
        margin: 1.2rem 0 0.6rem 0;
    }
    /* ── News sentiment tags ── */
    .tag-positive {
        background: rgba(0,230,118,0.2); color: #00E676;
        border-radius: 4px; padding: 1px 8px; font-size: 0.72rem; font-weight: 700;
    }
    .tag-negative {
        background: rgba(255,23,68,0.2); color: #FF1744;
        border-radius: 4px; padding: 1px 8px; font-size: 0.72rem; font-weight: 700;
    }
    .tag-neutral {
        background: rgba(138,141,148,0.2); color: #8A8D94;
        border-radius: 4px; padding: 1px 8px; font-size: 0.72rem; font-weight: 700;
    }
    /* ── Progress bar ── */
    .stProgress > div > div { background-color: #00D4FF !important; }
    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0B0E11; }
    ::-webkit-scrollbar-thumb { background: #2A2D35; border-radius: 4px; }
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