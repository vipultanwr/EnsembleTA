import pandas as pd
from fastquant import get_crypto_data

def load_crypto_data(asset, start_date, end_date, timeframe):
    """
    Loads crypto data for a given asset and date range.
    """
    print(f"Loading data for {asset} from {start_date} to {end_date}...")
    data = get_crypto_data(asset, start_date, end_date, time_resolution=timeframe)
    data = data[~data.index.duplicated(keep='first')]
    if data is None or data.empty:
        raise ValueError("Failed to load data.")
    print("Data loaded successfully.")
    return data
