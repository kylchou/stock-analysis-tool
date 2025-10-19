"""Command-line interface tying the metrics/dividends/risk modules together.

Examples:
    python main.py analyze AAPL
    python main.py analyze AAPL --benchmark SPY
    python main.py compare AAPL MSFT GOOGL
"""
from __future__ import annotations

import argparse
import logging

from stockanalyzer import dividends, metrics, risk, technical
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
