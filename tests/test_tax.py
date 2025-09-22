from datetime import date

from stockanalyzer import tax


def test_is_long_term_boundary():
    purchase = date(2024, 1, 1)
    assert tax.is_long_term(purchase, date(2024, 6, 1)) is False
    assert tax.is_long_term(purchase, date(2025, 1, 2)) is True


def test_estimate_tax_short_term_uses_ordinary_bracket():
    result = tax.estimate_tax(
        gain=5000,
        taxable_income=40000,
        purchase_date=date(2024, 1, 1),
        sale_date=date(2024, 6, 1),
    )
    assert result["long_term"] is False
    assert result["marginal_rate"] == 0.12  # 45,000 falls in the 12% bracket
    assert result["estimated_tax"] == 600.0


def test_estimate_tax_long_term_uses_ltcg_bracket():
    result = tax.estimate_tax(
        gain=5000,
        taxable_income=45000,
        purchase_date=date(2023, 1, 1),
        sale_date=date(2024, 6, 1),
    )
    assert result["long_term"] is True
    assert result["marginal_rate"] == 0.15  # 45,000 falls in the 15% LTCG bracket
    assert result["estimated_tax"] == 750.0


def test_days_until_long_term():
    purchase = date(2024, 1, 1)
    as_of = date(2024, 1, 1)
    assert tax.days_until_long_term(purchase, as_of) == tax.SHORT_TERM_THRESHOLD_DAYS + 1


def test_compare_sell_now_vs_wait_shows_savings_when_long_term_is_cheaper():
    comparison = tax.compare_sell_now_vs_wait(
        gain=10000,
        taxable_income=40000,
        purchase_date=date(2024, 1, 1),
        as_of=date(2024, 6, 1),
    )
    assert comparison["sell_now"]["long_term"] is False
    assert comparison["sell_after_long_term"]["long_term"] is True
    assert comparison["estimated_savings"] > 0
