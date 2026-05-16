"""
portfolio.py — Trading Altimeter
"""
import streamlit as st
import pandas as pd

def render_portfolio_page():"""
portfolio.py — Trading Altimeter
"""
import streamlit as st

def render_portfolio_page():
    st.subheader("💼 Active Portfolio Matrix")
    st.markdown("""
    <div style='background:#FFFFFF; border:1px solid #E2E8F0; padding:1.5rem; border-radius:12px;'>
        <h5 style='margin:0; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;'>Account Equity Valuation</h5>
        <h1 style='margin:6px 0; font-weight:900; color:#0F172A; font-size:2.25rem;'>₹2,84,950.00</h1>
        <span style='color:#16A34A; font-weight:700; font-size:0.95rem;'>▲ +6.18% Consolidated Account Yield</span>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("💼 Active Holdings Overview")
    st.markdown("""
    <div style='background:#FFFFFF; border:1px solid #E5E7EB; padding:1.5rem; border-radius:8px;'>
        <h4 style='margin:0; color:#4B5563;'>Total Portfolio Equity Valuation</h4>
        <h2 style='margin:4px 0; font-weight:800; color:#111827;'>₹1,42,500.00</h2>
        <span style='color:#10B981; font-weight:700;'>▲ +4.25% Net Overall Yield</span>
    </div>
    """, unsafe_allow_html=True)
