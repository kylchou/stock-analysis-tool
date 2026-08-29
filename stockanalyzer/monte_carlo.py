"""Monte Carlo price simulation using Geometric Brownian Motion.

Simulates a bunch of possible future price paths given a drift (mu) and
volatility (sigma) estimated from historical returns, so you can see a
spread of plausible outcomes instead of a single point forecast.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from stockanalyzer import metrics


def simulate_gbm(
    current_price: float,
    mu: float,
    sigma: float,
    days: int = 252,
    simulations: int = 1000,
    seed: int | None = None,
) -> np.ndarray:
    """Returns an array of shape (days + 1, simulations) of simulated prices."""
    rng = np.random.default_rng(seed)
    dt = 1 / 252
    price_paths = np.zeros((days + 1, simulations))
    price_paths[0] = current_price

    for t in range(1, days + 1):
        z = rng.standard_normal(simulations)
        price_paths[t] = price_paths[t - 1] * np.exp(
            (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
        )

    return price_paths


def summarize_simulation(price_paths: np.ndarray) -> dict:
    final_prices = price_paths[-1]
    return {
        "mean": float(np.mean(final_prices)),
        "median": float(np.median(final_prices)),
        "p5": float(np.percentile(final_prices, 5)),
        "p95": float(np.percentile(final_prices, 95)),
        "prob_above_start": float(np.mean(final_prices > price_paths[0, 0])),
    }


def backtest(
    prices: pd.Series,
    horizon_days: int = 252,
    estimation_days: int | None = None,
    simulations: int = 1000,
    seed: int | None = None,
) -> dict:
    """Sanity check on how much to trust the simulation: picks a point
    `horizon_days` trading days before the end of `prices`, estimates
    mu/sigma from everything before that point (or just the trailing
    `estimation_days` of it, if given), simulates forward from there, and
    compares the simulated distribution against what the price actually
    did. If the real outcome keeps landing outside the simulated p5-p95
    band, that's a sign the drift/vol estimate isn't a great fit for this
    ticker -- not something the simulation itself can tell you.
    """
    if len(prices) <= horizon_days + 2:
        raise ValueError(
            f"Need more than {horizon_days} days of price history to backtest a "
            f"{horizon_days}-day horizon; got {len(prices)}."
        )

    split = len(prices) - horizon_days
    estimation_window = (
        prices.iloc[:split] if estimation_days is None else prices.iloc[max(0, split - estimation_days):split]
    )

    mu = metrics.annualized_return(estimation_window)
    sigma = metrics.annualized_volatility(estimation_window)
    start_price = float(estimation_window.iloc[-1])
    actual_end_price = float(prices.iloc[-1])

    paths = simulate_gbm(start_price, mu, sigma, days=horizon_days, simulations=simulations, seed=seed)
    summary = summarize_simulation(paths)

    final_prices = paths[-1]
    actual_percentile = float(np.mean(final_prices <= actual_end_price)) * 100

    return {
        "start_price": start_price,
        "actual_end_price": actual_end_price,
        "estimated_mu": mu,
        "estimated_sigma": sigma,
        **summary,
        "actual_percentile": actual_percentile,
        "within_p5_p95": bool(summary["p5"] <= actual_end_price <= summary["p95"]),
    }
