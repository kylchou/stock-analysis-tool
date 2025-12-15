import numpy as np
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
