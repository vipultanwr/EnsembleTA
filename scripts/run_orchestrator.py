import yaml
import itertools
import subprocess
import sys
import os
import json
import pandas as pd

def run_orchestration():
    """
    Runs backtests for multiple combinations of parameters, collects the results,
    and saves them to a master CSV file.
    """
    # --- Load Configuration ---
    # Get the directory where the current script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    config_path = os.path.join(project_root, 'config.yaml')

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    param_grid = config['param_grid']

    # Create all combinations of parameters
    keys, values = zip(*param_grid.items())
    parameter_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    print(f"Starting orchestration for {len(parameter_combinations)} parameter combinations...")
    all_results = []

    # --- Loop through combinations and run tests ---
    for i, params in enumerate(parameter_combinations):
        print(f"\n--- Running combination {i+1}/{len(parameter_combinations)} ---")
        # Use the project_root to build the correct path
        temp_config_path = os.path.join(project_root, 'results', f"temp_config_{i}.yaml")
        try:
            # For the orchestrator, we assume we are running the ensemble_strategy
            strategy_name = 'ensemble_strategy'
            
            # Create a temporary config for this specific run
            run_config = config.copy()
            run_config['param_grid'] = params
            with open(temp_config_path, 'w') as f:
                yaml.dump(run_config, f)

            # Construct the absolute path to run_backtest.py
            script_dir = os.path.dirname(os.path.abspath(__file__))
            backtest_script_path = os.path.join(script_dir, 'run_backtest.py')

            # Set the PYTHONPATH for the subprocess to find the 'src' module
            env = os.environ.copy()
            env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')

            # Call run_backtest.py as a subprocess
            command = [
                sys.executable,
                backtest_script_path,
                '--strategy', strategy_name,
                '--config', temp_config_path
            ]
            process = subprocess.run(command, check=True, capture_output=True, text=True, env=env)

            # Parse the JSON output from the subprocess
            result_metrics = json.loads(process.stdout)
            
            # Add the parameters for this run to the results dictionary
            result_metrics.update(params)
            all_results.append(result_metrics)
            print(f"Successfully completed combination {i+1}. Sharpe Ratio: {result_metrics.get('Sharpe Ratio', 'N/A')}")

        except subprocess.CalledProcessError as e:
            print(f"An error occurred in the subprocess for combination {i+1}: {params}", file=sys.stderr)
            print(f"Return Code: {e.returncode}", file=sys.stderr)
            print(f"--- Subprocess stdout ---\n{e.stdout}\n-------------------------", file=sys.stderr)
            print(f"--- Subprocess stderr ---\n{e.stderr}\n-------------------------", file=sys.stderr)
            continue
        except json.JSONDecodeError as e:
            print(f"An error occurred while parsing JSON for combination {i+1}: {params}", file=sys.stderr)
            print(f"Error: {e}", file=sys.stderr)
            if 'process' in locals():
                print(f"--- Subprocess stdout that failed parsing ---\n{process.stdout}\n-------------------------------------------", file=sys.stderr)
            continue
        except Exception as e:
            print(f"A general error occurred during test combination {i+1}: {params}", file=sys.stderr)
            print(f"Error: {e}", file=sys.stderr)
            continue

        finally:
            # Clean up the temporary config file to prevent clutter
            if os.path.exists(temp_config_path):
                os.remove(temp_config_path)

    # --- Save all results to a master CSV file ---
    if all_results:
        results_df = pd.DataFrame(all_results)
        # Reorder columns to have parameters first
        param_keys = list(param_grid.keys())
        metric_keys = [col for col in results_df.columns if col not in param_keys]
        results_df = results_df[param_keys + metric_keys]
        
        output_path = os.path.join(project_root, 'results', 'master_results.csv')
        results_df.to_csv(output_path, index=False)
        print(f"\n--- Orchestration Complete ---")
        print(f"Master results saved to {output_path}")
    else:
        print("\n--- Orchestration Complete ---")
        print("No results were generated.")

if __name__ == '__main__':
    run_orchestration()

