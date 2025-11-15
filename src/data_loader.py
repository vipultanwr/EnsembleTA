import pandas as pd
from fastquant import get_crypto_data

def load_crypto_data(asset, start_date, end_date, timeframe):
    """
    Loads crypto data for a given asset and date range.
    """
    print(f"Loading data for {asset} from {start_date} to {end_date}...")
    data = get_crypto_data(asset, start_date, end_date, time_resolution=timeframe)
    if data is None or data.empty:
        raise ValueError("Failed to load data.")
    
    # Ensure index is DatetimeIndex and sorted
    data.index = pd.to_datetime(data.index)
    data = data.sort_index()
    
    # Drop duplicates from the index, keeping the first occurrence
    data = data[~data.index.duplicated(keep='first')]
    
    print("Data loaded successfully.")
    return data
