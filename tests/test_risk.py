import pytest

from stockanalyzer import risk


def test_high_sharpe_low_vol_scores_high():
    score = risk.risk_return_score(sharpe=2.0, volatility=0.1, max_dd=-0.05)
    assert score >= 70
    assert risk.classify(score) == "Attractive risk/return"


def test_negative_sharpe_high_vol_scores_low():
    score = risk.risk_return_score(sharpe=-1.5, volatility=0.6, max_dd=-0.4)
    assert score <= 45
    assert risk.classify(score) == "Weak risk/return"


def test_score_is_clamped_to_0_100():
    assert 0.0 <= risk.risk_return_score(sharpe=100, volatility=0, max_dd=0) <= 100.0
    assert 0.0 <= risk.risk_return_score(sharpe=-100, volatility=5, max_dd=-5) <= 100.0


def test_nan_sharpe_treated_as_neutral():
    score = risk.risk_return_score(sharpe=float("nan"), volatility=0.2, max_dd=-0.1)
    assert score == pytest.approx(50 - 0.2 * 25 - 0.1 * 25)
