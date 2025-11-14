"""
Configuration file for the ensemble backtest.

This file contains the fixed parameters that are not tuned during orchestration.
Tunable parameters are defined in `run_orchestrator.py`.
"""

# --- Fixed Date Parameters ---
RANKING_START_DATE = '2021-01-01'
RANKING_END_DATE = '2021-03-31'
BACKTEST_START_DATE = '2022-05-01'
BACKTEST_END_DATE = '2022-06-01'

# --- Fixed Backtesting Parameters ---
INITIAL_CASH = 100000.0
COMMISSION_PCT = 0.0
SLIPPAGE_PCT = 0.0