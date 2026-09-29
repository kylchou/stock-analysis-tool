from __future__ import annotations


def risk_return_score(sharpe: float, volatility: float, max_dd: float) -> float:
    if sharpe != sharpe:  # NaN
        sharpe = 0.0

    sharpe_component = max(min(sharpe, 3.0), -3.0) * (50 / 3)
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
