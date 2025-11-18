"""
Advanced Volatility Squeeze Breakout Strategy
Combines Bollinger Band Squeeze, Keltner Channel, and VCP concepts
for high-probability breakout trading with tight risk management.

COMPLEMENTARY to Volume-Weighted Momentum Strategy:
- VW-Momentum: trend-following, works in trending markets
- Volatility Squeeze: breakout/expansion, works after consolidation
- Together: full market cycle coverage
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from datetime import datetime
import pandas as pd
import numpy as np

from arbitrix.core.strategies.base import BaseStrategy, Signal
from arbitrix.core.utils.indicators import atr, ema, sma, bollinger


@dataclass
class VolatilitySqueezeConfig:
    """Configuration for Volatility Squeeze Breakout Strategy"""

    # Symbol and timeframe
    symbol: str = field(
        default="IBUS500",
        metadata={"group": "strategy", "description": "Trading symbol", "optimizable": True}
    )
    timeframe: str = field(
        default="H1",
        metadata={"group": "strategy", "description": "Timeframe for analysis", "optimizable": True}
    )

    # Bollinger Bands parameters
    bb_period: int = field(
        default=20,
        metadata={"group": "bollinger", "description": "Bollinger Bands period", "optimizable": True, "min": 15, "max": 25}
    )
    bb_std: float = field(
        default=2.0,
        metadata={"group": "bollinger", "description": "Bollinger Bands std dev", "optimizable": True, "min": 1.5, "max": 2.5}
    )

    # Keltner Channel parameters
    kc_period: int = field(
        default=20,
        metadata={"group": "keltner", "description": "Keltner Channel EMA period", "optimizable": True, "min": 15, "max": 25}
    )
    kc_atr_mult: float = field(
        default=1.5,
        metadata={"group": "keltner", "description": "Keltner Channel ATR multiplier", "optimizable": True, "min": 1.0, "max": 2.5}
    )

    # Squeeze detection
    squeeze_lookback: int = field(
        default=5,
        metadata={"group": "squeeze", "description": "Bars to confirm squeeze", "optimizable": True, "min": 3, "max": 10}
    )
    bandwidth_threshold: float = field(
        default=0.15,
        metadata={"group": "squeeze", "description": "BandWidth threshold for squeeze", "optimizable": True, "min": 0.10, "max": 0.25}
    )

    # Volatility Contraction Pattern (VCP)
    vcp_enable: bool = field(
        default=True,
        metadata={"group": "vcp", "description": "Enable VCP detection", "optimizable": True}
    )
    vcp_contractions: int = field(
        default=3,
        metadata={"group": "vcp", "description": "Min contractions for VCP", "optimizable": True, "min": 2, "max": 4}
    )
    vcp_lookback: int = field(
        default=20,
        metadata={"group": "vcp", "description": "Lookback for VCP detection", "optimizable": True, "min": 15, "max": 30}
    )

    # Breakout confirmation
    breakout_volume_mult: float = field(
        default=1.5,
        metadata={"group": "breakout", "description": "Volume multiplier for breakout", "optimizable": True, "min": 1.2, "max": 2.0}
    )
    breakout_close_pct: float = field(
        default=0.5,
        metadata={"group": "breakout", "description": "Min % close beyond band", "optimizable": True, "min": 0.3, "max": 0.8}
    )

    # Momentum confirmation (RSI)
    use_rsi_filter: bool = field(
        default=True,
        metadata={"group": "momentum", "description": "Use RSI for momentum filter", "optimizable": True}
    )
    rsi_period: int = field(
        default=14,
        metadata={"group": "momentum", "description": "RSI period", "optimizable": True, "min": 10, "max": 20}
    )
    rsi_neutral_low: float = field(
        default=40.0,
        metadata={"group": "momentum", "description": "RSI neutral zone low", "optimizable": True, "min": 30, "max": 45}
    )
    rsi_neutral_high: float = field(
        default=60.0,
        metadata={"group": "momentum", "description": "RSI neutral zone high", "optimizable": True, "min": 55, "max": 70}
    )

    # Trend alignment (optional)
    use_trend_filter: bool = field(
        default=False,
        metadata={"group": "trend", "description": "Require trend alignment", "optimizable": True}
    )
    trend_ema_period: int = field(
        default=50,
        metadata={"group": "trend", "description": "EMA period for trend", "optimizable": True, "min": 30, "max": 100}
    )

    # Risk management
    atr_period: int = field(
        default=14,
        metadata={"group": "risk", "description": "ATR period", "optimizable": True, "min": 10, "max": 20}
    )
    stop_atr_mult: float = field(
        default=2.0,
        metadata={"group": "risk", "description": "Stop loss ATR multiplier", "optimizable": True, "min": 1.5, "max": 3.0}
    )
    take_atr_mult: float = field(
        default=4.0,
        metadata={"group": "risk", "description": "Take profit ATR multiplier", "optimizable": True, "min": 3.0, "max": 6.0}
    )


class VolatilitySqueezeStrategy(BaseStrategy):
    """
    Volatility Squeeze Breakout Strategy combining:
    - Bollinger Band Squeeze for low volatility detection
    - Keltner Channel for squeeze confirmation
    - VCP (Volatility Contraction Pattern) for structure
    - Volume surge for breakout validation
    - RSI for momentum confirmation

    COMPLEMENTARY to Volume-Weighted Momentum:
    - Catches breakouts from consolidation
    - Works in range-bound to trending transitions
    - Lower frequency, higher R:R trades
    """

    def __init__(self, cfg: VolatilitySqueezeConfig):
        self.cfg = cfg
        self.symbol = cfg.symbol
        self.timeframe = cfg.timeframe
        self.name = "volatility_squeeze_breakout"

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators"""
        if df.empty or len(df) < max(self.cfg.bb_period, self.cfg.vcp_lookback):
            return df

        df = df.copy()

        # --- Bollinger Bands ---
        df['bb_middle'] = df['close'].rolling(window=self.cfg.bb_period).mean()
        std = df['close'].rolling(window=self.cfg.bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (std * self.cfg.bb_std)
        df['bb_lower'] = df['bb_middle'] - (std * self.cfg.bb_std)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

        # --- Keltner Channel ---
        df['kc_middle'] = ema(df['close'], self.cfg.kc_period)
        df['atr_ind'] = atr(df, self.cfg.kc_period)
        df['kc_upper'] = df['kc_middle'] + (df['atr_ind'] * self.cfg.kc_atr_mult)
        df['kc_lower'] = df['kc_middle'] - (df['atr_ind'] * self.cfg.kc_atr_mult)

        # --- Squeeze Detection ---
        # Squeeze = BB inside KC
        df['squeeze_on'] = (df['bb_lower'] > df['kc_lower']) & (df['bb_upper'] < df['kc_upper'])
        df['squeeze_off'] = ~df['squeeze_on']

        # BandWidth low threshold
        df['bandwidth_low'] = df['bb_width'] < self.cfg.bandwidth_threshold

        # Confirm squeeze for N bars
        df['squeeze_confirmed'] = (
            df['squeeze_on'].rolling(window=self.cfg.squeeze_lookback).sum() >= self.cfg.squeeze_lookback
        ) & df['bandwidth_low']

        # --- VCP Detection ---
        if self.cfg.vcp_enable:
            df['vcp_pattern'] = self._detect_vcp(df)
        else:
            df['vcp_pattern'] = False

        # --- Volume ---
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_surge'] = df['volume'] > (df['volume_ma'] * self.cfg.breakout_volume_mult)

        # --- RSI ---
        if self.cfg.use_rsi_filter:
            df['rsi'] = self._calculate_rsi(df['close'], self.cfg.rsi_period)
        else:
            df['rsi'] = 50.0

        # --- Trend Filter ---
        if self.cfg.use_trend_filter:
            df['trend_ema'] = ema(df['close'], self.cfg.trend_ema_period)
            df['trend_up'] = df['close'] > df['trend_ema']
            df['trend_down'] = df['close'] < df['trend_ema']
        else:
            df['trend_up'] = True
            df['trend_down'] = True

        # --- ATR for risk ---
        df['atr'] = atr(df, self.cfg.atr_period)

        return df.dropna()

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _detect_vcp(self, df: pd.DataFrame) -> pd.Series:
        """Detect Volatility Contraction Pattern"""
        vcp = pd.Series(False, index=df.index)

        lookback = self.cfg.vcp_lookback
        min_contractions = self.cfg.vcp_contractions

        for i in range(lookback, len(df)):
            # Look at recent price action
            recent_highs = df['high'].iloc[i-lookback:i+1]
            recent_lows = df['low'].iloc[i-lookback:i+1]
            recent_ranges = recent_highs - recent_lows

            # Check for progressively smaller ranges
            # Split lookback into segments
            segment_size = lookback // min_contractions
            if segment_size < 2:
                continue

            ranges = []
            for j in range(min_contractions):
                start = i - lookback + (j * segment_size)
                end = start + segment_size
                if end > i + 1:
                    end = i + 1
                segment_range = recent_ranges.iloc[start:end].mean()
                ranges.append(segment_range)

            # Check if ranges are decreasing
            is_contracting = all(ranges[k] > ranges[k+1] for k in range(len(ranges)-1))

            # Check if making higher lows
            segment_lows = []
            for j in range(min_contractions):
                start = i - lookback + (j * segment_size)
                end = start + segment_size
                if end > i + 1:
                    end = i + 1
                segment_low = recent_lows.iloc[start:end].min()
                segment_lows.append(segment_low)

            higher_lows = all(segment_lows[k] < segment_lows[k+1] for k in range(len(segment_lows)-1))

            if is_contracting and higher_lows:
                vcp.iloc[i] = True

        return vcp

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """Generate breakout signals after squeeze"""
        signals: List[Signal] = []

        in_squeeze = False
        squeeze_start_idx = None

        for i, (ts, row) in enumerate(df.iterrows()):
            if i < 1:
                continue

            prev_row = df.iloc[i-1]
            price = float(row['close'])

            # Track squeeze state
            if row['squeeze_confirmed'] and not in_squeeze:
                in_squeeze = True
                squeeze_start_idx = i

            # Look for breakout after squeeze
            if in_squeeze and row['squeeze_off']:

                # --- BULLISH BREAKOUT ---
                bullish_conditions = []

                # 1. Price breaks above upper BB
                bb_breakout_up = (
                    prev_row['close'] <= prev_row['bb_upper'] and
                    row['close'] > row['bb_upper']
                )
                bullish_conditions.append(bb_breakout_up)

                # 2. Close well into breakout zone
                if bb_breakout_up:
                    close_pct = (row['close'] - row['bb_upper']) / row['bb_upper']
                    strong_close = close_pct >= (self.cfg.breakout_close_pct / 100)
                    bullish_conditions.append(strong_close)
                else:
                    bullish_conditions.append(False)

                # 3. Volume surge
                bullish_conditions.append(row['volume_surge'])

                # 4. RSI confirmation (not overbought)
                if self.cfg.use_rsi_filter:
                    rsi_ok = row['rsi'] < 70 and row['rsi'] > self.cfg.rsi_neutral_low
                    bullish_conditions.append(rsi_ok)

                # 5. VCP pattern (if enabled)
                if self.cfg.vcp_enable:
                    bullish_conditions.append(row['vcp_pattern'] or prev_row['vcp_pattern'])

                # 6. Trend alignment (if enabled)
                if self.cfg.use_trend_filter:
                    bullish_conditions.append(row['trend_up'])

                # Generate BUY if conditions met
                if bb_breakout_up and sum(bullish_conditions[1:]) >= len(bullish_conditions[1:]) * 0.6:
                    reason_parts = ["squeeze_breakout_up"]
                    if row['volume_surge']:
                        reason_parts.append("vol_surge")
                    if self.cfg.vcp_enable and (row['vcp_pattern'] or prev_row['vcp_pattern']):
                        reason_parts.append("vcp")
                    if self.cfg.use_rsi_filter:
                        reason_parts.append(f"rsi_{row['rsi']:.0f}")

                    signals.append(Signal(
                        when=ts,
                        action="buy",
                        price=price,
                        reason="+".join(reason_parts)
                    ))

                    in_squeeze = False

                # --- BEARISH BREAKOUT ---
                bearish_conditions = []

                # 1. Price breaks below lower BB
                bb_breakout_down = (
                    prev_row['close'] >= prev_row['bb_lower'] and
                    row['close'] < row['bb_lower']
                )
                bearish_conditions.append(bb_breakout_down)

                # 2. Close well into breakout zone
                if bb_breakout_down:
                    close_pct = (row['bb_lower'] - row['close']) / row['bb_lower']
                    strong_close = close_pct >= (self.cfg.breakout_close_pct / 100)
                    bearish_conditions.append(strong_close)
                else:
                    bearish_conditions.append(False)

                # 3. Volume surge
                bearish_conditions.append(row['volume_surge'])

                # 4. RSI confirmation (not oversold)
                if self.cfg.use_rsi_filter:
                    rsi_ok = row['rsi'] > 30 and row['rsi'] < self.cfg.rsi_neutral_high
                    bearish_conditions.append(rsi_ok)

                # 5. VCP not required for bearish (different pattern)

                # 6. Trend alignment (if enabled)
                if self.cfg.use_trend_filter:
                    bearish_conditions.append(row['trend_down'])

                # Generate SELL if conditions met
                if bb_breakout_down and sum(bearish_conditions[1:]) >= len(bearish_conditions[1:]) * 0.6:
                    reason_parts = ["squeeze_breakout_down"]
                    if row['volume_surge']:
                        reason_parts.append("vol_surge")
                    if self.cfg.use_rsi_filter:
                        reason_parts.append(f"rsi_{row['rsi']:.0f}")

                    signals.append(Signal(
                        when=ts,
                        action="sell",
                        price=price,
                        reason="+".join(reason_parts)
                    ))

                    in_squeeze = False

        return signals

    def stop_distance_points(self, row: pd.Series) -> float:
        """Tight stop based on ATR or recent swing low"""
        atr_value = float(row.get('atr', 0.0))
        return max(atr_value, 1e-6) * self.cfg.stop_atr_mult

    def take_distance_points(self, row: pd.Series) -> float:
        """Wide target based on ATR for high R:R"""
        atr_value = float(row.get('atr', 0.0))
        return max(atr_value, 1e-6) * self.cfg.take_atr_mult

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
    ) -> None:
        """Hook for pre-processing"""
        return None
