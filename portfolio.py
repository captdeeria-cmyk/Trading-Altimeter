"""
portfolio.py — Trading Altimeter
"""
import streamlit as st
import pandas as pd

def render_portfolio_page():
    st.subheader("💼 Active Holdings Overview")
    st.markdown("""
    <div style='background:#FFFFFF; border:1px solid #E5E7EB; padding:1.5rem; border-radius:8px;'>
        <h4 style='margin:0; color:#4B5563;'>Total Portfolio Equity Valuation</h4>
        <h2 style='margin:4px 0; font-weight:800; color:#111827;'>₹1,42,500.00</h2>
        <span style='color:#10B981; font-weight:700;'>▲ +4.25% Net Overall Yield</span>
    </div>
    """, unsafe_allow_html=True)
