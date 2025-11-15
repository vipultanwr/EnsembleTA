import pandas as pd
import numpy as np
from src.strategy import generate_ensemble_signal

def test_generate_ensemble_signal():
    """
    Tests the generate_ensemble_signal function with a sample DataFrame.
    """
    # Create a sample DataFrame of strategy signals
    data = {
        'strat1': [1, -1, 0, 1, -1],
        'strat2': [1, 1, -1, -1, 0],
        'strat3': [-1, 1, 0, 1, 1]
    }
    index = pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'])
    strategy_signals = pd.DataFrame(data, index=index)

    # Expected ensemble signal
    # Sums: [1, 1, -1, 1, 0]
    # Expected: [1, 1, -1, 1, 0]
    expected_data = {'ensemble_signal': [1, 1, -1, 1, 0]}
    expected_ensemble_signal = pd.DataFrame(expected_data, index=index)

    # Generate the ensemble signal
    ensemble_signal = generate_ensemble_signal(strategy_signals)

    # Assert that the output is correct
    pd.testing.assert_frame_equal(ensemble_signal, expected_ensemble_signal)

def test_generate_ensemble_signal_empty_input():
    """
    Tests the generate_ensemble_signal function with an empty DataFrame.
    """
    # Create an empty DataFrame
    strategy_signals = pd.DataFrame()

    # Expected empty ensemble signal
    expected_ensemble_signal = pd.DataFrame(index=strategy_signals.index, data={'ensemble_signal': []})

    # Generate the ensemble signal
    ensemble_signal = generate_ensemble_signal(strategy_signals)

    # Assert that the output is correct
    pd.testing.assert_frame_equal(ensemble_signal, expected_ensemble_signal)
