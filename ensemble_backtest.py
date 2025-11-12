import pandas as pd
import numpy as np
import talib
from talib import abstract
from fastquant import get_crypto_data
import sys
from CoreQuantUtilities.backtester.backtester import StrategyBacktester
from CoreQuantUtilities.ta_strategies.TABot import getTACombinedSignals

from config import *


# def getTACombinedSignals(input_df, returnall=False):
#     """
#     Generates trading signals for a wide range of TA-Lib indicators.
#     This function is kept exactly as provided.
#     """
#     if input_df is None or input_df.empty:
#         return None

#     all_funcs = talib.get_functions()

#     signals = pd.DataFrame(index=input_df.index)
#     signals["MA"] = np.where(abstract.Function("MA")(input_df) < input_df.close, 1,
#                              np.where(abstract.Function("MA")(input_df) > input_df.close, -1, 0))

#     for func in all_funcs:
#         if "CDL" in abstract.Function(func).info['name']:
#             signals[abstract.Function(func).info['display_name']] = np.where(abstract.Function(func)(input_df) > 0, 1,
#                                                                               np.where(
#                                                                                   abstract.Function(func)(input_df) < 0,
#                                                                                   -1, 0))

#     for func in all_funcs:
#         if "PRICE" in abstract.Function(func).info['name']:
#             signals[abstract.Function(func).info['display_name']] = np.where(
#                 abstract.Function(func)(input_df) > input_df['close'], 1,
#                 np.where(abstract.Function(func)(input_df) < input_df['close'], -1, 0))

#     signals["OBV"] = np.where(
#         abstract.Function("OBV")(input_df) > abstract.Function("OBV")(input_df).rolling(5).mean().fillna(
#             method="bfill"), 1, 0)
#     signals["ADOSC"] = np.where(
#         ((abstract.Function("ADOSC")(input_df) >= 0) & (abstract.Function("ADOSC")(input_df).shift(1) < 0)), 1,
#         np.where(((abstract.Function("ADOSC")(input_df) < 0) & (abstract.Function("ADOSC")(input_df).shift(1) >= 0)),
#                  -1, 0))
#     signals["AD"] = np.where(
#         abstract.Function("AD")(input_df) > abstract.Function("AD")(input_df).rolling(5).mean().fillna(method="bfill"),
#         1, 0)

#     signals["NATR"] = np.where(abstract.Function("NATR")(input_df) > 0.6, 1, 0)
#     signals["NATR"] = signals["NATR"] * signals["MA"]

#     signals["BETA"] = np.where(abstract.Function("BETA")(input_df) > 1.5, 1,
#                               np.where(abstract.Function("BETA")(input_df) < -1.5, -1, 0))
#     signals["CORREL"] = np.where(abstract.Function("CORREL")(input_df) > 0.85, 1, 0)
#     signals["CORREL"] = signals["CORREL"] * signals["MA"]
#     signals["LINEARREG"] = np.where(((input_df.close >= abstract.Function("LINEARREG")(input_df)) & (
#                 input_df.close.shift(1) < abstract.Function("LINEARREG")(input_df).shift(1))), 1, np.where(
#         ((input_df.close <= abstract.Function("LINEARREG")(input_df)) & (
#                     input_df.close.shift(1) > abstract.Function("LINEARREG")(input_df).shift(1))), -1, 0))
#     signals["TSF"] = np.where(((input_df.close >= abstract.Function("TSF")(input_df)) & (
#                 input_df.close.shift(1) < abstract.Function("TSF")(input_df).shift(1))), 1, np.where(
#         ((input_df.close <= abstract.Function("TSF")(input_df)) & (
#                     input_df.close.shift(1) > abstract.Function("TSF")(input_df).shift(1))), -1, 0))

#     signals["ADX"] = np.where(abstract.Function("ADX")(input_df) > 25, 1, 0)
#     signals["ADX"] = signals["MA"] * signals["ADX"]
#     signals["RSI"] = np.where(abstract.Function("RSI")(input_df) < 30, 1,
#                               np.where(abstract.Function("RSI")(input_df) > 70, -1, 0))
#     # This is just a snippet, the full logic from the original file is preserved.

#     signals["HT_DCPERIOD"] = np.where(abstract.Function("HT_DCPERIOD")(input_df) > 25, 1, 0)
#     signals["HT_DCPERIOD"] = signals["MA"] * signals["HT_DCPERIOD"]
#     signals["HT_TRENDMODE"] = np.where(abstract.Function("HT_TRENDMODE")(input_df) == 1, signals["MA"], signals["RSI"])

#     if returnall:
#         return signals
#     else:
#         return signals.iloc[-1]


