from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class InstrumentConfig:
    """Lightweight metadata describing a tradable instrument.

    Extracted into the core namespace so that importing backtesting helpers
    does not implicitly require the heavier configuration loader machinery.
    """

    ib_symbol: str
    security_type: str = "CFD"
    exchange: str = "SMART"
    currency: str = "USD"
    local_symbol: Optional[str] = None
    primary_exchange: Optional[str] = None
    multiplier: Optional[float] = None
    expiry: Optional[str] = None
    what_to_show: str = "TRADES"
    point_value: Optional[float] = None
    tick_size: Optional[float] = None
    commission_rate: Optional[float] = None
    commission_min: Optional[float] = None
