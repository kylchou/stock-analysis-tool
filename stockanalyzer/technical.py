"""Technical indicators: moving averages, RSI, MACD."""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma(prices: pd.Series, window: int) -> pd.Series:
    return prices.rolling(window=window).mean()


def ema(prices: pd.Series, span: int) -> pd.Series:
    return prices.ewm(span=span, adjust=False).mean()


def rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    # A run with zero losses (or zero everything) divides by zero here, which
    # is a real case for a strictly-increasing price series, not just bad
    # data -- handle it explicitly instead of letting numpy warn about it.
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = avg_gain / avg_loss

    result = 100 - (100 / (1 + rs))
    result = result.mask(avg_loss == 0, 100.0)  # no losses in the window -> maxed out
    result = result.mask((avg_gain == 0) & (avg_loss == 0), 50.0)  # no movement at all -> neutral
    return result


def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    fast_ema = ema(prices, fast)
    slow_ema = ema(prices, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return pd.DataFrame({"macd": macd_line, "signal": signal_line, "histogram": histogram})
