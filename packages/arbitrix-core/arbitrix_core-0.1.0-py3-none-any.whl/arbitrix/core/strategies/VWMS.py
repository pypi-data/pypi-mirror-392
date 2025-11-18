"""
Advanced US500 Volume-Weighted Momentum Strategy
Combines Volume-Weighted MACD, Money Flow Index, and Volume Profile concepts
for a robust trend-following approach with leading signals.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from datetime import datetime
import pandas as pd
import numpy as np

from arbitrix.core.strategies.base import BaseStrategy, Signal
from arbitrix.core.utils.indicators import atr, ema, sma


@dataclass
class VolumeWeightedMomentumConfig:
    """Configuration for Volume-Weighted Momentum Strategy"""

    # Symbol and timeframe
    symbol: str = field(
        default="IBUS500",
        metadata={"group": "strategy", "description": "Trading symbol (e.g., IBUS500)", "optimizable": True}
    )
    timeframe: str = field(
        default="H1",
        metadata={"group": "strategy", "description": "Timeframe for analysis", "optimizable": True}
    )

    # Volume-Weighted MACD parameters
    vwmacd_fast_period: int = field(
        default=12,
        metadata={"group": "vwmacd", "description": "Fast VWMA period for MACD", "optimizable": True, "min": 8, "max": 16}
    )
    vwmacd_slow_period: int = field(
        default=26,
        metadata={"group": "vwmacd", "description": "Slow VWMA period for MACD", "optimizable": True, "min": 20, "max": 35}
    )
    vwmacd_signal_period: int = field(
        default=9,
        metadata={"group": "vwmacd", "description": "Signal line period", "optimizable": True, "min": 7, "max": 12}
    )

    # Money Flow Index parameters
    mfi_period: int = field(
        default=14,
        metadata={"group": "mfi", "description": "MFI calculation period", "optimizable": True, "min": 10, "max": 20}
    )
    mfi_overbought: float = field(
        default=80.0,
        metadata={"group": "mfi", "description": "MFI overbought threshold", "optimizable": True, "min": 75, "max": 85}
    )
    mfi_oversold: float = field(
        default=20.0,
        metadata={"group": "mfi", "description": "MFI oversold threshold", "optimizable": True, "min": 15, "max": 25}
    )

    # Chaikin Money Flow parameters
    cmf_period: int = field(
        default=21,
        metadata={"group": "cmf", "description": "CMF calculation period", "optimizable": True, "min": 15, "max": 25}
    )
    cmf_threshold: float = field(
        default=0.05,
        metadata={"group": "cmf", "description": "CMF confirmation threshold", "optimizable": True, "min": 0.0, "max": 0.15}
    )

    # Volume Profile approximation (using volume SMA)
    volume_ma_period: int = field(
        default=20,
        metadata={"group": "volume", "description": "Volume moving average period", "optimizable": True, "min": 15, "max": 30}
    )
    volume_surge_multiplier: float = field(
        default=1.5,
        metadata={"group": "volume", "description": "Volume surge threshold multiplier", "optimizable": True, "min": 1.2, "max": 2.0}
    )

    # Trend filter
    trend_ema_fast: int = field(
        default=50,
        metadata={"group": "trend", "description": "Fast trend EMA", "optimizable": True, "min": 30, "max": 60}
    )
    trend_ema_slow: int = field(
        default=200,
        metadata={"group": "trend", "description": "Slow trend EMA", "optimizable": True, "min": 150, "max": 250}
    )

    # Risk management
    atr_period: int = field(
        default=14,
        metadata={"group": "risk", "description": "ATR period for stops/targets", "optimizable": True, "min": 10, "max": 20}
    )
    stop_atr_mult: float = field(
        default=2.0,
        metadata={"group": "risk", "description": "Stop loss ATR multiplier", "optimizable": True, "min": 1.5, "max": 3.0}
    )
    take_atr_mult: float = field(
        default=3.0,
        metadata={"group": "risk", "description": "Take profit ATR multiplier", "optimizable": True, "min": 2.0, "max": 5.0}
    )

    # Signal filters
    require_volume_confirmation: bool = field(
        default=True,
        metadata={"group": "filters", "description": "Require volume surge for entry", "optimizable": True}
    )
    require_trend_alignment: bool = field(
        default=True,
        metadata={"group": "filters", "description": "Only trade with major trend", "optimizable": True}
    )
    use_mfi_divergence: bool = field(
        default=True,
        metadata={"group": "filters", "description": "Enable MFI divergence detection", "optimizable": True}
    )


class VolumeWeightedMomentumStrategy(BaseStrategy):
    """
    Advanced US500 Strategy combining:
    - Volume-Weighted MACD for momentum with volume context
    - Money Flow Index for overbought/oversold and divergences
    - Chaikin Money Flow for accumulation/distribution confirmation
    - Volume surge detection for breakout validation
    - Multi-timeframe trend alignment
    """

    def __init__(self, cfg: VolumeWeightedMomentumConfig):
        self.cfg = cfg
        self.symbol = cfg.symbol
        self.timeframe = cfg.timeframe
        self.name = "volume_weighted_momentum"

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators"""
        if df.empty or len(df) < max(self.cfg.vwmacd_slow_period, self.cfg.trend_ema_slow):
            return df

        df = df.copy()

        # --- Volume-Weighted MACD ---
        df['vwma_fast'] = self._volume_weighted_ma(df['close'], df['volume'], self.cfg.vwmacd_fast_period)
        df['vwma_slow'] = self._volume_weighted_ma(df['close'], df['volume'], self.cfg.vwmacd_slow_period)
        df['vwmacd'] = df['vwma_fast'] - df['vwma_slow']
        df['vwmacd_signal'] = df['vwmacd'].ewm(span=self.cfg.vwmacd_signal_period, adjust=False).mean()
        df['vwmacd_hist'] = df['vwmacd'] - df['vwmacd_signal']

        # --- Money Flow Index ---
        df['mfi'] = self._calculate_mfi(df, self.cfg.mfi_period)

        # --- Chaikin Money Flow ---
        df['cmf'] = self._calculate_cmf(df, self.cfg.cmf_period)

        # --- Volume indicators ---
        df['volume_ma'] = df['volume'].rolling(window=self.cfg.volume_ma_period).mean()
        df['volume_surge'] = df['volume'] > (df['volume_ma'] * self.cfg.volume_surge_multiplier)

        # --- Trend filters ---
        df['ema_fast'] = ema(df['close'], self.cfg.trend_ema_fast)
        df['ema_slow'] = ema(df['close'], self.cfg.trend_ema_slow)
        df['trend'] = np.where(df['ema_fast'] > df['ema_slow'], 1, -1)

        # --- ATR for risk management ---
        df['atr'] = atr(df, self.cfg.atr_period)

        # --- MFI Divergence detection ---
        if self.cfg.use_mfi_divergence:
            df['mfi_bullish_div'] = self._detect_bullish_divergence(df['close'], df['mfi'])
            df['mfi_bearish_div'] = self._detect_bearish_divergence(df['close'], df['mfi'])
        else:
            df['mfi_bullish_div'] = False
            df['mfi_bearish_div'] = False

        return df.dropna()

    def _volume_weighted_ma(self, price: pd.Series, volume: pd.Series, period: int) -> pd.Series:
        """Calculate Volume-Weighted Moving Average"""
        pv = price * volume
        return pv.rolling(window=period).sum() / volume.rolling(window=period).sum()

    def _calculate_mfi(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Money Flow Index"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']

        # Positive and negative money flow
        positive_flow = pd.Series(0.0, index=df.index)
        negative_flow = pd.Series(0.0, index=df.index)

        price_diff = typical_price.diff()
        positive_flow[price_diff > 0] = money_flow[price_diff > 0]
        negative_flow[price_diff < 0] = money_flow[price_diff < 0]

        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()

        mfi = 100 - (100 / (1 + positive_mf / (negative_mf + 1e-10)))
        return mfi

    def _calculate_cmf(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Chaikin Money Flow"""
        mf_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + 1e-10)
        mf_volume = mf_multiplier * df['volume']

        cmf = mf_volume.rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
        return cmf

    def _detect_bullish_divergence(self, price: pd.Series, indicator: pd.Series, lookback: int = 14) -> pd.Series:
        """Detect bullish divergence: price makes lower low, indicator makes higher low"""
        divergence = pd.Series(False, index=price.index)

        for i in range(lookback, len(price)):
            recent_price = price.iloc[i-lookback:i+1]
            recent_indicator = indicator.iloc[i-lookback:i+1]

            price_min_idx = recent_price.idxmin()
            ind_min_idx = recent_indicator.idxmin()

            # Check if price made new low but indicator didn't
            if (price.iloc[i] < recent_price.iloc[:-1].min() and 
                indicator.iloc[i] > recent_indicator.iloc[:-1].min()):
                divergence.iloc[i] = True

        return divergence

    def _detect_bearish_divergence(self, price: pd.Series, indicator: pd.Series, lookback: int = 14) -> pd.Series:
        """Detect bearish divergence: price makes higher high, indicator makes lower high"""
        divergence = pd.Series(False, index=price.index)

        for i in range(lookback, len(price)):
            recent_price = price.iloc[i-lookback:i+1]
            recent_indicator = indicator.iloc[i-lookback:i+1]

            # Check if price made new high but indicator didn't
            if (price.iloc[i] > recent_price.iloc[:-1].max() and 
                indicator.iloc[i] < recent_indicator.iloc[:-1].max()):
                divergence.iloc[i] = True

        return divergence

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """Generate trading signals based on multiple volume-weighted conditions"""
        signals: List[Signal] = []

        for i, (ts, row) in enumerate(df.iterrows()):
            if i < 1:  # Need previous row for signal detection
                continue

            prev_row = df.iloc[i-1]
            price = float(row['close'])

            # --- BUY CONDITIONS ---
            buy_conditions = []

            # 1. VWMACD crossover (primary signal)
            vwmacd_cross_up = (prev_row['vwmacd'] <= prev_row['vwmacd_signal'] and 
                              row['vwmacd'] > row['vwmacd_signal'])
            buy_conditions.append(vwmacd_cross_up)

            # 2. MFI oversold or bullish divergence
            mfi_bullish = row['mfi'] < self.cfg.mfi_oversold or row['mfi_bullish_div']
            buy_conditions.append(mfi_bullish)

            # 3. CMF positive (accumulation)
            cmf_positive = row['cmf'] > self.cfg.cmf_threshold
            buy_conditions.append(cmf_positive)

            # 4. Volume confirmation (if required)
            if self.cfg.require_volume_confirmation:
                buy_conditions.append(row['volume_surge'])

            # 5. Trend alignment (if required)
            if self.cfg.require_trend_alignment:
                buy_conditions.append(row['trend'] > 0)

            # Generate BUY signal if primary + majority of conditions met
            if vwmacd_cross_up and sum(buy_conditions[1:]) >= len(buy_conditions[1:]) * 0.6:
                reason_parts = []
                if vwmacd_cross_up:
                    reason_parts.append("vwmacd_cross_up")
                if mfi_bullish:
                    reason_parts.append(f"mfi_bullish({row['mfi']:.1f})")
                if cmf_positive:
                    reason_parts.append(f"cmf_pos({row['cmf']:.3f})")
                if row['volume_surge']:
                    reason_parts.append("vol_surge")

                signals.append(Signal(
                    when=ts,
                    action="buy",
                    price=price,
                    reason="+".join(reason_parts)
                ))

            # --- SELL CONDITIONS ---
            sell_conditions = []

            # 1. VWMACD crossover down (primary signal)
            vwmacd_cross_down = (prev_row['vwmacd'] >= prev_row['vwmacd_signal'] and 
                                row['vwmacd'] < row['vwmacd_signal'])
            sell_conditions.append(vwmacd_cross_down)

            # 2. MFI overbought or bearish divergence
            mfi_bearish = row['mfi'] > self.cfg.mfi_overbought or row['mfi_bearish_div']
            sell_conditions.append(mfi_bearish)

            # 3. CMF negative (distribution)
            cmf_negative = row['cmf'] < -self.cfg.cmf_threshold
            sell_conditions.append(cmf_negative)

            # 4. Volume confirmation (if required)
            if self.cfg.require_volume_confirmation:
                sell_conditions.append(row['volume_surge'])

            # 5. Trend alignment (if required)
            if self.cfg.require_trend_alignment:
                sell_conditions.append(row['trend'] < 0)

            # Generate SELL signal if primary + majority of conditions met
            if vwmacd_cross_down and sum(sell_conditions[1:]) >= len(sell_conditions[1:]) * 0.6:
                reason_parts = []
                if vwmacd_cross_down:
                    reason_parts.append("vwmacd_cross_down")
                if mfi_bearish:
                    reason_parts.append(f"mfi_bearish({row['mfi']:.1f})")
                if cmf_negative:
                    reason_parts.append(f"cmf_neg({row['cmf']:.3f})")
                if row['volume_surge']:
                    reason_parts.append("vol_surge")

                signals.append(Signal(
                    when=ts,
                    action="sell",
                    price=price,
                    reason="+".join(reason_parts)
                ))

        return signals

    def stop_distance_points(self, row: pd.Series) -> float:
        """Dynamic stop loss based on ATR"""
        atr_value = float(row.get('atr', 0.0))
        return max(atr_value, 1e-6) * self.cfg.stop_atr_mult

    def take_distance_points(self, row: pd.Series) -> float:
        """Dynamic take profit based on ATR"""
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
        """Hook for pre-processing before backtests/optimizations"""
        # Can be used to download additional data, calculate seasonal factors, etc.
        return None