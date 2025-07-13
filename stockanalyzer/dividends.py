"""Dividend yield, growth rate, and payout ratio calculations."""
from __future__ import annotations

import pandas as pd


def dividend_yield(annual_dividend: float, current_price: float) -> float:
    if not current_price:
        return float("nan")
    return annual_dividend / current_price


def trailing_annual_dividend(dividends: pd.Series) -> float:
    """Sum of dividends paid in the trailing 365 days from the most recent payment."""
    if dividends.empty:
        return 0.0
    cutoff = dividends.index.max() - pd.Timedelta(days=365)
    return float(dividends[dividends.index >= cutoff].sum())


def dividend_growth_rate(dividends: pd.Series, years: int = 5) -> float:
    """CAGR of total dividends paid per calendar year, over the trailing `years` years."""
    if dividends.empty:
        return float("nan")
    yearly = dividends.groupby(dividends.index.year).sum()
    recent = yearly.tail(years)
    if len(recent) < 2 or recent.iloc[0] <= 0:
        return float("nan")
    n_periods = len(recent) - 1
    return float((recent.iloc[-1] / recent.iloc[0]) ** (1 / n_periods) - 1)


def payout_ratio(annual_dividend_per_share: float, eps: float) -> float:
    if not eps:
        return float("nan")
    return annual_dividend_per_share / eps
