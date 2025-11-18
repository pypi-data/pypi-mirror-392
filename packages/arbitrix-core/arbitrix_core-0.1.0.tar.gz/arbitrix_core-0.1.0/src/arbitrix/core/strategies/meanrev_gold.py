from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from .base import BaseStrategy, Signal
from arbitrix.core.utils.indicators import atr, rsi


@dataclass
class MeanRevGoldConfig:
    symbol: str
    timeframe: str
    rsi_period: int = 2
    rsi_overbought: int = 70
    rsi_oversold: int = 30
    atr_period: int = 14
    vol_filter_atr_max: float = 2.0
    stop_atr_mult: float = 1.2
    take_atr_mult: float = 1.8
    allow_short: bool = True


class MeanRevGoldStrategy(BaseStrategy):
    def __init__(self, cfg: MeanRevGoldConfig):
        self.name = "meanrev_gold"
        self.symbol = cfg.symbol
        self.timeframe = cfg.timeframe
        self.cfg = cfg

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df["atr"] = atr(df, self.cfg.atr_period)
        df["rsi"] = rsi(df["close"], self.cfg.rsi_period)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        df = df.dropna(subset=["atr", "rsi"]).copy()
        signals: list[Signal] = []
        for ts, row in df.iterrows():
            if row["atr"] > self.cfg.vol_filter_atr_max:
                continue
            if row["rsi"] <= self.cfg.rsi_oversold:
                signals.append(Signal(when=ts, action="buy", price=float(row["close"]), reason="rsi_oversold"))
            if self.cfg.allow_short and row["rsi"] >= self.cfg.rsi_overbought:
                signals.append(Signal(when=ts, action="sell", price=float(row["close"]), reason="rsi_overbought"))
        return signals

    def stop_distance_points(self, row: pd.Series) -> float:
        return float(row["atr"] * self.cfg.stop_atr_mult)

    def take_distance_points(self, row: pd.Series) -> float:
        return float(row["atr"] * self.cfg.take_atr_mult)
