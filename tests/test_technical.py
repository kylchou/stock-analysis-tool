import pandas as pd
import pytest

from stockanalyzer import technical


def make_price_series(values):
    dates = pd.date_range("2024-01-01", periods=len(values), freq="D")
    return pd.Series(values, index=dates, dtype=float)


def test_sma_matches_manual_average():
    prices = make_price_series([1, 2, 3, 4, 5])
    result = technical.sma(prices, window=3)
    assert result.iloc[2] == pytest.approx(2.0)  # avg(1,2,3)
    assert result.iloc[4] == pytest.approx(4.0)  # avg(3,4,5)
    assert result.iloc[:2].isna().all()


def test_ema_reacts_faster_than_sma_to_a_jump():
    prices = make_price_series([10] * 20 + [50])
    sma_val = technical.sma(prices, window=10).iloc[-1]
    ema_val = technical.ema(prices, span=10).iloc[-1]
    assert ema_val > sma_val


def test_rsi_is_100_when_all_gains():
    prices = make_price_series(list(range(1, 30)))  # strictly increasing
    result = technical.rsi(prices, window=14)
    assert result.iloc[-1] == pytest.approx(100.0)


def test_rsi_is_0_when_all_losses():
    prices = make_price_series(list(range(30, 1, -1)))  # strictly decreasing
    result = technical.rsi(prices, window=14)
    assert result.iloc[-1] == pytest.approx(0.0)


def test_macd_histogram_is_difference_of_macd_and_signal():
    prices = make_price_series([10 + i * 0.5 for i in range(60)])
    result = technical.macd(prices)
    diff = result["macd"] - result["signal"]
    pd.testing.assert_series_equal(result["histogram"], diff, check_names=False)
