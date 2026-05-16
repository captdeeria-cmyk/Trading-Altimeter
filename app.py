"""
app.py — Trading Altimeter
Main application entry point.
"""

import streamlit as st
import datetime
import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── RULE 1: THIS MUST ABSOLUTELY BE THE FIRST STREAMLIT OPERATION ──
st.set_page_config(
    page_title="Trading Altimeter",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── NOW IT IS SAFE TO IMPORT SCRIPT MODULES ──
from utils import (
    inject_css, NSE_250, NIFTY_50,
    render_sidebar_header, render_banner, signal_badge, format_currency,
)
from indicators import (
    calculate_dhan_indicators, classify_dhan_signal
)
from backtester import run_backtest, build_price_chart, build_equity_curve
from news_sentiment import get_news_with_sentiment
from watchlist import render_watchlist_page
from portfolio import render_portfolio_page
from dhan_broker import render_order_panel

logger = logging.getLogger(__name__)

# ── RUN STYLE INJECTIONS NEXT ──
inject_css()

# ... (The rest of your router logic below remains the same)"""
app.py — Trading Altimeter
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# CRITICAL: This call MUST happen before any custom CSS injections or utility imports
st.set_page_config(
    page_title="Trading Altimeter",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Now it is completely safe to import custom engines and execute injections
from utils import inject_css, NSE_250, render_sidebar_header, render_banner, signal_badge
from dhan_broker import fetch_historical_candles, get_dhan_connection
from indicators import calculate_dhan_indicators, classify_dhan_signal

# Inject crisp light theme properties
inject_css()

# Rest of your routing application code goes here...
