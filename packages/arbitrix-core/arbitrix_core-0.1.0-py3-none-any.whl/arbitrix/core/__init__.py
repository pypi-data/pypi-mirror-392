"""Core (open-source) surface of Arbitrix.

This subpackage intentionally contains only the components that are safe to
publish independently: the backtesting engine, strategy base classes, cost
models, shared utilities, and lightweight type definitions.
"""

from .backtest.engine import Backtester, BTConfig, BTResult, Trade
from .strategies.base import BaseStrategy, Signal
from .types import InstrumentConfig

__all__ = [
    "Backtester",
    "BTConfig",
    "BTResult",
    "Trade",
    "BaseStrategy",
    "Signal",
    "InstrumentConfig",
]
