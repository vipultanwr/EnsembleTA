"""
Configuration file for the ensemble backtest.
"""

# --- Data Fetching Parameters ---
RANKING_START_DATE = '2021-01-01'
RANKING_END_DATE = '2021-03-31'
BACKTEST_START_DATE = '2022-05-01'
BACKTEST_END_DATE = '2022-06-01'
ASSET = "BTC/USDT"
TIMEFRAME = '5m'

# --- Ensemble Parameters ---
N_TOP_STRATEGIES = 15
SIGNAL_SHIFTS = [1, 2] # Lookback periods for signals

# --- Backtesting Parameters ---
INITIAL_CASH = 100000.0
COMMISSION_PCT = 0.0
SLIPPAGE_PCT = 0.0