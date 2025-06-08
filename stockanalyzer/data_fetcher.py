"""Thin wrapper around yfinance so the rest of the codebase never imports it
directly -- makes it easy to mock out network calls in tests, and gives us
one place to add caching.
"""
from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)


class DataFetcher:
    def __init__(self):
        self._price_cache: dict[tuple, pd.DataFrame] = {}
        self._info_cache: dict[str, dict] = {}

    def get_price_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        key = (ticker, period, interval)
        if key in self._price_cache:
            return self._price_cache[key]

        log.info("Fetching %s price history (%s, %s)", ticker, period, interval)
        data = yf.Ticker(ticker).history(period=period, interval=interval)
        if data.empty:
            raise ValueError(f"No price data returned for '{ticker}' -- check the ticker symbol.")
        self._price_cache[key] = data
        return data

    def get_close_prices(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.Series:
        return self.get_price_history(ticker, period, interval)["Close"]

    def get_info(self, ticker: str) -> dict:
        if ticker not in self._info_cache:
            log.info("Fetching %s info", ticker)
            self._info_cache[ticker] = yf.Ticker(ticker).info
        return self._info_cache[ticker]

    def get_dividends(self, ticker: str) -> pd.Series:
        return yf.Ticker(ticker).dividends
