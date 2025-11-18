from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd

from .base import BaseStrategy, Signal
from arbitrix.core.utils.indicators import atr, sma
import arbitrix.core.costs as costs


@dataclass
class CarryConfig:
    symbols: list[str]
    timeframe: str = "D1"
    risk_per_pair: float = 0.003
    ma_period: int = 50
    stop_atr_mult: float = 2.0
    take_atr_mult: float = 3.0
    static_swap_points: Optional[Dict[str, Dict[str, float]]] = None
    risk_off_filter: Optional[Dict[str, float]] = None


class CarryTradeStrategy(BaseStrategy):
    def __init__(self, cfg: CarryConfig):
        self.name = "carry_trade"
        self.symbol = None
        self.timeframe = cfg.timeframe
        self.cfg = cfg

    def prepare_one(self, symbol: str, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df["atr"] = atr(df, 14)
        df["ma"] = sma(df["close"], self.cfg.ma_period)
        override = (self.cfg.static_swap_points or {}).get(symbol)
        df["swap_long_points"] = costs.swap_points(symbol, "long", override)
        df["swap_short_points"] = costs.swap_points(symbol, "short", override)
        return df

    def generate_signals_multi(self, dfs: Dict[str, pd.DataFrame]) -> Dict[str, list[Signal]]:
        out: Dict[str, list[Signal]] = {}
        for symbol, df in dfs.items():
            dfp = df.dropna(subset=["ma", "atr"]).copy()
            sigs: list[Signal] = []
            for ts, row in dfp.iterrows():
                if self._is_risk_off(ts, dfs):
                    continue
                prefer_long = row["close"] > row["ma"]
                if row["swap_long_points"] > 0 and prefer_long:
                    sigs.append(Signal(when=ts, action="buy", price=float(row["close"]), reason="carry_positive_swap"))
                elif row["swap_short_points"] > 0 and not prefer_long:
                    sigs.append(Signal(when=ts, action="sell", price=float(row["close"]), reason="carry_positive_swap"))
            out[symbol] = sigs
        return out

    def _is_risk_off(self, ts: pd.Timestamp, dfs: Dict[str, pd.DataFrame]) -> bool:
        cfg = self.cfg.risk_off_filter or {}
        if cfg.get("type") != "vol_proxy":
            return False
        proxy_symbol = cfg.get("proxy_symbol")
        if proxy_symbol not in dfs:
            return False
        atr_period = int(cfg.get("atr_period", 14))
        threshold = float(cfg.get("atr_threshold_points", float("inf")))
        proxy_df = dfs[proxy_symbol].copy()
        if "atr_proxy" not in proxy_df.columns:
            proxy_df["atr_proxy"] = atr(proxy_df, atr_period)
        valid = proxy_df.loc[:ts]
        if valid.empty:
            return False
        return bool(valid.iloc[-1]["atr_proxy"] >= threshold)

    def stop_distance_points(self, row: pd.Series) -> float:
        return float(row["atr"] * self.cfg.stop_atr_mult)

    def take_distance_points(self, row: pd.Series) -> float:
        return float(row["atr"] * self.cfg.take_atr_mult)
