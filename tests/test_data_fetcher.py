"""Tests for DataFetcher's caching behavior, using a mocked yfinance.Ticker
so these run with no network access.
"""
import os
import time

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
    fetcher = DataFetcher(cache_dir=None)

    fetcher.get_price_history("AAPL", period="1y", interval="1d")
    fetcher.get_price_history("AAPL", period="1y", interval="1d")

    assert FakeTicker.call_count == 1  # second call should hit the cache


def test_get_price_history_different_params_not_cached_together(monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)
    fetcher = DataFetcher(cache_dir=None)

    fetcher.get_price_history("AAPL", period="1y", interval="1d")
    fetcher.get_price_history("AAPL", period="6mo", interval="1d")

    assert FakeTicker.call_count == 2


def test_get_close_prices_returns_close_column(monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)
    fetcher = DataFetcher(cache_dir=None)

    closes = fetcher.get_close_prices("AAPL")
    assert list(closes.values) == [100, 101, 102, 103, 104]


def test_get_info_caches_per_ticker(monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)
    fetcher = DataFetcher(cache_dir=None)

    fetcher.get_info("AAPL")
    fetcher.get_info("AAPL")

    assert FakeTicker.call_count == 1


def test_empty_price_history_raises_value_error(monkeypatch):
    class EmptyTicker(FakeTicker):
        def history(self, period, interval):
            return pd.DataFrame()

    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", EmptyTicker)
    fetcher = DataFetcher(cache_dir=None)

    with pytest.raises(ValueError):
        fetcher.get_price_history("BADTICKER")


# --- on-disk cache -----------------------------------------------------
# The in-memory dict above only helps within a single process. These cover
# the disk layer, which is what actually saves a refetch on the *next*
# `python main.py ...` invocation.


def test_disk_cache_survives_a_fresh_instance(tmp_path, monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)

    DataFetcher(cache_dir=tmp_path).get_price_history("AAPL", period="1y", interval="1d")
    assert FakeTicker.call_count == 1

    # A brand new instance -- like a new `python main.py` run -- should hit
    # the file written by the one above instead of calling yfinance again.
    second = DataFetcher(cache_dir=tmp_path)
    second.get_price_history("AAPL", period="1y", interval="1d")
    assert FakeTicker.call_count == 1


def test_disk_cache_ignores_expired_entries(tmp_path, monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)

    fetcher = DataFetcher(cache_dir=tmp_path, cache_ttl_seconds=1)
    fetcher.get_price_history("AAPL", period="1y", interval="1d")
    assert FakeTicker.call_count == 1

    cache_file = next(tmp_path.iterdir())
    stale_mtime = time.time() - 3600  # well past the 1-second TTL above
    os.utime(cache_file, (stale_mtime, stale_mtime))

    DataFetcher(cache_dir=tmp_path, cache_ttl_seconds=1).get_price_history(
        "AAPL", period="1y", interval="1d"
    )
    assert FakeTicker.call_count == 2  # stale, so it should have refetched


def test_disk_cache_none_disables_the_disk_layer(monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)

    fetcher = DataFetcher(cache_dir=None)
    fetcher.get_price_history("AAPL", period="1y", interval="1d")

    assert fetcher.cache_dir is None
    assert fetcher._disk_cache_path("price", "AAPL", "1y", "1d") is None


def test_get_info_uses_the_disk_cache_too(tmp_path, monkeypatch):
    monkeypatch.setattr("stockanalyzer.data_fetcher.yf.Ticker", FakeTicker)

    DataFetcher(cache_dir=tmp_path).get_info("AAPL")
    assert FakeTicker.call_count == 1

    DataFetcher(cache_dir=tmp_path).get_info("AAPL")
    assert FakeTicker.call_count == 1
