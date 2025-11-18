from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time as dt_time
from typing import Literal
import pandas as pd
import numpy as np

from .base import BaseStrategy, Signal
from arbitrix.core.utils.indicators import atr


@dataclass
class BreakoutConfig:
    symbol: str = field(
        default="",
        metadata={"group": "strategy", "description": "Simbolo di trading (es. EURUSD, IBUS500).", "optimizable": True},
    )
    timeframe: str = field(
        default="M5",
        metadata={"group": "strategy", "description": "Timeframe di esecuzione (es. M5, M15, H1, ...).", "optimizable": True},
    )
    breakout_window_min: int = field(
        default=30,
        metadata={"group": "strategy", "description": "Durata della finestra di breakout in minuti.", "optimizable": True},
    )
    session_open_hhmm: str = field(
        default="15:30",
        metadata={"group": "strategy", "description": "Orario di apertura della sessione in formato HH:MM.", "optimizable": True},
    )
    atr_period: int = field(
        default=14,
        metadata={"group": "strategy", "description": "Periodo utilizzato per il calcolo dell’ATR.", "optimizable": True},
    )
    atr_min_points: float = field(
        default=0.0,
        metadata={"group": "strategy", "description": "Valore minimo dell’ATR richiesto per consentire l’ingresso.", "optimizable": True},
    )
    stop_atr_mult: float = field(
        default=1.5,
        metadata={"group": "strategy", "description": "Moltiplicatore ATR per la distanza dello stop loss.", "optimizable": True},
    )
    take_atr_mult: float = field(
        default=3.0,
        metadata={"group": "strategy", "description": "Moltiplicatore ATR per la distanza del take profit.", "optimizable": True},
    )
    allow_short: bool = field(
        default=True,
        metadata={"group": "strategy", "description": "Se abilitato, consente anche operazioni short.", "optimizable": True},
    )
    session_timezone: str = field(
        default="Europe/Rome",
        metadata={"group": "strategy", "description": "Timezone di riferimento per l’orario di apertura sessione.", "optimizable": True},
    )
    # NEW: how bar timestamps are labeled in your data
    bar_label: Literal["end", "start"] = field(
        default="end",
        metadata={"group": "data", "description": "Se il timestamp della barra rappresenta l'inizio o la fine del periodo."},
    )


def _parse_timeframe_to_minutes(tf: str) -> int:
    tf = tf.strip().upper()
    if tf.startswith("M"):
        return int(tf[1:])
    if tf.startswith("H"):
        return int(tf[1:]) * 60
    if tf in ("D", "D1"):
        return 1440
    if tf.startswith("D"):
        return int(tf[1:]) * 1440
    raise ValueError(f"Unsupported timeframe: {tf}")


class BreakoutIndexStrategy(BaseStrategy):
    def __init__(self, cfg: BreakoutConfig):
        self.name = "breakout_index"
        self.symbol = cfg.symbol
        self.timeframe = cfg.timeframe
        self.cfg = cfg

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Expects df with tz-aware or tz-naive (UTC) index and columns: ['open','high','low','close'].
        Creates:
            - atr
            - session_open_ts (UTC)
            - in_open_range (bool)
            - or_high, or_low (Open Range for the day, filled on all rows of that local day)
        """
        if df.empty:
            return df

        df = df.copy()

        # --- Ensure tz-aware UTC index
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")

        # --- Indicators
        df["atr"] = atr(df, self.cfg.atr_period)

        # --- Build per-row session_open_ts in UTC using session timezone
        local_idx = df.index.tz_convert(self.cfg.session_timezone)
        # midnight (local) for each row
        local_midnight = local_idx.normalize()

        # session open time (delta)
        hh, mm = map(int, self.cfg.session_open_hhmm.split(":"))
        open_delta = pd.to_timedelta(hh, unit="h") + pd.to_timedelta(mm, unit="m")

        # session open (local tz) for each row's day, then convert to UTC
        session_open_local = local_midnight + open_delta
        session_open_utc = session_open_local.tz_convert("UTC")
        df["session_open_ts"] = session_open_utc

        # --- Timeframe → bar interval
        tf_minutes = _parse_timeframe_to_minutes(self.timeframe)
        bar_span = pd.to_timedelta(tf_minutes, unit="m")

        if self.cfg.bar_label == "end":
            bar_end = df.index
            bar_start = bar_end - bar_span
        else:  # "start"
            bar_start = df.index
            bar_end = bar_start + bar_span

        # --- Open-range window membership by interval overlap
        window = pd.to_timedelta(self.cfg.breakout_window_min, unit="m")
        win_start = session_open_utc
        win_end = session_open_utc + window

        # Overlap if (bar_start < win_end) and (bar_end > win_start)
        df["in_open_range"] = (bar_start < win_end) & (bar_end > win_start)

        # --- Compute OR high/low per local 'trading day'
        # Use the local day id to avoid UTC-crossing issues
        local_day = local_midnight.date  # ndarray of date objects aligned with index
        day_series = pd.Series(local_day, index=df.index, name="local_day")
        df["local_day"] = day_series

        df["or_high"] = np.nan
        df["or_low"] = np.nan

        for day, sub in df.groupby("local_day", sort=False):
            win_mask = sub["in_open_range"]
            if not win_mask.any():
                continue
            orh = sub.loc[win_mask, "high"].max()
            orl = sub.loc[win_mask, "low"].min()
            # assign the OR levels to all rows of that day
            df.loc[sub.index, "or_high"] = orh
            df.loc[sub.index, "or_low"] = orl

        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        # require properly computed fields
        req = ["atr", "or_high", "or_low", "local_day"]
        for c in req:
            if c not in df.columns:
                raise ValueError(f"Missing required column '{c}'. Did you call prepare()?")

        work = df.dropna(subset=["atr", "or_high", "or_low"]).copy()

        if self.cfg.atr_min_points > 0:
            work = work[work["atr"] >= self.cfg.atr_min_points]

        signals: list[Signal] = []
        # Avoid multiple same-side entries per local day
        last_side: dict[str, str] = {}

        for ts, row in work.iterrows():
            day_key = str(row["local_day"])
            px = float(row["close"])

            if px > row["or_high"] and last_side.get(day_key) != "long":
                signals.append(Signal(when=ts, action="buy", price=px, reason="breakout_up"))
                last_side[day_key] = "long"

            if self.cfg.allow_short and px < row["or_low"] and last_side.get(day_key) != "short":
                signals.append(Signal(when=ts, action="sell", price=px, reason="breakout_down"))
                last_side[day_key] = "short"

        return signals

    def stop_distance_points(self, row: pd.Series) -> float:
        return float(row["atr"] * self.cfg.stop_atr_mult)

    def take_distance_points(self, row: pd.Series) -> float:
        return float(row["atr"] * self.cfg.take_atr_mult)
