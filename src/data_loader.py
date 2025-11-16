import pandas as pd
from fastquant import get_crypto_data
import sys

def load_crypto_data(asset, start_date, end_date, timeframe):
    """
    Loads cryptocurrency data for a given asset, date range, and timeframe.
    """
    print(f"Loading data for {asset} from {start_date} to {end_date}", file=sys.stderr)
    data = get_crypto_data(asset, start_date, end_date, timeframe)
    if data.empty:
        print(f"No data found for {asset} from {start_date} to {end_date}.", file=sys.stderr)
        return pd.DataFrame()
    print("Data loaded successfully.", file=sys.stderr)
    return data
