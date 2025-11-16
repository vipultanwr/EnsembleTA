import pandas as pd
import numpy as np

def generate_signals(data, **params):
    """
    A simple moving average crossover strategy.
    
    Generates a buy signal (1) when the short moving average crosses above the long moving average,
    and a sell signal (-1) when it crosses below.
    """
    short_window = params.get('short_window', 20)
    long_window = params.get('long_window', 50)

    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    # Create short and long simple moving averages
    signals['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1, center=False).mean()

    # Generate signals
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)   

    # Take the difference of the signals in order to generate actual trading orders
    signals['positions'] = signals['signal'].diff()

    return pd.DataFrame({'signal': signals['positions']})