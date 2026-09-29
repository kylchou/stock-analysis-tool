# stock-analysis-tool

My dad and I got tired of checking four different sites every time we wanted
to look at a stock before buying or selling, so we made this. You give it a
ticker and it pulls everything we usually care about into one place.

## What's in it

- price history, dividends, sector/industry (from yfinance)
- return, volatility, Sharpe, Sortino, max drawdown, beta vs SPY (or whatever)
- dividend yield, growth rate, payout ratio
- a 0-100 risk/return score so you can sort a bunch of tickers quickly
- SMA, EMA, RSI, MACD
- portfolio mode: give it a csv of `ticker,shares` and it shows value,
  weights, and how correlated your holdings are
- Monte Carlo sim of future prices, plus a backtest to see how well the sim
  would've done in the past
- a rough capital gains tax estimate (short vs long term)
- csv/html reports and png charts

## Setup

```bash
pip install -r requirements.txt
```

## Using it

```bash
python main.py analyze AAPL
python main.py compare AAPL MSFT GOOGL --report out/compare.html
python main.py portfolio examples/sample_portfolio.csv
python main.py simulate AAPL --days 252 --simulations 2000
python main.py backtest AAPL --horizon-days 126
python main.py technical AAPL
```

Data gets cached in `.stockanalyzer_cache/` for a day so reruns don't hit
yfinance again.

## Tests

```bash
python -m pytest
```

They don't need internet, yfinance is mocked.

## Heads up

This is a side project, not financial advice. The tax part especially is a
ballpark number, don't file anything based on it.

MIT license, see [LICENSE](LICENSE).
