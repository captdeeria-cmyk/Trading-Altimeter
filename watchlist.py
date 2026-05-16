"""
watchlist.py — Trading Altimeter
"""
import streamlit as st
import pandas as pd
from dhan_broker import fetch_historical_candles
from indicators import calculate_dhan_indicators, classify_dhan_signal

def render_watchlist_page():
    st.subheader("⭐ Custom Trading Watchlist")
    
    # Simple list tracking simulation context
    if "watchlist_items" not in st.session_state:
        st.session_state["watchlist_items"] = ["RELIANCE", "TCS"]
        
    new_stock = st.text_input("Add NSE Ticker Symbol:", "").upper().strip()
    if st.button("➕ Add to System Grid") and new_stock:
        if new_stock not in st.session_state["watchlist_items"]:
            st.session_state["watchlist_items"].append(new_stock)
            st.rerun()
            
    # Mock lookup database for scanner rendering
    sec_ids = {"RELIANCE": "2885", "TCS": "11536", "HDFCBANK": "1333"}
    
    rows = []
    for item in st.session_state["watchlist_items"]:
        sid = sec_ids.get(item, "2885")
        df_candles = fetch_historical_candles(sid)
        if not df_candles.empty:
            df_proc = calculate_dhan_indicators(df_candles)
            sig = classify_dhan_signal(df_proc)
            rows.append({"Symbol": item, "LTP": f"₹{sig['ltp']:.2f}", "Altimeter Vector": sig['signal']})
            
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
