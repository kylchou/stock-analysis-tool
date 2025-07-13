import pandas as pd
import pytest

from stockanalyzer import dividends


def test_dividend_yield_basic():
    assert dividends.dividend_yield(annual_dividend=2.0, current_price=100.0) == pytest.approx(0.02)


def test_dividend_yield_nan_for_zero_price():
    result = dividends.dividend_yield(2.0, 0.0)
    assert result != result  # NaN is the only float that isn't equal to itself


def test_trailing_annual_dividend_sums_last_year():
    dates = pd.to_datetime(["2023-01-01", "2023-06-01", "2024-01-01", "2024-06-01"])
    series = pd.Series([0.5, 0.5, 0.6, 0.6], index=dates)
    total = dividends.trailing_annual_dividend(series)
    # Only payments within 365 days of the last payment (2024-06-01) should count.
    assert total == pytest.approx(1.2)


def test_trailing_annual_dividend_empty_series():
    assert dividends.trailing_annual_dividend(pd.Series(dtype=float)) == 0.0


def test_dividend_growth_rate_cagr():
    yearly_dates = pd.to_datetime(["2020-06-01", "2021-06-01", "2022-06-01", "2023-06-01"])
    series = pd.Series([1.00, 1.10, 1.21, 1.331], index=yearly_dates)  # exactly 10%/yr
    rate = dividends.dividend_growth_rate(series, years=4)
    assert rate == pytest.approx(0.10, rel=1e-3)


def test_payout_ratio():
    assert dividends.payout_ratio(annual_dividend_per_share=1.5, eps=3.0) == pytest.approx(0.5)
