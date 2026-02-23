"""Matplotlib charts. Every function saves a PNG instead of calling plt.show()
so this works fine headless (CI, cron jobs, etc.).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # noqa: E402
import matplotlib.pyplot as plt
import pandas as pd


def plot_price_with_moving_averages(
    prices: pd.Series, sma_short: pd.Series, sma_long: pd.Series, ticker: str, out_path: str
) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(prices.index, prices.values, label="Close", linewidth=1.2)
    ax.plot(sma_short.index, sma_short.values, label=f"SMA {len(sma_short)}d", linewidth=1)
    ax.plot(sma_long.index, sma_long.values, label=f"SMA {len(sma_long)}d", linewidth=1)
    ax.set_title(f"{ticker} price with moving averages")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_drawdown(prices: pd.Series, ticker: str, out_path: str) -> None:
    running_max = prices.cummax()
    drawdown = (prices - running_max) / running_max

    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.fill_between(drawdown.index, drawdown.values * 100, 0, color="crimson", alpha=0.5)
    ax.set_title(f"{ticker} drawdown")
    ax.set_ylabel("Drawdown (%)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_correlation_heatmap(correlation: pd.DataFrame, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(correlation.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(correlation.columns)))
    ax.set_yticks(range(len(correlation.index)))
    ax.set_xticklabels(correlation.columns, rotation=45, ha="right")
    ax.set_yticklabels(correlation.index)
    for i in range(len(correlation.index)):
        for j in range(len(correlation.columns)):
            ax.text(j, i, f"{correlation.values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Correlation")
    ax.set_title("Return correlation")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
