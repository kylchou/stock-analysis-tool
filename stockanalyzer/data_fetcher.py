"""Thin wrapper around yfinance so the rest of the codebase never imports it
directly -- makes it easy to mock out network calls in tests, and gives us
one place to add caching.
"""
from __future__ import annotations

import hashlib
import logging
import pickle
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)

# Price history for a given ticker/period/interval doesn't change until the
# next trading day closes, and yfinance rate-limits if you lean on it too
# hard -- so a same-day rerun of `compare`/`portfolio` (easy to do, e.g. you
# and someone else both poking at it the same afternoon) shouldn't have to
# refetch everything from scratch. 24h is generous on purpose: worst case
# you're a day stale, which doesn't matter for anything here.
DEFAULT_CACHE_DIR = Path(".stockanalyzer_cache")
DEFAULT_CACHE_TTL_SECONDS = 24 * 60 * 60


class DataFetcher:
    def __init__(
        self,
        cache_dir: str | Path | None = DEFAULT_CACHE_DIR,
        cache_ttl_seconds: float = DEFAULT_CACHE_TTL_SECONDS,
    ):
        self._price_cache: dict[tuple, pd.DataFrame] = {}
        self._info_cache: dict[str, dict] = {}
        # cache_dir=None disables the on-disk layer entirely (tests use
        # this so pytest never leaves cache files scattered around) --
        # the in-memory dicts above still dedupe repeat calls within a
        # single run either way.
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.cache_ttl_seconds = cache_ttl_seconds
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _disk_cache_path(self, *key_parts: str) -> Path | None:
        if not self.cache_dir:
            return None
        digest = hashlib.sha1("|".join(str(p) for p in key_parts).encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.pkl"

    def _read_disk_cache(self, path: Path | None):
        if not path or not path.exists():
            return None
        age_seconds = time.time() - path.stat().st_mtime
        if age_seconds > self.cache_ttl_seconds:
            return None
        try:
            with path.open("rb") as f:
                return pickle.load(f)
        except Exception:
            log.warning("Disk cache file %s was unreadable, refetching", path)
            return None

    def _write_disk_cache(self, path: Path | None, data) -> None:
        if not path:
            return
        try:
            with path.open("wb") as f:
                pickle.dump(data, f)
        except OSError:
            log.warning("Couldn't write disk cache to %s", path)

    def get_price_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        key = (ticker, period, interval)
        if key in self._price_cache:
            return self._price_cache[key]

        disk_path = self._disk_cache_path("price", ticker, period, interval)
        cached = self._read_disk_cache(disk_path)
        if cached is not None:
            self._price_cache[key] = cached
            return cached

        log.info("Fetching %s price history (%s, %s)", ticker, period, interval)
        data = yf.Ticker(ticker).history(period=period, interval=interval)
        if data.empty:
            raise ValueError(f"No price data returned for '{ticker}' -- check the ticker symbol.")
        self._price_cache[key] = data
        self._write_disk_cache(disk_path, data)
        return data

    def get_close_prices(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.Series:
        return self.get_price_history(ticker, period, interval)["Close"]

    def get_info(self, ticker: str) -> dict:
        if ticker in self._info_cache:
            return self._info_cache[ticker]

        disk_path = self._disk_cache_path("info", ticker)
        cached = self._read_disk_cache(disk_path)
        if cached is not None:
            self._info_cache[ticker] = cached
            return cached

        log.info("Fetching %s info", ticker)
        info = yf.Ticker(ticker).info
        self._info_cache[ticker] = info
        self._write_disk_cache(disk_path, info)
        return info

    def get_dividends(self, ticker: str) -> pd.Series:
        return yf.Ticker(ticker).dividends
