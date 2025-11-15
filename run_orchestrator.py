import yaml
import itertools
import subprocess

def run_orchestration():
    """
    Runs backtests for multiple combinations of parameters by calling run_backtest.py.
    """
    # --- Load Configuration ---
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    param_grid = config['param_grid']

    # Create all combinations of parameters
    keys, values = zip(*param_grid.items())
    parameter_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    print(f"Starting orchestration for {len(parameter_combinations)} parameter combinations...")

    # --- Loop through combinations and run tests ---
    for i, params in enumerate(parameter_combinations):
        print(f"\n--- Running combination {i+1}/{len(parameter_combinations)} ---")
        try:
            # For the orchestrator, we assume we are running the ensemble_strategy
            strategy_name = 'ensemble_strategy'
            
            # Create a temporary config for this specific run
            run_config = config.copy()
            run_config['param_grid'] = params
            temp_config_path = f"results/temp_config_{i}.yaml"
            with open(temp_config_path, 'w') as f:
                yaml.dump(run_config, f)

            # Call run_backtest.py as a subprocess
            command = [
                '~/.pyenv/versions/project1/bin/python',
                'run_backtest.py',
                '--strategy', strategy_name,
                '--config', temp_config_path
            ]
            subprocess.run(command, check=True)

        except Exception as e:
            print(f"An error occurred during test combination {i+1}: {params}")
            print(f"Error: {e}")
            continue

    print("\n--- Orchestration Complete ---")

if __name__ == '__main__':
    run_orchestration()

