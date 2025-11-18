import argparse
import yaml
import importlib
import sys
import os
import pandas as pd

print(f"sys.path in run_backtest: {sys.path}", file=sys.stderr)

from src.data_loader import load_data
from CoreQuantUtilities.backtester.backtester import StrategyBacktester
from src.plotting import generate_curated_report

import json

def run_backtest(strategy_name, config_path):
    """
    Runs a backtest for a single strategy.
    """
    # Get project root (re-add this)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))

    # --- 1. Load Configuration ---
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # --- 2. Load Strategy ---
    try:
        strategy_module = importlib.import_module(f"src.strategies.{strategy_name}")
    except ImportError:
        print(f"CRITICAL: Failed to import strategy '{strategy_name}'. Check if the file exists at 'src/strategies/{strategy_name}.py' and that the project's src directory is on the python path.", file=sys.stderr)
        sys.exit(1)

    # --- 3. Load Data ---
    asset = config['param_grid']['asset']
    timeframe = config['param_grid']['timeframe']
    backtest_start_date = config['backtest_start_date']
    backtest_end_date = config['backtest_end_date']
    
    data = load_data(asset, backtest_start_date, backtest_end_date, timeframe)
    
    if data.empty:
        print(f"CRITICAL: No data loaded for asset '{asset}'. Halting backtest.", file=sys.stderr)
        sys.exit(1)

    # Calculate benchmark returns BEFORE resetting the index
    benchmark_returns = data['close'].pct_change()

    # Standardize index to 'date' column for the backtester
    data.index.name = 'date'
    data.reset_index(inplace=True)

    # --- 4. Generate Signals ---
    params = {**config, **config['param_grid']}
    signals_df = strategy_module.generate_signals(data, **params)
    data['signal'] = signals_df['signal']

    # --- 5. Run Backtest ---
    bt_backtester = StrategyBacktester(
        commission=config['commission_pct'],
        slippage=config['slippage_pct'],
        initial_cash=config['initial_cash']
    )
    
    bt_backtester.backtest(data, signal_col='signal')

    # --- 6. Save Results and Output JSON ---
    metrics = bt_backtester.calculate_metrics()
    
    # --- Data Alignment for Plotting ---
    # The backtester operates on a RangeIndex, so we need to align the results
    # back to a DatetimeIndex for correct plotting.
    
    # Get the original DatetimeIndex from the data *before* it was reset
    datetime_index = pd.to_datetime(data['date']).dt.tz_localize('UTC')
    
    # Align strategy returns
    # The returns series from the backtester is already aligned with the original data's length
    strategy_returns = bt_backtester.results['returns']
    strategy_returns.index = datetime_index
    
    # Align benchmark returns
    benchmark_returns.index = datetime_index
    
    # Align trades
    # The trades index from the backtester is already UTC timezone-aware
    trades_df = bt_backtester.trades
    trades_df.index = pd.to_datetime(trades_df.index)
    
    # --- Create a unique filename for the report ---
    n_top = config['param_grid']['n_top_strategies']
    shifts = config['param_grid']['signal_shifts']
    # Create a filename-safe string for the shifts list, e.g., [1, 2, 3] -> "1_2_3"
    shifts_str = '_'.join(map(str, shifts))
    
    # Sanitize asset name for filename
    asset_str = asset.replace('/', '')

    report_filename = os.path.join(
        project_root, 
        'results', 
        f"{strategy_name}_{asset_str}_{timeframe}_top{n_top}_shifts{shifts_str}.html"
    )

    # Generate and save the curated report
    generate_curated_report(
        returns=strategy_returns,
        benchmark_returns=benchmark_returns,
        trades=trades_df,
        metrics=metrics,
        title=f"{strategy_name} {asset} {timeframe} (Top {n_top}, Shifts {shifts})",
        output_filename=report_filename
    )

    
    # Add report URL to metrics and print as JSON for the orchestrator
    metrics['report_url'] = report_filename
    print(json.dumps(metrics))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a single strategy backtest.')
    parser.add_argument('--strategy', type=str, required=True, help='The name of the strategy file in the strategies/ directory (without .py)')
    parser.add_argument('--config', type=str, default='config.yaml', help='The path to the configuration file.')
    args = parser.parse_args()

    try:
        run_backtest(args.strategy, args.config)
    except Exception as e:
        import traceback
        print(f"An unhandled exception occurred in run_backtest: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)