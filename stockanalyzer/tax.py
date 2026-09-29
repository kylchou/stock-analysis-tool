# rough estimate only, not tax advice. 2024 single-filer brackets, whole gain
# taxed at the marginal rate
from __future__ import annotations

from datetime import date

SHORT_TERM_THRESHOLD_DAYS = 365

# (lower, upper, rate)
ORDINARY_BRACKETS: list[tuple[float, float, float]] = [
    (0, 11_600, 0.10),
    (11_600, 47_150, 0.12),
    (47_150, 100_525, 0.22),
    (100_525, 191_950, 0.24),
    (191_950, 243_725, 0.32),
    (243_725, 609_350, 0.35),
    (609_350, float("inf"), 0.37),
]

LTCG_BRACKETS: list[tuple[float, float, float]] = [
    (0, 47_025, 0.0),
    (47_025, 518_900, 0.15),
    (518_900, float("inf"), 0.20),
]


def is_long_term(purchase_date: date, sale_date: date) -> bool:
    return (sale_date - purchase_date).days > SHORT_TERM_THRESHOLD_DAYS


def _marginal_rate(taxable_income: float, brackets: list[tuple[float, float, float]]) -> float:
    for lower, upper, rate in brackets:
        if lower <= taxable_income < upper:
            return rate
    return brackets[-1][2]


def estimate_tax(
    gain: float,
    taxable_income: float,
    purchase_date: date,
    sale_date: date,
) -> dict:
    long_term = is_long_term(purchase_date, sale_date)
    income_with_gain = taxable_income + max(gain, 0)
    brackets = LTCG_BRACKETS if long_term else ORDINARY_BRACKETS
    rate = _marginal_rate(income_with_gain, brackets)
    return {
        "long_term": long_term,
        "holding_period_days": (sale_date - purchase_date).days,
        "marginal_rate": rate,
        "estimated_tax": round(max(gain, 0) * rate, 2),
    }


def compare_sell_now_vs_wait(
    gain: float,
    taxable_income: float,
    purchase_date: date,
    as_of: date,
) -> dict:
    sell_now = estimate_tax(gain, taxable_income, purchase_date, as_of)
    days_to_wait = days_until_long_term(purchase_date, as_of)
    wait_date = date.fromordinal(as_of.toordinal() + days_to_wait)
    sell_later = estimate_tax(gain, taxable_income, purchase_date, wait_date)
    return {
        "sell_now": sell_now,
        "sell_after_long_term": sell_later,
        "days_to_wait": days_to_wait,
        "estimated_savings": round(sell_now["estimated_tax"] - sell_later["estimated_tax"], 2),
    }


def days_until_long_term(purchase_date: date, as_of: date) -> int:
    held = (as_of - purchase_date).days
    return max(SHORT_TERM_THRESHOLD_DAYS - held + 1, 0)
