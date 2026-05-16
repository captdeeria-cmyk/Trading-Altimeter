import pandas as pd
from dhanhq import dhanhq

def get_dhan_historical_data(client_id, access_token, security_id, exchange_segment="NSE_EQ", expiry_code=0):
    """
    Fetches historical data directly from Dhan API.
    Replaces yfinance entirely.
    """
    dhan = dhanhq(client_id, access_token)
    
    # Fetch daily charts (you can change '1' to '5' or '15' for intraday minutes)
    # 1 = 1 Minute, 2 = Daily. Let's assume Daily for 200 HMA daily strategy
    data = dhan.get_historical_data(
        symbol=security_id,
        exchange_segment=exchange_segment,
        instrument_type="EQUITY",
        expiry_code=expiry_code,
        from_date="2025-01-01",  # Adjust dates dynamically as needed
        to_date="2026-05-16",
        data_period="2" 
    )
    
    if data and data.get('status') == 'success':
        df = pd.DataFrame(data['data'])
        # Dhan returns timestamps, open, high, low, close, volume
        df['Date'] = pd.to_datetime(df['start_time'])
        df.set_index('Date', inplace=True)
        df.rename(columns={
            'open': 'Open', 
            'high': 'High', 
            'low': 'Low', 
            'close': 'Close', 
            'volume': 'Volume'
        }, inplace=True)
        return df
    else:
        print(f"Error fetching data from Dhan: {data.get('remarks')}")
        return pd.DataFrame()
