import pandas as pd
import pytest

from stockanalyzer import metrics


def make_price_series(values):
    dates = pd.date_range("2024-01-01", periods=len(values), freq="D")
    return pd.Series(values, index=dates, dtype=float)


def test_daily_returns_basic():
    prices = make_price_series([100, 110, 99])
    returns = metrics.daily_returns(prices)
    assert pytest.approx(returns.iloc[0], rel=1e-6) == 0.10
    assert pytest.approx(returns.iloc[1], rel=1e-6) == -0.10


def test_annualized_return_flat_price_is_zero():
    prices = make_price_series([100] * 30)
    assert metrics.annualized_return(prices) == pytest.approx(0.0)


def test_annualized_volatility_zero_for_constant_returns():
    # Constant daily growth rate -> zero volatility.
    prices = make_price_series([100 * (1.001**i) for i in range(50)])
    vol = metrics.annualized_volatility(prices)
    assert vol == pytest.approx(0.0, abs=1e-6)


def test_sharpe_ratio_nan_when_volatility_zero():
    prices = make_price_series([100] * 10)
    assert metrics.sharpe_ratio(prices) != metrics.sharpe_ratio(prices)  # NaN != NaN


def test_max_drawdown_detects_peak_to_trough():
    prices = make_price_series([100, 120, 90, 95, 130])
    dd = metrics.max_drawdown(prices)
    # Peak of 120 down to trough of 90 -> -25%
    assert dd == pytest.approx(-0.25, rel=1e-6)


def test_max_drawdown_zero_for_monotonic_increase():
    prices = make_price_series([100, 110, 120, 130])
    assert metrics.max_drawdown(prices) == pytest.approx(0.0)


def test_beta_of_series_with_itself_is_one():
    prices = make_price_series([100, 102, 101, 105, 103, 108])
    assert metrics.beta(prices, prices) == pytest.approx(1.0, rel=1e-6)


def test_beta_nan_for_too_short_series():
    prices = make_price_series([100])
    assert metrics.beta(prices, prices) != metrics.beta(prices, prices)
