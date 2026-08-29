import numpy as np
import pandas as pd
import pytest

from stockanalyzer import monte_carlo


def test_simulate_gbm_shape():
    paths = monte_carlo.simulate_gbm(100.0, mu=0.08, sigma=0.2, days=50, simulations=200, seed=42)
    assert paths.shape == (51, 200)
    assert np.all(paths[0] == 100.0)


def test_simulate_gbm_is_reproducible_with_seed():
    a = monte_carlo.simulate_gbm(100.0, 0.08, 0.2, days=30, simulations=100, seed=7)
    b = monte_carlo.simulate_gbm(100.0, 0.08, 0.2, days=30, simulations=100, seed=7)
    np.testing.assert_array_equal(a, b)


def test_zero_volatility_gives_deterministic_growth():
    paths = monte_carlo.simulate_gbm(100.0, mu=0.0, sigma=0.0, days=252, simulations=5, seed=1)
    # With zero drift and zero vol, price should stay flat.
    assert np.allclose(paths[-1], 100.0)


def test_summarize_simulation_keys_and_ordering():
    paths = monte_carlo.simulate_gbm(100.0, 0.05, 0.15, days=100, simulations=500, seed=3)
    summary = monte_carlo.summarize_simulation(paths)
    assert set(summary) == {"mean", "median", "p5", "p95", "prob_above_start"}
    assert summary["p5"] <= summary["median"] <= summary["p95"]
    assert 0.0 <= summary["prob_above_start"] <= 1.0


def _random_walk_prices(n: int, drift: float = 0.0005, vol: float = 0.01, seed: int = 0) -> pd.Series:
    dates = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    daily_returns = rng.normal(drift, vol, size=n - 1)
    prices = 100 * np.concatenate([[1.0], np.cumprod(1 + daily_returns)])
    return pd.Series(prices, index=dates)


def test_backtest_raises_when_not_enough_history():
    prices = pd.Series(np.linspace(100, 110, 50))
    with pytest.raises(ValueError):
        monte_carlo.backtest(prices, horizon_days=252)


def test_backtest_returns_expected_keys_and_ranges():
    prices = _random_walk_prices(800)
    result = monte_carlo.backtest(prices, horizon_days=100, simulations=300, seed=1)

    assert set(result) == {
        "start_price",
        "actual_end_price",
        "estimated_mu",
        "estimated_sigma",
        "mean",
        "median",
        "p5",
        "p95",
        "prob_above_start",
        "actual_percentile",
        "within_p5_p95",
    }
    assert result["p5"] <= result["median"] <= result["p95"]
    assert 0.0 <= result["actual_percentile"] <= 100.0
    assert isinstance(result["within_p5_p95"], bool)


def test_backtest_estimation_days_narrows_the_window():
    # Flat for the first stretch, then a clean upward trend -- a short
    # trailing window right before the split sees only the trend, so its
    # estimated drift should come out well above the full-history estimate,
    # which gets diluted by all the flat history before it.
    flat = np.full(400, 100.0)
    trending = 100 * (1.002 ** np.arange(1, 200))
    dates = pd.date_range("2020-01-01", periods=len(flat) + len(trending), freq="B")
    prices = pd.Series(np.concatenate([flat, trending]), index=dates)

    horizon = 50
    full_window = monte_carlo.backtest(prices, horizon_days=horizon, simulations=100, seed=2)
    short_window = monte_carlo.backtest(
        prices, horizon_days=horizon, estimation_days=30, simulations=100, seed=2
    )

    assert short_window["estimated_mu"] > full_window["estimated_mu"]
    # Both should still be estimating from the same point (same start price).
    assert short_window["start_price"] == full_window["start_price"]
