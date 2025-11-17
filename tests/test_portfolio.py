import pandas as pd
import pytest

from stockanalyzer import portfolio


def test_portfolio_value_sums_holdings():
    holdings = {"AAPL": 10, "MSFT": 5}
    prices = {"AAPL": 200.0, "MSFT": 400.0}
    assert portfolio.portfolio_value(holdings, prices) == pytest.approx(4000.0)


def test_portfolio_weights_sum_to_one():
    holdings = {"AAPL": 10, "MSFT": 5}
    prices = {"AAPL": 200.0, "MSFT": 400.0}
    weights = portfolio.portfolio_weights(holdings, prices)
    assert sum(weights.values()) == pytest.approx(1.0)
    assert weights["AAPL"] == pytest.approx(2000 / 4000)


def test_portfolio_weights_zero_value_returns_zeros():
    holdings = {"AAPL": 0, "MSFT": 0}
    prices = {"AAPL": 200.0, "MSFT": 400.0}
    weights = portfolio.portfolio_weights(holdings, prices)
    assert weights == {"AAPL": 0.0, "MSFT": 0.0}


def test_correlation_matrix_perfectly_correlated_series():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    base = pd.Series(range(10), index=dates, dtype=float) + 100
    price_histories = {"A": base, "B": base * 2}  # B moves in lockstep with A
    corr = portfolio.correlation_matrix(price_histories)
    assert corr.loc["A", "B"] == pytest.approx(1.0, rel=1e-6)


def test_load_holdings_csv(tmp_path):
    csv_path = tmp_path / "holdings.csv"
    csv_path.write_text("ticker,shares\nAAPL,10\nMSFT,5\n")
    holdings = portfolio.load_holdings_csv(str(csv_path))
    assert holdings == {"AAPL": 10, "MSFT": 5}
