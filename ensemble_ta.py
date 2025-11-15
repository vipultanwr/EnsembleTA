import pandas as pd
import numpy as np
import talib
from talib import abstract
from src.data_loader import load_crypto_data
import sys
from src.backtest_engine import StrategyBacktester
from src.strategy import getTACombinedSignals
from src.metrics import short_backtest

# Import constants that will NOT be tuned
from config import (
    RANKING_START_DATE, RANKING_END_DATE,
    BACKTEST_START_DATE, BACKTEST_END_DATE,
    COMMISSION_PCT, SLIPPAGE_PCT, INITIAL_CASH
)


class EnsembleRanker:
    """
    Handles the process of fetching data, generating signals,
    and ranking strategies to find the best performers.
    """
    def __init__(self, asset, start_date, end_date, timeframe, signal_shifts):
        self.asset = asset
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        self.signal_shifts = signal_shifts
        self.ranking_data = self._load_data()

    def _load_data(self):
        """Loads data for the entire ranking period at once."""
        return load_crypto_data(self.asset, self.start_date, self.end_date, self.timeframe)

    def generate_rankings(self):
        """
        Generates and ranks all strategies across the entire dataset.
        """
        print(f"Generating signals for {self.asset} ({self.timeframe})...")
        all_signals = getTACombinedSignals(self.ranking_data, returnall=True)
        returns = self.ranking_data.close.pct_change().fillna(0)

        fwd_results = []
        rvs_results = []

        print(f"Ranking {len(all_signals.columns)} strategies...")
        for strategy in all_signals.columns:
            for shift in self.signal_shifts:
                # Forward strategy
                sig = all_signals[strategy].shift(shift).fillna(0)
                ret = returns
                sig_aligned, ret_aligned = sig.align(ret, join='inner', axis=0)
                pnl_fwd = sig_aligned * ret_aligned
                stats_fwd = short_backtest(pnl_fwd, self.timeframe)
                stats_fwd.update({'strategy': strategy, 'shift': shift})
                fwd_results.append(stats_fwd)

                # Reverse strategy
                pnl_rvs = -1 * sig_aligned * ret_aligned
                stats_rvs = short_backtest(pnl_rvs, self.timeframe)
                stats_rvs.update({'strategy': strategy, 'shift': shift})
                rvs_results.append(stats_rvs)

        df_fwd = pd.DataFrame(fwd_results).set_index(['strategy', 'shift'])
        df_rvs = pd.DataFrame(rvs_results).set_index(['strategy', 'shift'])

        print("Strategy ranking generation complete.")
        return df_fwd, df_rvs


def run_ensemble_backtest(top_fwd, top_rvs, asset, timeframe, report_filename=None):
    """
    Runs the final out-of-sample backtest for a given set of top strategies.
    Returns the performance metrics.
    """
    print("\n--- Running Final Ensemble Backtest ---")
    try:
        backtest_df = load_crypto_data(asset, BACKTEST_START_DATE, BACKTEST_END_DATE, timeframe)
    except ValueError as e:
        print(f"Could not fetch data for the final backtest period: {e}")
        return None

    print("Generating signals for backtest period...")
    backtest_signals = getTACombinedSignals(backtest_df, True)

    print("Creating ensemble signal from top strategies...")
    ensemble_signal_series = pd.Series(0.0, index=backtest_signals.index)

    # Add signals from top forward strategies
    if not top_fwd.empty:
        for strat, shift in top_fwd.index:
            if strat in backtest_signals.columns:
                ensemble_signal_series += backtest_signals[strat].shift(shift)

    # Add signals from top reverse strategies
    if not top_rvs.empty:
        for strat, shift in top_rvs.index:
            if strat in backtest_signals.columns:
                ensemble_signal_series += -1 * backtest_signals[strat].shift(shift)

    # Convert the summed votes into a final signal: 1 (buy), -1 (sell), 0 (hold)
    backtest_df['Signals'] = np.sign(ensemble_signal_series).fillna(0)

    print("Running final backtest...")
    bt_backtester = StrategyBacktester(
        commission=COMMISSION_PCT, slippage=SLIPPAGE_PCT, initial_cash=INITIAL_CASH
    )

    # Prepare DataFrame for the backtester
    backtest_df.reset_index(inplace=True)
    backtest_df.rename(columns={'dt': 'date'}, inplace=True)
    bt_backtester.backtest(backtest_df, signal_col='Signals')

    print("\n--- Ensemble Backtest Results ---")
    metrics = bt_backtester.calculate_metrics()
    for key, value in metrics.items():
        print(f"{key:<25}: {value}")

    if report_filename:
        from src.plotting import generate_quantstats_report
        returns = bt_backtester.results['returns']
        generate_quantstats_report(returns, title=f"{asset} {timeframe} Ensemble Strategy", output_filename=report_filename)
    
    return metrics


def run_single_test(asset, timeframe, n_top_strategies, signal_shifts, report_filename=None):
    """
    Runs a full ranking and backtest cycle for a single set of parameters.
    """
    print("\n" + "="*50)
    print(f"Running Test for: ASSET={asset}, TIMEFRAME={timeframe}, N_TOP={n_top_strategies}, SHIFTS={signal_shifts}")
    print("="*50)

    # --- Step 1: Rank all strategies ---
    ranker = EnsembleRanker(
        asset=asset,
        start_date=RANKING_START_DATE,
        end_date=RANKING_END_DATE,
        timeframe=timeframe,
        signal_shifts=signal_shifts
    )
    df_fwd, df_rvs = ranker.generate_rankings()

    # --- Step 2: Select top strategies based on a metric ---
    top_fwd_strategies = df_fwd.sort_values(by='final_return', ascending=False).head(n_top_strategies)
    top_rvs_strategies = df_rvs.sort_values(by='final_return', ascending=False).head(n_top_strategies)

    print(f"\n--- Top {n_top_strategies} Forward Strategies ---")
    print(top_fwd_strategies)
    print(f"\n--- Top {n_top_strategies} Reverse Strategies ---")
    print(top_rvs_strategies)

    # --- Step 3: Run the final out-of-sample backtest ---
    metrics = run_ensemble_backtest(top_fwd_strategies, top_rvs_strategies, asset, timeframe, report_filename=report_filename)

    return metrics
