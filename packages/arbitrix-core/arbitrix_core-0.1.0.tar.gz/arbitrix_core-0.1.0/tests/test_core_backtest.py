from __future__ import annotations

import math
import pandas as pd

from arbitrix.core.backtest import BTConfig, Backtester
from arbitrix.core.strategies.base import BaseStrategy, Signal
from arbitrix.core import costs


class DummyStrategy(BaseStrategy):
    name = "dummy-ma"
    symbol = "EURUSD"
    timeframe = "1H"

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        frame = df.copy()
        frame["fast"] = frame["close"].rolling(3).mean()
        frame["slow"] = frame["close"].rolling(6).mean()
        return frame.dropna()

    def generate_signals(self, df: pd.DataFrame):
        signals: list[Signal] = []
        for idx in range(1, len(df)):
            fast_prev = df["fast"].iloc[idx - 1]
            slow_prev = df["slow"].iloc[idx - 1]
            fast_now = df["fast"].iloc[idx]
            slow_now = df["slow"].iloc[idx]
            when = df.index[idx]
            price = float(df["close"].iloc[idx])
            if fast_prev <= slow_prev and fast_now > slow_now:
                signals.append(Signal(action="buy", when=when, price=price, reason="bullish cross"))
            elif fast_prev >= slow_prev and fast_now < slow_now:
                signals.append(Signal(action="sell", when=when, price=price, reason="bearish cross"))
        return signals

    def stop_distance_points(self, row: pd.Series) -> float:
        return 0.0005

    def take_distance_points(self, row: pd.Series) -> float:
        return 0.001


def _sample_frame() -> pd.DataFrame:
    dates = pd.date_range("2022-01-01", periods=48, freq="H", tz="UTC")
    prices = pd.Series(
        [
            1.10 + (i * 0.0003) + 0.001 * math.sin(i / 2.0)
            for i in range(len(dates))
        ],
        index=dates,
    )
    data = pd.DataFrame(
        {
            "open": prices.shift(1).fillna(prices.iloc[0]),
            "high": prices + 0.0007,
            "low": prices - 0.0007,
            "close": prices,
            "volume": 1000,
        },
        index=dates,
    )
    return data


def test_dummy_strategy_generates_trades():
    costs.configure(point_overrides={"EURUSD": 1.0}, allow_provider_lookups=False)
    strategy = DummyStrategy()
    bt = Backtester(BTConfig())
    result = bt.run_single(
        _sample_frame(),
        strategy=strategy,
        risk_perc=0.01,
        initial_equity=100_000,
    )
    assert result.trades, "expected at least one trade"
    metrics = result.metrics
    assert metrics.get("TradeCount", 0) >= 1
    assert "Sharpe" in metrics
    assert "MaxDD" in metrics
