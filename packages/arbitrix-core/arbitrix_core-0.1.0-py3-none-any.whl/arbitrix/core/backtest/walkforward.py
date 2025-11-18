from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from .engine import Backtester, BTResult
from arbitrix.core.strategies.base import BaseStrategy


@dataclass
class WalkForwardConfig:
    train_bars: int
    test_bars: int
    step: Optional[int] = None


@dataclass
class WalkForwardBlock:
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    train_result: BTResult
    test_result: BTResult


class WalkForwardAnalyzer:
    def __init__(self, backtester: Backtester, risk_perc: float, initial_equity: float):
        self.backtester = backtester
        self.risk_perc = risk_perc
        self.initial_equity = initial_equity

    def run(self, df: pd.DataFrame, strategy: BaseStrategy, cfg: WalkForwardConfig) -> List[WalkForwardBlock]:
        blocks: List[WalkForwardBlock] = []
        step = cfg.step or cfg.test_bars
        total = len(df)
        start_idx = 0
        while True:
            train_end = start_idx + cfg.train_bars
            test_end = train_end + cfg.test_bars
            if test_end > total:
                break
            train_df = df.iloc[start_idx:train_end]
            test_df = df.iloc[train_end:test_end]
            train_res = self.backtester.run_single(train_df, strategy, self.risk_perc, self.initial_equity)
            test_res = self.backtester.run_single(test_df, strategy, self.risk_perc, self.initial_equity)
            blocks.append(
                WalkForwardBlock(
                    train_start=train_df.index[0],
                    train_end=train_df.index[-1],
                    test_start=test_df.index[0],
                    test_end=test_df.index[-1],
                    train_result=train_res,
                    test_result=test_res,
                )
            )
            start_idx += step
            if start_idx + cfg.train_bars + cfg.test_bars > total:
                break
        return blocks
