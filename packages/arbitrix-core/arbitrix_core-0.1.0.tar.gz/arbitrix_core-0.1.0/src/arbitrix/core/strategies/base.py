from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Literal, Optional
import pandas as pd

SignalAction = Literal["buy", "sell", "exit"]


@dataclass
class Signal:
    when: pd.Timestamp
    action: SignalAction
    price: float
    reason: str = ""

    def is_entry(self) -> bool:
        return self.action in ("buy", "sell")


class BaseStrategy:
    name: str
    symbol: str | None
    timeframe: str

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:  # pragma: no cover - to override
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:  # pragma: no cover - to override
        return []

    def stop_distance_points(self, row: pd.Series) -> float:  # pragma: no cover - to override
        return 0.0

    def take_distance_points(self, row: pd.Series) -> float:
        return 0.0

    @classmethod
    def prepare_task(
        cls,
        *,
        provider: Any,
        config: Any,
        task: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        as_of: Optional[datetime] = None,
        optimization_start: Optional[datetime] = None,
        strategy: Optional["BaseStrategy"] = None,
        strategy_config: Any = None,
        context: Optional[Dict[str, Any]] = None,
        **_: Any,
    ) -> None:  # pragma: no cover - default no-op
        """Hook executed before running backtests or optimizations."""
        return None
