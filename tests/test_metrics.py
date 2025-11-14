import pytest
from src.metrics import get_annualization_factor

def test_get_annualization_factor_daily():
    """Test daily annualization factor."""
    assert get_annualization_factor('1d') == 365.25

def test_get_annualization_factor_hourly():
    """Test hourly annualization factor."""
    assert get_annualization_factor('1h') == (24 / 1) * 365.25
    assert get_annualization_factor('4h') == (24 / 4) * 365.25

def test_get_annualization_factor_minutely():
    """Test minutely annualization factor."""
    assert get_annualization_factor('1m') == (60 / 1) * 24 * 365.25
    assert get_annualization_factor('15m') == (60 / 15) * 24 * 365.25

def test_get_annualization_factor_default():
    """Test default annualization factor for unknown timeframe."""
    assert get_annualization_factor('unknown') == 365.25
