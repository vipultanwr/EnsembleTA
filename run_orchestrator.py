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
            # Run the test for the current parameter set
            metrics = run_single_test(
                asset=params['asset'],
                timeframe=params['timeframe'],
                n_top_strategies=params['n_top_strategies'],
                signal_shifts=params['signal_shifts']
            )

            if metrics:
                # Combine parameters and metrics into a single dictionary
                result_row = params.copy()
                result_row.update(metrics)
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
    best_results = results_df.sort_values(by='Sharpe Ratio', ascending=False)
    print("Top 5 results based on Sharpe Ratio:")
    print(best_results.head(5))

    # --- Generate a detailed report for the best run ---
    if not best_results.empty:
        print("\n--- Generating detailed report for the best performing strategy ---")
        best_params = best_results.iloc[0].to_dict()
        run_single_test(
            asset=best_params['asset'],
            timeframe=best_params['timeframe'],
            n_top_strategies=int(best_params['n_top_strategies']),
            signal_shifts=best_params['signal_shifts'],
            plot=True
        )


if __name__ == '__main__':
    run_orchestration()
