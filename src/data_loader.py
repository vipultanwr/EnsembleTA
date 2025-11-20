import pandas as pd
import yfinance as yf
import ccxt
import sys
from datetime import datetime

def _load_yfinance_data(asset, start_date, end_date, timeframe):
    """
    Loads data from Yahoo Finance.
    Covers stocks, forex, crypto, and commodities.
    """
    print(f"Loading data for {asset} from yfinance...", file=sys.stderr)
    
    yfinance_asset = asset
    # Only convert crypto-style tickers, and avoid touching already-formatted tickers
    if '/' in asset and '=' not in asset:
        yfinance_asset = asset.replace('/', '-')
        if 'USDT' in yfinance_asset:
            yfinance_asset = yfinance_asset.replace('USDT', 'USD')
        print(f"Converted asset to yfinance format: {yfinance_asset}", file=sys.stderr)

    try:
        # yfinance uses '1d' for daily, '1h' for hourly, etc.
        df = yf.download(
            tickers=yfinance_asset,
            start=start_date,
            end=end_date,
            interval=timeframe,
            progress=False
        )
        if df.empty:
            print(f"yfinance returned no data for {yfinance_asset}.", file=sys.stderr)
            return pd.DataFrame()
        
        # Check if columns are MultiIndex and flatten if necessary
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Standardize column names to lowercase
        df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Adj Close': 'adj_close',
            'Volume': 'volume'
        }, inplace=True)
        
        # Ensure index is timezone-naive datetime
        df.index = pd.to_datetime(df.index).tz_localize(None)

        # --- Validation Step ---
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            print(f"Validation failed: DataFrame for {yfinance_asset} is missing required columns.", file=sys.stderr)
            return pd.DataFrame()
        
        print("yfinance data loaded successfully.", file=sys.stderr)
        return df[['open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        print(f"An error occurred with yfinance for {yfinance_asset}: {e}", file=sys.stderr)
        return pd.DataFrame()

def _load_ccxt_data(asset, start_date, end_date, timeframe):
    """
    Loads crypto OHLCV data from CCXT.
    """
    print(f"Loading data for {asset} from ccxt...", file=sys.stderr)
    try:
        exchange = ccxt.binance() # Using Binance as a default exchange
        
        # Convert dates to milliseconds for ccxt
        since = exchange.parse8601(f'{start_date}T00:00:00Z')
        
        # Fetch data
        ohlcv = exchange.fetch_ohlcv(asset, timeframe, since)
        if not ohlcv:
            print(f"ccxt returned no data for {asset}.", file=sys.stderr)
            return pd.DataFrame()
            
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Filter for end_date
        df = df[df.index <= pd.to_datetime(end_date)]
        
        print("ccxt data loaded successfully.", file=sys.stderr)
        return df
    except Exception as e:
        print(f"An error occurred with ccxt for {asset}: {e}", file=sys.stderr)
        return pd.DataFrame()

def _load_icici_data(asset, start_date, end_date, timeframe):
    """
    Placeholder for loading data from the user's custom ICICI Direct script.
    """
    print(f"NOTE: ICICI Direct data loading for '{asset}' is a placeholder and not yet implemented.", file=sys.stderr)
    print("Please integrate your custom script here.", file=sys.stderr)
    # To integrate:
    # 1. Add your script's logic here.
    # 2. Ensure it returns a pandas DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
    #    and a datetime index.
    return pd.DataFrame()

def load_data(asset, start_date, end_date, timeframe, source='auto'):
    """
    Main data loading function.
    
    Routes to the correct data source based on the user's plan:
    1. Timeframe >= 1d: Use yfinance.
    2. Intraday Crypto: Use ccxt.
    3. Indian Stocks: Use custom ICICI script (requires source='icici').
    4. Other Intraday: Default to yfinance.
    """
    
    # Manual source override
    if source == 'yfinance':
        return _load_yfinance_data(asset, start_date, end_date, timeframe)
    elif source == 'ccxt':
        return _load_ccxt_data(asset, start_date, end_date, timeframe)
    elif source == 'icici':
        return _load_icici_data(asset, start_date, end_date, timeframe)

    # Automatic routing logic
    is_daily_or_longer = 'd' in timeframe.lower() or 'w' in timeframe.lower() or 'mo' in timeframe.lower()

    if is_daily_or_longer:
        print(f"Routing to yfinance for daily/longer timeframe ({timeframe})...", file=sys.stderr)
        return _load_yfinance_data(asset, start_date, end_date, timeframe)
    else:
        # Simple heuristic for crypto assets
        if '/' in asset:
            print(f"Routing to ccxt for intraday crypto asset ({asset})...", file=sys.stderr)
            return _load_ccxt_data(asset, start_date, end_date, timeframe)
        else:
            print(f"Routing to yfinance for other intraday assets ({asset})...", file=sys.stderr)
            return _load_yfinance_data(asset, start_date, end_date, timeframe)