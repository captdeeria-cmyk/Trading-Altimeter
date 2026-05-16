import streamlit as st
from dhan_broker import get_dhan_historical_data
from indicators import calculate_indicators, generate_hma_signal

@st.cache_data(ttl=300) # Cache scanner results for 5 minutes
def run_fast_hma_scanner(stock_universe, client_id, access_token):
    scanner_results = []
    
    # Progress indicator for the cockpit dashboard
    progress_bar = st.progress(0)
    
    for idx, stock in enumerate(stock_universe):
        # stock contains {'symbol': 'RELIANCE', 'security_id': '1333'}
        df = get_dhan_historical_data(client_id, access_token, stock['security_id'])
        
        if not df.empty:
            df_analyzed = calculate_indicators(df)
            signal, ltp = generate_hma_signal(df_analyzed)
            
            if signal in ["🚀 BULLISH BREAKOUT", "💀 BEARISH BREAKDOWN", "👀 APPROACHING 200 HMA"]:
                scanner_results.append({
                    "Stock": stock['symbol'],
                    "LTP": ltp,
                    "Signal": signal
                })
        
        # Update progress dynamically
        progress_bar.progress((idx + 1) / len(stock_universe))
        
    return pd.DataFrame(scanner_results)
