import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

interval_periods = {
    "daily": {
        "interval": "1d",
        "start": datetime.now() - timedelta(days=730),
        "end": datetime.now()
    },
    "hourly": {
        "interval": "1h",
        "start": datetime.now() - timedelta(days=365),
        "end": datetime.now()
    },
    "15min": {
        "interval": "15m",
        "start": datetime.now() - timedelta(days=30),
        "end": datetime.now()
    },
    "1min": {
        "interval": "15m",
        "start": datetime.now() - timedelta(days=7),
        "end": datetime.now()
    },
}

def get_data(ticker: str, interval_period="hourly"):
    if interval_period not in interval_periods:
        raise ValueError(f"Invalid period_name '{interval_period}'. Available: {list(interval_periods.keys())}")
    
    params = interval_periods[interval_period]

    df = yf.download(ticker, interval=params["interval"], start=params["start"], end=params["end"], auto_adjust=True)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index = pd.to_datetime(df.index)
    df = df.sort_index().copy()

    df.columns.name = None
    df.index.name = None
    return df