"""Monte Carlo price simulation using Geometric Brownian Motion.

Simulates a bunch of possible future price paths given a drift (mu) and
volatility (sigma) estimated from historical returns, so you can see a
spread of plausible outcomes instead of a single point forecast.
"""
from __future__ import annotations

import numpy as np


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
