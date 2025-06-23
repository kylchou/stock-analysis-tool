"""Core return/risk metrics computed from a price series. Pure functions over
pandas Series so they're easy to unit test with synthetic data -- no network
calls in here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def daily_returns(prices: pd.Series) -> pd.Series:
    return prices.pct_change().dropna()


def annualized_return(prices: pd.Series, trading_days: int = TRADING_DAYS_PER_YEAR) -> float:
    returns = daily_returns(prices)
    if returns.empty:
        return float("nan")
    mean_daily = returns.mean()
    return float((1 + mean_daily) ** trading_days - 1)


def annualized_volatility(prices: pd.Series, trading_days: int = TRADING_DAYS_PER_YEAR) -> float:
    returns = daily_returns(prices)
    if returns.empty:
        return float("nan")
    return float(returns.std() * np.sqrt(trading_days))


def sharpe_ratio(
    prices: pd.Series, risk_free_rate: float = 0.04, trading_days: int = TRADING_DAYS_PER_YEAR
) -> float:
    vol = annualized_volatility(prices, trading_days)
    if not vol:
        return float("nan")
    ret = annualized_return(prices, trading_days)
    return (ret - risk_free_rate) / vol


def sortino_ratio(
    prices: pd.Series, risk_free_rate: float = 0.04, trading_days: int = TRADING_DAYS_PER_YEAR
) -> float:
    returns = daily_returns(prices)
    downside = returns[returns < 0]
    downside_std = float(downside.std() * np.sqrt(trading_days)) if len(downside) else 0.0
    if not downside_std:
        return float("nan")
    ret = annualized_return(prices, trading_days)
    return (ret - risk_free_rate) / downside_std


def max_drawdown(prices: pd.Series) -> float:
    if prices.empty:
        return float("nan")
    running_max = prices.cummax()
    drawdown = (prices - running_max) / running_max
    return float(drawdown.min())


def beta(stock_prices: pd.Series, market_prices: pd.Series) -> float:
    stock_returns = daily_returns(stock_prices)
    market_returns = daily_returns(market_prices)
    aligned = pd.concat([stock_returns, market_returns], axis=1, join="inner")
    aligned.columns = ["stock", "market"]
    aligned = aligned.dropna()
    if len(aligned) < 2:
        return float("nan")
    market_variance = aligned["market"].var()
    if not market_variance:
        return float("nan")
    return float(aligned["stock"].cov(aligned["market"]) / market_variance)
