# Arbitrix Core

`arbitrix-core` is the open-source subset of Arbitrix that contains the
backtesting engine, strategy abstractions, technical indicators, and cost
models required to run local research workflows.

## Installation

```bash
python -m pip install arbitrix-core
# optional extras
python -m pip install 'arbitrix-core[ib]'
```

## Quick start

```python
from arbitrix.core.backtest import Backtester, BTConfig
from arbitrix.core.strategies.base import BaseStrategy, Signal

cfg = BTConfig()
bt = Backtester(cfg)
```

See the main repository's documentation under `docs/` for end-to-end guides,
including CSV backtest and moving-average crossover examples that are mirrored
under `open-core/examples/`.
