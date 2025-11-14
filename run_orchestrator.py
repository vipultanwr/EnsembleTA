import pandas as pd
import itertools
import os
from ensemble_backtest import run_single_test
from config import param_grid

def run_orchestration():
    """
    Runs the ensemble backtest for multiple combinations of parameters (grid search).
    """



    # Create all combinations of parameters
    keys, values = zip(*param_grid.items())
    parameter_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    all_results = []

    print(f"Starting orchestration for {len(parameter_combinations)} parameter combinations...")

    # --- Loop through combinations and run tests ---
    for i, params in enumerate(parameter_combinations):
        print(f"\n--- Running combination {i+1}/{len(parameter_combinations)} ---")
        try:
            # Define a unique report filename for this run
            shifts_str = '_'.join(map(str, params['signal_shifts']))
            report_filename = f"results/report_{params['asset'].replace('/', '_')}_{params['timeframe']}_{params['n_top_strategies']}_{shifts_str}.html"

            # Run the test for the current parameter set
            metrics = run_single_test(
                asset=params['asset'],
                timeframe=params['timeframe'],
                n_top_strategies=params['n_top_strategies'],
                signal_shifts=params['signal_shifts'],
                report_filename=report_filename
            )

            if metrics:
                # Combine parameters and metrics into a single dictionary
                result_row = params.copy()
                result_row.update(metrics)
                result_row['report_url'] = report_filename  # Add report URL for the dashboard
                all_results.append(result_row)
            else:
                print(f"Test failed for parameters: {params}")

        except Exception as e:
            print(f"An error occurred during test combination {i+1}: {params}")
            print(f"Error: {e}")
            # Optionally, log the error and continue
            continue

    # --- Save results to CSV ---
    if not all_results:
        print("No results were generated. Exiting.")
        return

    results_df = pd.DataFrame(all_results)

    # Create results directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')

    output_path = 'results/master_results.csv'
    print(f"\nSaving all results to {output_path}...")
    results_df.to_csv(output_path, index=False)

    print("\n--- Orchestration Complete ---")
    print("Top 5 results based on Sharpe Ratio:")
    print(results_df.sort_values(by='Sharpe Ratio', ascending=False).head(5))


if __name__ == '__main__':
    run_orchestration()
