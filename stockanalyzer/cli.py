"""Command-line interface tying the metrics/dividends/risk modules together.

Examples:
    python main.py analyze AAPL
    python main.py analyze AAPL --benchmark SPY
    python main.py compare AAPL MSFT GOOGL
"""
from __future__ import annotations

import argparse
import logging

from stockanalyzer import dividends, metrics, monte_carlo, portfolio, risk, technical
from stockanalyzer.data_fetcher import DataFetcher

log = logging.getLogger(__name__)


def _analyze_one(fetcher: DataFetcher, ticker: str, benchmark: str | None, period: str) -> dict:
    prices = fetcher.get_close_prices(ticker, period=period)
    info = fetcher.get_info(ticker)
    divs = fetcher.get_dividends(ticker)

    vol = metrics.annualized_volatility(prices)
    ret = metrics.annualized_return(prices)
    sharpe = metrics.sharpe_ratio(prices)
    sortino = metrics.sortino_ratio(prices)
    mdd = metrics.max_drawdown(prices)

    result = {
        "ticker": ticker,
        "sector": info.get("sector", "n/a"),
        "industry": info.get("industry", "n/a"),
        "annualized_return": round(ret, 4) if ret == ret else None,
        "annualized_volatility": round(vol, 4) if vol == vol else None,
        "sharpe_ratio": round(sharpe, 3) if sharpe == sharpe else None,
        "sortino_ratio": round(sortino, 3) if sortino == sortino else None,
        "max_drawdown": round(mdd, 4) if mdd == mdd else None,
        "dividend_yield": None,
        "risk_score": None,
        "risk_label": None,
    }

    annual_div = dividends.trailing_annual_dividend(divs)
    current_price = float(prices.iloc[-1])
    div_yield = dividends.dividend_yield(annual_div, current_price)
    result["dividend_yield"] = round(div_yield, 4) if div_yield == div_yield else 0.0

    score = risk.risk_return_score(sharpe, vol, mdd)
    result["risk_score"] = score
    result["risk_label"] = risk.classify(score)

    if benchmark:
        benchmark_prices = fetcher.get_close_prices(benchmark, period=period)
        result["beta"] = round(metrics.beta(prices, benchmark_prices), 3)

    return result


def cmd_analyze(args: argparse.Namespace) -> int:
    fetcher = DataFetcher()
    result = _analyze_one(fetcher, args.ticker, args.benchmark, args.period)
    for key, value in result.items():
        print(f"{key}: {value}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    fetcher = DataFetcher()
    rows = [_analyze_one(fetcher, ticker, args.benchmark, args.period) for ticker in args.tickers]
    rows.sort(key=lambda r: r["risk_score"] or 0, reverse=True)

    for row in rows:
        print(f"{row['ticker']:>6}  score={row['risk_score']:>5}  {row['risk_label']}")
    return 0


def cmd_portfolio(args: argparse.Namespace) -> int:
    holdings = portfolio.load_holdings_csv(args.csv_path)
    fetcher = DataFetcher()

    current_prices = {ticker: float(fetcher.get_close_prices(ticker, period="5d").iloc[-1]) for ticker in holdings}
    value = portfolio.portfolio_value(holdings, current_prices)
    weights = portfolio.portfolio_weights(holdings, current_prices)

    print(f"Total portfolio value: ${value:,.2f}\n")
    for ticker, weight in sorted(weights.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {ticker:>6}  {weight * 100:5.1f}%  ({holdings[ticker]} shares @ ${current_prices[ticker]:.2f})")

    price_histories = {ticker: fetcher.get_close_prices(ticker, period=args.period) for ticker in holdings}
    corr = portfolio.correlation_matrix(price_histories)
    print("\nReturn correlation matrix:")
    print(corr.round(2))
    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    fetcher = DataFetcher()
    prices = fetcher.get_close_prices(args.ticker, period=args.period)
    mu = metrics.annualized_return(prices)
    sigma = metrics.annualized_volatility(prices)
    current_price = float(prices.iloc[-1])

    paths = monte_carlo.simulate_gbm(
        current_price, mu, sigma, days=args.days, simulations=args.simulations, seed=args.seed
    )
    summary = monte_carlo.summarize_simulation(paths)

    print(f"{args.ticker} Monte Carlo simulation ({args.simulations} runs, {args.days} trading days)")
    print(f"  current price:      ${current_price:.2f}")
    print(f"  estimated mu/sigma: {mu:.2%} / {sigma:.2%} (annualized, from trailing {args.period})")
    for key, value in summary.items():
        print(f"  {key:>17}: {value:.2f}" if key != "prob_above_start" else f"  {key:>17}: {value:.1%}")
    return 0


def cmd_technical(args: argparse.Namespace) -> int:
    fetcher = DataFetcher()
    prices = fetcher.get_close_prices(args.ticker, period=args.period)

    latest_rsi = technical.rsi(prices).iloc[-1]
    macd_df = technical.macd(prices)
    latest_macd = macd_df.iloc[-1]

    print(f"{args.ticker} technical snapshot")
    print(f"  SMA 20:  {technical.sma(prices, 20).iloc[-1]:.2f}")
    print(f"  SMA 50:  {technical.sma(prices, 50).iloc[-1]:.2f}")
    print(f"  RSI 14:  {latest_rsi:.1f}")
    print(f"  MACD:    {latest_macd['macd']:.3f}  signal: {latest_macd['signal']:.3f}  hist: {latest_macd['histogram']:.3f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate stocks by risk, return, and dividends.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a single ticker")
    analyze.add_argument("ticker")
    analyze.add_argument("--benchmark", default="SPY", help="Benchmark ticker for beta (default: SPY)")
    analyze.add_argument("--period", default="1y")
    analyze.set_defaults(func=cmd_analyze)

    compare = subparsers.add_parser("compare", help="Compare multiple tickers, ranked by risk score")
    compare.add_argument("tickers", nargs="+")
    compare.add_argument("--benchmark", default="SPY")
    compare.add_argument("--period", default="1y")
    compare.set_defaults(func=cmd_compare)

    port = subparsers.add_parser("portfolio", help="Analyze a portfolio from a ticker,shares CSV")
    port.add_argument("csv_path")
    port.add_argument("--period", default="1y")
    port.set_defaults(func=cmd_portfolio)

    sim = subparsers.add_parser("simulate", help="Monte Carlo simulate future prices")
    sim.add_argument("ticker")
    sim.add_argument("--period", default="2y", help="History window used to estimate drift/volatility")
    sim.add_argument("--days", type=int, default=252)
    sim.add_argument("--simulations", type=int, default=1000)
    sim.add_argument("--seed", type=int, default=None)
    sim.set_defaults(func=cmd_simulate)

    tech = subparsers.add_parser("technical", help="Show SMA/RSI/MACD snapshot for a ticker")
    tech.add_argument("ticker")
    tech.add_argument("--period", default="6mo")
    tech.set_defaults(func=cmd_technical)

    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
