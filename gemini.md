---

### Housekeeping TODO

- [ ] **Consolidate Top-Level Scripts:** Move `run_*.py` and `generate_dashboard.py` into a new `scripts/` directory.
- [ ] **Organize Documentation Assets:** Move `project_workflow.png` into a new `docs/images/` directory.
- [ ] **Unify Source Code Layout:** Move the `strategies/` directory into `src/` and update imports.
- [ ] **Clean Up Build Artifacts:** Remove `build/` and `*.egg-info/` directories and add them to `.gitignore`.
### Development Log

*   **Dependency Management with `uv`:** Migrated the project's dependency management from a mixed `conda`/`pip` setup to `uv`. This modernizes the workflow, significantly improves installation speed, and ensures reproducibility. Introduced `pyproject.toml` for direct dependency management and updated `README.md` with the new setup instructions.
*   **Fix Orchestration Pipeline:** Repaired the entire orchestration and results aggregation pipeline. The orchestrator now correctly captures results from backtest subprocesses and generates the `master_results.csv` file. This involved a major refactoring to use a clean JSON data channel (`stdout`) while redirecting all logs to `stderr`. Fixed numerous cascading bugs, including `NameError`s, `JSONDecodeError`s, and hardcoded Python paths.
*   **Modernized Dashboard UI:** Updated the `generate_dashboard.py` script to create a `results_dashboard.html` file with an "Apple glass screen-like modern UI design". This involved adding CSS for a glassmorphism effect, updating fonts, and improving the overall layout.
*   **Expanded Hyperparameters:** Researched and updated the `param_grid` in `config.py` with a much larger and more diverse set of hyperparameters for a large-scale backtest. This included adding more assets, timeframes, a wider range of `n_top_strategies`, and more `signal_shifts`.
*   **Large-Scale Backtest:** Executed the `run_orchestrator.py` script to run the backtest with the new hyperparameters, generating a new `master_results.csv` file.
*   **Dashboard Update:** Regenerated the `results_dashboard.html` to display the results from the new backtest.
*   **Gitignore Update:** Updated the `.gitignore` file to prevent `unused_files/`, `results/`, `__pycache__/`, and `.DS_Store` from being pushed to the remote repository.
*   **Interactive Dashboard:** Created an interactive HTML dashboard (`results_dashboard.html`) to display master results using DataTables.js. This makes it easy to search, sort, and compare the results of different hyperparameter combinations.
*   **Automated Reporting:** Modified the orchestration process to generate a unique QuantStats report for every backtest run. The dashboard rows are clickable and link to the detailed HTML report for each run.
*   **Metrics Correction:** Fixed the misleading `Annualized Return` calculation by extending the default backtest period to a full year in `config.py`, ensuring more realistic and statistically sound results.
*   **Advanced Visualization:** Integrated the `quantstats` library to generate comprehensive HTML performance reports, providing a professional and in-depth view of the strategy's performance. A new `src/plotting.py` module was created for this purpose.
*   **Centralized Hyperparameters:** Moved the `param_grid` definition from `run_orchestrator.py` to `config.py` to centralize all configuration parameters, making the project easier to manage and tune.
*   **Hyperparameter Tuning:** Implemented an orchestration script (`run_orchestrator.py`) to perform a grid search over a defined set of parameters (`asset`, `timeframe`, `n_top_strategies`, `signal_shifts`). This allows for systematic evaluation of different strategy configurations.
*   **Code Refactoring:** Refactored `ensemble_backtest.py` into a callable library function (`run_single_test`) to be used by the orchestrator.
*   **Project Structuring:** Implemented a professional, reproducible project structure.
    *   Created a comprehensive `README.md` with project overview, setup, and usage instructions.
    *   Generated `requirements.txt` and restored `environment.yml` for robust dependency management.
    *   Established a `tests/` directory with an initial test for the metrics module to enforce code quality.
    *   Restored `data/` and `notebooks/` directories to the project root.
*   **Modularization:** Refactored the project by moving core components into the `src` directory.
    *   Strategy generation logic moved to `src/strategy.py`.
    *   Backtesting engine (`StrategyBacktester`) moved to `src/backtest_engine.py`, making the project self-contained.
    *   Data loading functionality centralized in `src/data_loader.py`.
    *   Metrics calculations (`short_backtest`, `get_annualization_factor`) moved to `src/metrics.py`.
*   **Project Cleanup:** Moved all unused files and directories into a dedicated `unused_files` folder to declutter the project structure.
*   **Git:** Created checkpoints for all major refactoring and structuring changes.
*   **Configuration:** Added a comprehensive `.gitignore` file for Python projects and updated `config.py` to only contain fixed parameters.\n*   **Execution Environment**: All Python commands must be executed within the `project1` pyenv virtual environment.
