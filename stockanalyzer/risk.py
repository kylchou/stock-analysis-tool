"""Blend several metrics into a single risk/return score for quick ranking
across a watchlist. Not scientific -- just a consistent way to sort tickers.
"""
from __future__ import annotations


def risk_return_score(sharpe: float, volatility: float, max_dd: float) -> float:
    """Returns a 0-100 score. Higher Sharpe pushes it up; higher volatility
    and deeper drawdowns pull it down.
    """
    if sharpe != sharpe:  # NaN check without importing math/numpy just for this
        sharpe = 0.0

    sharpe_component = max(min(sharpe, 3.0), -3.0) * (50 / 3)  # maps [-3, 3] -> [-50, 50]
    vol_penalty = min(abs(volatility), 1.0) * 25
    dd_penalty = min(abs(max_dd), 1.0) * 25

    score = 50 + sharpe_component - vol_penalty - dd_penalty
    return round(max(0.0, min(100.0, score)), 1)


def classify(score: float) -> str:
    if score >= 70:
        return "Attractive risk/return"
    if score >= 45:
        return "Moderate"
    return "Weak risk/return"
