from __future__ import annotations

from typing import Optional

from .. import base

__all__ = [
    "configure",
    "commission_one_side",
    "commission_round_turn",
    "spread_cost",
    "slippage_cost",
    "swap_points",
    "swap_cost_per_day",
]


def configure(context: Optional[dict] = None) -> None:  # pragma: no cover - simple hook
    """Default model does not need extra configuration."""
    return None


def commission_one_side(symbol: str, price: float, volume_lot: float) -> float:
    notional = base.trade_notional(symbol, price, volume_lot)
    commission = base.commission_from_notional(
        symbol=symbol,
        price=price,
        volume_lot=volume_lot,
        notional=notional,
    )
    return commission


def commission_round_turn(symbol: str, price: float, volume_lot: float) -> float:
    return commission_one_side(symbol, price, volume_lot) * 2.0


def spread_cost(symbol: str, spread_points: float, volume_lot: float) -> float:
    pv = base.get_point_value(symbol)
    return float(spread_points) * pv * float(volume_lot)


def slippage_cost(symbol: str, slippage_points: float, volume_lot: float) -> float:
    pv = base.get_point_value(symbol)
    return float(slippage_points) * pv * float(volume_lot)


def swap_points(symbol: str, direction: str, static_override: Optional[dict] = None) -> float:
    override = base.swap_points_static(symbol, direction, static_override)
    if override is not None:
        return override
    return base.swap_points_from_cache(symbol, direction)


def swap_cost_per_day(symbol: str, volume_lot: float, direction: str, static_override: Optional[dict] = None) -> float:
    points = swap_points(symbol, direction, static_override)
    pv = base.get_point_value(symbol)
    return points * pv * float(volume_lot)
