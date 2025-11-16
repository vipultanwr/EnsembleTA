import argparse
import yaml
import importlib
import sys
from src.data_loader import load_crypto_data
from CoreQuantUtilities.backtester.backtester import StrategyBacktester
from src.plotting import generate_quantstats_report

import json

def run_backtest(strategy_name, config_path):
    """
    Runs a backtest for a single strategy.
    """
    # --- 1. Load Configuration ---
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # --- 2. Load Strategy ---
    try:
        strategy_module = importlib.import_module(f"strategies.{strategy_name}")
    except ImportError:
        print(f"Error: Strategy '{strategy_name}' not found in the 'strategies' directory.", file=sys.stderr)
        return

    # --- 3. Load Data ---
    asset = config['param_grid']['asset'] # Use first asset for single run
    timeframe = config['param_grid']['timeframe'] # Use first timeframe
    backtest_start_date = config['backtest_start_date']
    backtest_end_date = config['backtest_end_date']
    data = load_crypto_data(asset, backtest_start_date, backtest_end_date, timeframe)
    
    data.reset_index(inplace=True)
    data.rename(columns={'dt': 'date'}, inplace=True)

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
    
    # Generate and save the QuantStats report
    report_filename = f"results/{strategy_name}_{asset.replace('/', '')}_{timeframe}.html"
    generate_quantstats_report(bt_backtester.results['returns'], title=f"{strategy_name} {asset} {timeframe}", output_filename=report_filename)
    
    # Add report URL to metrics and print as JSON for the orchestrator
    metrics['report_url'] = report_filename
    print(json.dumps(metrics))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a single strategy backtest.')
    parser.add_argument('--strategy', type=str, required=True, help='The name of the strategy file in the strategies/ directory (without .py)')
    parser.add_argument('--config', type=str, default='config.yaml', help='The path to the configuration file.')
    args = parser.parse_args()

    run_backtest(args.strategy, args.config)