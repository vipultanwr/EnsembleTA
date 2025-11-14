"""
Configuration file for the ensemble backtest.

This file contains the fixed parameters that are not tuned during orchestration.
Tunable parameters are defined in `run_orchestrator.py`.
"""

# --- Fixed Date Parameters ---
RANKING_START_DATE = '2021-01-01'
RANKING_END_DATE = '2021-12-31'
BACKTEST_START_DATE = '2022-01-01'
BACKTEST_END_DATE = '2022-12-31'

# --- Fixed Backtesting Parameters ---
INITIAL_CASH = 100000.0
COMMISSION_PCT = 0.0
SLIPPAGE_PCT = 0.0

# --- Tunable Parameters (Hyperparameters for Orchestration) ---
param_grid = {
    'asset': ['BTC/USDT', 'ETH/USDT'],
    'timeframe': ['1h', '4h'],
    'n_top_strategies': [5, 10],
    'signal_shifts': [[1], [1, 2]]
}