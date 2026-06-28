# Stock Analysis Tool

A Python tool my dad and I started building together to evaluate stocks
across volatility, dividends, sector, tax implications, and risk-adjusted
return -- basically everything we found ourselves manually pulling up on
different sites before deciding whether to buy or sell something.

## Features

- **Risk/return metrics** -- annualized return & volatility, Sharpe ratio,
  Sortino ratio, max drawdown, beta vs. a benchmark
- **Dividend analysis** -- trailing yield, multi-year dividend growth rate
  (CAGR), payout ratio
- **Capital gains tax estimator** -- rough short-term vs. long-term tax
  comparison so you can see if it's worth waiting past the 1-year mark
  before selling
- **Technical indicators** -- SMA, EMA, RSI, MACD
- **Portfolio mode** -- load a `ticker,shares` CSV and get total value,
  per-holding weights, and a return correlation matrix
- **Monte Carlo simulation** -- project a spread of future prices using
  Geometric Brownian Motion seeded from a stock's own historical
  drift/volatility
- **Reports** -- dump any analysis to CSV or a self-contained HTML table
- **Charts** -- price + moving averages, drawdown, and a correlation heatmap
  (all headless, saved as PNGs)
- **One risk/return score (0-100)** that blends Sharpe, volatility, and
  drawdown so you can quickly rank a watchlist

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Single ticker
python main.py analyze AAPL --benchmark SPY

# Compare several tickers, ranked by risk/return score
python main.py compare AAPL MSFT GOOGL NVDA --report out/compare.html

# Portfolio from a CSV of ticker,shares
python main.py portfolio examples/sample_portfolio.csv

# Monte Carlo price simulation
python main.py simulate AAPL --days 252 --simulations 2000

# Moving averages / RSI / MACD snapshot
python main.py technical AAPL
```

## Project layout

```
stockanalyzer/
  data_fetcher.py   # yfinance wrapper + caching
  metrics.py        # return, volatility, Sharpe/Sortino, drawdown, beta
  dividends.py      # yield, growth rate (CAGR), payout ratio
  tax.py            # short vs. long-term capital gains estimator
  risk.py           # blends metrics into a single 0-100 score
  technical.py      # SMA, EMA, RSI, MACD
  portfolio.py      # portfolio value/weights, correlation matrix
  monte_carlo.py    # GBM price simulation
  report.py         # CSV / HTML report writers
  visualize.py      # matplotlib charts (headless, saved as PNG)
  cli.py            # argparse entry point
tests/              # unit tests over synthetic price series (no network)
examples/
  sample_portfolio.csv
main.py
```

## Why the module split

Every metric/indicator is a pure function over a `pandas.Series` -- none of
them import `yfinance` directly. `data_fetcher.py` is the only module that
talks to the network, which is what makes the rest of this testable without
mocking an API for every test. (`data_fetcher.py` itself is tested with a
mocked `yf.Ticker`, so even the caching logic runs offline.)

## Disclaimer

Educational project. Nothing here is financial or tax advice -- especially
`tax.py`, which uses simplified brackets and taxes the entire gain at one
marginal rate instead of doing it bracket-by-bracket. Talk to an actual
advisor before making real decisions with real money.

## License

MIT, see [LICENSE](LICENSE).
