import pandas as pd
import numpy as np
from CoreQuantUtilities.ta_strategies.TABot import getTACombinedSignals
from src.data_loader import load_data
from src.metrics import short_backtest
import sys

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
        return load_data(self.asset, self.start_date, self.end_date, self.timeframe)

    def generate_rankings(self):
        """
        Generates and ranks all strategies across the entire dataset.
        """
        print(f"Generating signals for {self.asset} ({self.timeframe})...", file=sys.stderr)
        all_signals = getTACombinedSignals(self.ranking_data, returnall=True)
        returns = self.ranking_data.close.pct_change().fillna(0)

        fwd_results = []
        rvs_results = []

        print(f"Ranking {len(all_signals.columns)} strategies...", file=sys.stderr)
        for strategy in all_signals.columns:
            for shift in self.signal_shifts:
                sig = all_signals[strategy].shift(shift).fillna(0)
                ret = returns
                sig_aligned, ret_aligned = sig.align(ret, join='inner', axis=0)
                pnl_fwd = sig_aligned * ret_aligned
                stats_fwd = short_backtest(pnl_fwd, self.timeframe)
                stats_fwd.update({'strategy': strategy, 'shift': shift})
                fwd_results.append(stats_fwd)

                pnl_rvs = -1 * sig_aligned * ret_aligned
                stats_rvs = short_backtest(pnl_rvs, self.timeframe)
                stats_rvs.update({'strategy': strategy, 'shift': shift})
                rvs_results.append(stats_rvs)

        df_fwd = pd.DataFrame(fwd_results).set_index(['strategy', 'shift'])
        df_rvs = pd.DataFrame(rvs_results).set_index(['strategy', 'shift'])

        print("Strategy ranking generation complete.", file=sys.stderr)
        return df_fwd, df_rvs

def generate_signals(data, **params):
    """
    Generates ensemble signals based on ranking top strategies.
    """
    asset = params.get('asset')
    timeframe = params.get('timeframe')
    n_top_strategies = params.get('n_top_strategies')
    signal_shifts = params.get('signal_shifts')
    ranking_start_date = params.get('ranking_start_date')
    ranking_end_date = params.get('ranking_end_date')

    # --- Step 1: Rank all strategies ---
    ranker = EnsembleRanker(
        asset=asset,
        start_date=ranking_start_date,
        end_date=ranking_end_date,
        timeframe=timeframe,
        signal_shifts=signal_shifts
    )
    df_fwd, df_rvs = ranker.generate_rankings()

    # --- Step 2: Select top strategies based on a metric ---
    top_fwd_strategies = df_fwd.sort_values(by='final_return', ascending=False).head(n_top_strategies)
    top_rvs_strategies = df_rvs.sort_values(by='final_return', ascending=False).head(n_top_strategies)

    print(f"\n--- Top {n_top_strategies} Forward Strategies ---", file=sys.stderr)
    print(top_fwd_strategies, file=sys.stderr)
    print(f"\n--- Top {n_top_strategies} Reverse Strategies ---", file=sys.stderr)
    print(top_rvs_strategies, file=sys.stderr)

    # --- Step 3: Generate ensemble signal for the backtest period ---
    print("Generating signals for backtest period...", file=sys.stderr)
    backtest_signals = getTACombinedSignals(data, True)

    print("Creating ensemble signal from top strategies...", file=sys.stderr)
    ensemble_signal_series = pd.Series(0.0, index=backtest_signals.index)

    if not top_fwd_strategies.empty:
        for strat, shift in top_fwd_strategies.index:
            if strat in backtest_signals.columns:
                ensemble_signal_series += backtest_signals[strat].shift(shift)

    if not top_rvs_strategies.empty:
        for strat, shift in top_rvs_strategies.index:
            if strat in backtest_signals.columns:
                ensemble_signal_series += -1 * backtest_signals[strat].shift(shift)

    # Convert the summed votes into a final signal: 1 (buy), -1 (sell), 0 (hold)
    final_signal = np.sign(ensemble_signal_series).fillna(0)
    
    return pd.DataFrame({'signal': final_signal})
