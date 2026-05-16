"""
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