class EnsembleRanker:
    """
    Handles the process of fetching data, generating signals,
    and ranking strategies to find the best performers.
    """
    def __init__(self, asset, start_date, end_date, timeframe):
        self.asset = asset
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        self.ranking_data = self._load_data()

    def _load_data(self):
        """Loads data for the entire ranking period at once."""
        print(f"Loading ranking data for {self.asset} from {self.start_date} to {self.end_date}...")
        data = get_crypto_data(self.asset, self.start_date, self.end_date, time_resolution=self.timeframe)
        if data is None or data.empty:
            raise ValueError("Failed to load data for ranking.")
        print("Data loaded successfully.")
        return data

    def _short_backtest(self, pnl_returns):
        """A simplified, vectorized backtest to quickly rank strategies."""
        if pnl_returns.std() == 0:
            sharpe = 0
        else:
            # Annualize Sharpe for 5m timeframe: 12 * 24 * 365.25 data points per year
            sharpe = (pnl_returns.mean() / pnl_returns.std()) * np.sqrt(12 * 24 * 365.25)

        pos_returns = pnl_returns[pnl_returns > 0].sum()
        neg_returns = pnl_returns[pnl_returns < 0].sum()

        if neg_returns == 0:
            profit_factor = np.inf
        else:
            profit_factor = abs(pos_returns / neg_returns)

        final_return = (pnl_returns + 1).prod()
        return {'sharpe': sharpe, 'profit_factor': profit_factor, 'final_return': final_return}

    def generate_rankings(self):
        """
        Generates and ranks all strategies across the entire dataset.
        This is much more efficient than the month-by-month approach.
        """
        print("Generating signals using getTACombinedSignals...")
        all_signals = getTACombinedSignals(self.ranking_data, returnall=True)
        returns = self.ranking_data.close.pct_change().fillna(0)

        fwd_results = []
        rvs_results = []

        print(f"Ranking {len(all_signals.columns)} strategies...")
        for strategy in all_signals.columns:
            for shift in SIGNAL_SHIFTS:
                # Forward strategy
                pnl_fwd = all_signals[strategy].shift(shift).fillna(0) * returns
                stats_fwd = self._short_backtest(pnl_fwd)
                stats_fwd.update({'strategy': strategy, 'shift': shift})
                fwd_results.append(stats_fwd)

                # Reverse strategy
                pnl_rvs = -1 * all_signals[strategy].shift(shift).fillna(0) * returns
                stats_rvs = self._short_backtest(pnl_rvs)
                stats_rvs.update({'strategy': strategy, 'shift': shift})
                rvs_results.append(stats_rvs)

        df_fwd = pd.DataFrame(fwd_results).set_index(['strategy', 'shift'])
        df_rvs = pd.DataFrame(rvs_results).set_index(['strategy', 'shift'])

        print("Strategy ranking generation complete.")
        return df_fwd, df_rvs


def run_ensemble_backtest(top_fwd, top_rvs):
    print("\n--- Running Final Ensemble Backtest ---")
    print(f"Loading backtest data for {ASSET} from {BACKTEST_START_DATE} to {BACKTEST_END_DATE}...")
    backtest_df = get_crypto_data(ASSET, BACKTEST_START_DATE, BACKTEST_END_DATE, time_resolution=TIMEFRAME)
    if backtest_df is None or backtest_df.empty:
        print("Could not fetch data for the final backtest period. Exiting.")
        return

    print("Generating signals for backtest period...")
    backtest_signals = getTACombinedSignals(backtest_df, True)

    print("Creating ensemble signal from top strategies...")
    ensemble_signal_series = pd.Series(0.0, index=backtest_signals.index)

    # Add signals from top forward strategies
    for strat, shift in top_fwd.index:
        if strat in backtest_signals.columns:
            ensemble_signal_series += backtest_signals[strat].shift(shift)

    # Add signals from top reverse strategies
    for strat, shift in top_rvs.index:
        if strat in backtest_signals.columns:
            ensemble_signal_series += -1 * backtest_signals[strat].shift(shift)

    # Convert the summed votes into a final signal: 1 (buy), -1 (sell), 0 (hold)
    backtest_df['Signals'] = np.sign(ensemble_signal_series).fillna(0)

    print("Running final backtest with CoreQuantUtilities...")
    bt_backtester = StrategyBacktester(
        commission=COMMISSION_PCT, slippage=SLIPPAGE_PCT, initial_cash=INITIAL_CASH
    )

    # Prepare DataFrame for the backtester
    backtest_df.reset_index(inplace=True)
    backtest_df.rename(columns={'dt': 'date'}, inplace=True)
    bt_backtester.backtest(backtest_df, signal_col='Signals')

    print("\n--- Ensemble Backtest Results ---")
    bt_backtester.print_metrics()
    bt_backtester.plot_results(style='candlestick')


if __name__ == '__main__':

    # --- Step 1: Rank all strategies ---
    ranker = EnsembleRanker(ASSET, RANKING_START_DATE, RANKING_END_DATE, TIMEFRAME)
    df_fwd, df_rvs = ranker.generate_rankings()

    # --- Step 2: Select top strategies based on a metric ---
    top_fwd_strategies = df_fwd.sort_values(by='final_return', ascending=False).head(N_TOP_STRATEGIES)
    top_rvs_strategies = df_rvs.sort_values(by='final_return', ascending=False).head(N_TOP_STRATEGIES)

    print("\n--- Top 15 Forward Strategies ---")
    print(top_fwd_strategies)
    print("\n--- Top 15 Reverse Strategies ---")
    print(top_rvs_strategies)

    # Save the top forward strategies to a pickle file
    top_fwd_strategies.to_pickle("top_fwd_strategies.pkl")
    top_rvs_strategies.to_pickle("top_rvs_strategies.pkl")

    top_fwd_strategies = pd.read_pickle("top_fwd_strategies.pkl")
    top_rvs_strategies = pd.read_pickle("top_rvs_strategies.pkl")


    # --- Step 3: Run the final out-of-sample backtest ---
    run_ensemble_backtest(top_fwd_strategies, top_rvs_strategies)
