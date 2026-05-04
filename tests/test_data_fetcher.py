"""Tests for DataFetcher's caching behavior, using a mocked yfinance.Ticker
so these run with no network access.
"""
import pandas as pd
import pytest

from stockanalyzer.data_fetcher import DataFetcher


class FakeTicker:
    call_count = 0

    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, period, interval):
        FakeTicker.call_count += 1
        dates = pd.date_range("2024-01-01", periods=5, freq="D")
        return pd.DataFrame({"Close": [100, 101, 102, 103, 104]}, index=dates)

    @property
    def info(self):
        FakeTicker.call_count += 1
        return {"sector": "Technology"}

    @property
    def dividends(self):
        return pd.Series(dtype=float)


@pytest.fixture(autouse=True)
def reset_call_count():
    FakeTicker.call_count = 0
    yield


def test_get_price_history_caches_by_ticker_period_interval(monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)
    fetcher = DataFetcher()

    fetcher.get_price_history("AAPL", period="1y", interval="1d")
    fetcher.get_price_history("AAPL", period="1y", interval="1d")

    assert FakeTicker.call_count == 1  # second call should hit the cache


def test_get_price_history_different_params_not_cached_together(monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)
    fetcher = DataFetcher()

    fetcher.get_price_history("AAPL", period="1y", interval="1d")
    fetcher.get_price_history("AAPL", period="6mo", interval="1d")

    assert FakeTicker.call_count == 2


def test_get_close_prices_returns_close_column(monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)
    fetcher = DataFetcher()

    closes = fetcher.get_close_prices("AAPL")
    assert list(closes.values) == [100, 101, 102, 103, 104]


def test_get_info_caches_per_ticker(monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)
    fetcher = DataFetcher()

    fetcher.get_info("AAPL")
    fetcher.get_info("AAPL")

    assert FakeTicker.call_count == 1


def test_empty_price_history_raises_value_error(monkeypatch):
    class EmptyTicker(FakeTicker):
        def history(self, period, interval):
            return pd.DataFrame()

    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", EmptyTicker)
    fetcher = DataFetcher()

    with pytest.raises(ValueError):
        fetcher.get_price_history("BADTICKER")
