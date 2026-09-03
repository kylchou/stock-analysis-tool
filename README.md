# Stock Analysis Tool

Me and my dad kept pulling up like 4 different sites to check a stock's
volatility, dividend history, sector, whatever, before deciding to actually
buy or sell anything -- so we started building this to just do it all in
one place.

## What it does

- pulls price history, dividends, and sector/industry info (via yfinance)
- volatility, Sharpe ratio, Sortino ratio, max drawdown, beta vs a
  benchmark like SPY
- dividend yield, multi-year growth rate, payout ratio
- a rough short-term vs. long-term capital gains estimate -- **not tax
  advice**, just a quick "is it worth waiting" gut check
- SMA / EMA / RSI / MACD if you're into the technical side
- portfolio mode: point it at a `ticker,shares` csv and it'll tell you
  total value, per-holding weight, and how correlated everything is
- Monte Carlo simulation so you get a spread of possible future prices
  instead of one guess
- can export a report as csv/html, or save charts as png

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py analyze AAPL --benchmark SPY
python main.py compare AAPL MSFT GOOGL --report out/compare.html
python main.py portfolio examples/sample_portfolio.csv
python main.py simulate AAPL --days 252 --simulations 2000
python main.py technical AAPL
```

## How it's organized

Every calculation module (`metrics.py`, `dividends.py`, `tax.py`,
`technical.py`, etc.) just takes a `pandas.Series` and never touches the
network. `data_fetcher.py` is the only file that actually calls yfinance,
which is what makes everything else easy to unit test without mocking an
API every time.

## Disclaimer

Educational project, not financial or tax advice. `tax.py` especially is a
rough estimate using simplified brackets, not something to file with.

MIT licensed, see [LICENSE](LICENSE).
