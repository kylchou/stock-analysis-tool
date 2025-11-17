"""Portfolio-level aggregation: value, weights, and cross-holding correlation."""
from __future__ import annotations

import pandas as pd


def combine_price_histories(price_histories: dict[str, pd.Series]) -> pd.DataFrame:
    df = pd.DataFrame(price_histories)
    return df.dropna(how="all")


def correlation_matrix(price_histories: dict[str, pd.Series]) -> pd.DataFrame:
    df = combine_price_histories(price_histories)
    returns = df.pct_change().dropna(how="all")
    return returns.corr()


def portfolio_value(holdings: dict[str, float], current_prices: dict[str, float]) -> float:
    return sum(shares * current_prices[ticker] for ticker, shares in holdings.items())


def portfolio_weights(holdings: dict[str, float], current_prices: dict[str, float]) -> dict[str, float]:
    total = portfolio_value(holdings, current_prices)
    if not total:
        return {ticker: 0.0 for ticker in holdings}
    return {
        ticker: (shares * current_prices[ticker]) / total
        for ticker, shares in holdings.items()
    }


def load_holdings_csv(path: str) -> dict[str, float]:
    """Reads a CSV with columns 'ticker,shares' into a {ticker: shares} dict."""
    df = pd.read_csv(path)
    return dict(zip(df["ticker"], df["shares"]))
