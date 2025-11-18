from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

from arbitrix.core.strategies.base import BaseStrategy, Signal
import arbitrix.core.costs as costs
from arbitrix.core.types import InstrumentConfig


@dataclass
class Trade:
    symbol: str
    side: str
    entry_time: pd.Timestamp
    entry_price: float
    exit_time: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    volume: float = 0.0
    stop_points: float = 0.0
    take_points: float = 0.0
    pnl: float = 0.0
    commission_paid: float = 0.0
    spread_cost: float = 0.0
    slippage_cost: float = 0.0
    swap_pnl: float = 0.0
    gross_pnl: float = 0.0
    net_pnl: float = 0.0
    notes: Dict[str, float] = field(default_factory=dict)
    _last_swap_day: Optional[pd.Timestamp] = None


@dataclass
class BTConfig:
    commission_per_lot: float = 3.0
    default_slippage_points: float = 0.5
    slippage_atr_multiplier: float = 0.0
    apply_spread_cost: bool = True
    apply_swap_cost: bool = True


@dataclass
class BTResult:
    trades: List[Trade]
    daily_equity: pd.Series
    gross_equity: pd.Series
    metrics: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


class Backtester:
    def __init__(self, cfg: BTConfig, instruments: Optional[Dict[str, InstrumentConfig]] = None):
        self.cfg = cfg
        self.instruments = instruments or {}
        costs.set_commission_per_lot(cfg.commission_per_lot)

    def run_single(
        self,
        df: pd.DataFrame,
        strategy: BaseStrategy,
        risk_perc: float,
        initial_equity: float,
        swap_override: Optional[dict] = None,
        *,
        cancel_callback: Optional[Callable[[], None]] = None,
        early_stop_conditions: Optional[Dict[str, Any]] = None,
    ) -> BTResult:
        def _maybe_cancel() -> None:
            if cancel_callback:
                cancel_callback()

        _maybe_cancel()
        if df.empty:
            raise ValueError("DataFrame is empty; cannot run backtest.")

        # Prepare data & signals
        _maybe_cancel()
        prepared = strategy.prepare(df)
        _maybe_cancel()

        # Consume signals lazily to avoid materialising unbounded iterators
        raw_signals = strategy.generate_signals(prepared)
        if raw_signals is None:
            raw_signals = []
        elif isinstance(raw_signals, Signal):
            raw_signals = [raw_signals]
        signals_iter = iter(raw_signals)
        pending_signal: Optional[Signal] = None

        def _ensure_next_signal() -> None:
            nonlocal pending_signal
            if pending_signal is not None:
                return
            try:
                _maybe_cancel()
                next_sig = next(signals_iter)
            except StopIteration:
                pending_signal = None
                return
            when = pd.Timestamp(next_sig.when)
            pending_signal = next_sig
            pending_signal.when = (
                when.tz_localize("UTC")
                if getattr(when, "tzinfo", None) is None
                else when.tz_convert("UTC")
            )

        _ensure_next_signal()

        equity = float(initial_equity)
        gross_equity = float(initial_equity)
        symbol = strategy.symbol or "SYMBOL"
        trades: List[Trade] = []
        open_trade: Optional[Trade] = None
        equity_by_day: Dict[pd.Timestamp, float] = {}
        gross_by_day: Dict[pd.Timestamp, float] = {}

        # Parse early stop conditions
        early_stop_enabled = bool(early_stop_conditions)
        max_dd_threshold = early_stop_conditions.get("max_drawdown") if early_stop_conditions else None
        min_trades_threshold = early_stop_conditions.get("min_trades") if early_stop_conditions else None
        check_interval = early_stop_conditions.get("check_interval", 50) if early_stop_conditions else 50
        bar_count = 0
        early_stopped = False
        early_stop_reason = None

        # Main bar loop (Series rows to stay compatible with your helpers)
        for raw_ts, row in prepared.iterrows():
            _maybe_cancel()
            bar_count += 1
            ts = raw_ts.tz_localize("UTC") if raw_ts.tzinfo is None else raw_ts.tz_convert("UTC")
            day = ts.normalize()

            # Apply overnight swap and check for exits first
            if open_trade:
                swap_delta = self._apply_overnight_swap(symbol, open_trade, day, swap_override)
                if swap_delta:
                    equity += swap_delta

                equity, gross_equity, open_trade = self._maybe_close_trade(
                    symbol, open_trade, row, ts, equity, gross_equity, trades
                )

            # Consume any signals scheduled up to this timestamp
            while True:
                _maybe_cancel()
                if pending_signal is None:
                    _ensure_next_signal()
                if pending_signal is None or pending_signal.when > ts:
                    break
                next_sig = pending_signal
                pending_signal = None
                # Only one position at a time — skip extra signals while in a trade
                if open_trade:
                    continue

                open_trade, equity = self._open_trade(
                    strategy, ts, row, next_sig, risk_perc, equity
                )

            equity_by_day[day] = equity
            gross_by_day[day] = gross_equity

            # Check early stopping conditions periodically
            if early_stop_enabled and bar_count % check_interval == 0:
                # Check drawdown
                if max_dd_threshold is not None and equity_by_day:
                    equity_series = pd.Series(equity_by_day).sort_index()
                    current_dd = self._max_drawdown(equity_series)
                    if abs(current_dd) > max_dd_threshold:
                        early_stopped = True
                        early_stop_reason = f"max_drawdown exceeded: {abs(current_dd):.4f} > {max_dd_threshold}"
                        break

                # Check minimum trades after significant portion of data
                if min_trades_threshold is not None and bar_count > len(prepared) * 0.3:
                    if len(trades) < min_trades_threshold:
                        early_stopped = True
                        early_stop_reason = f"insufficient trades: {len(trades)} < {min_trades_threshold}"
                        break

        if early_stopped:
            # Mark as disqualified due to early stopping
            if open_trade:
                last_ts = raw_ts.tz_localize("UTC") if raw_ts.tzinfo is None else raw_ts.tz_convert("UTC")
                equity, gross_equity, _ = self._force_close(
                    symbol, open_trade, row, last_ts, equity, gross_equity, trades
                )
                equity_by_day[day] = equity
            
            # Build minimal metrics for early stopped run
            daily_equity = pd.Series(equity_by_day).sort_index().ffill()
            gross_equity_series = pd.Series(gross_by_day).sort_index().ffill()
            if gross_equity_series.empty and not daily_equity.empty:
                gross_equity_series = daily_equity.copy()
            
            metrics = self._compute_metrics(daily_equity)
            metrics["net_pnl"] = sum(t.net_pnl for t in trades)
            metrics["TradeCount"] = float(len(trades))
            metrics["Qualified"] = 0.0
            
            metadata = {
                "disqualified": True,
                "disqualify_reasons": [f"early_stop: {early_stop_reason}"],
                "early_stopped": True,
                "early_stop_reason": early_stop_reason,
                "bars_processed": bar_count,
            }
            
            return BTResult(
                trades=trades,
                daily_equity=daily_equity,
                gross_equity=gross_equity_series,
                metrics=metrics,
                metadata=metadata,
            )

        # Force-close any open position at the last bar
        if open_trade:
            last_ts = prepared.index[-1]
            last_ts = last_ts.tz_localize("UTC") if last_ts.tzinfo is None else last_ts.tz_convert("UTC")
            day = last_ts.normalize()
            swap_delta = self._apply_overnight_swap(symbol, open_trade, day, swap_override)
            if swap_delta:
                equity += swap_delta
            last_row = prepared.iloc[-1]
            equity, gross_equity, _ = self._force_close(
                symbol, open_trade, last_row, last_ts, equity, gross_equity, trades
            )
            equity_by_day[day] = equity

        # Build equity series & metrics
        daily_equity = pd.Series(equity_by_day).sort_index().ffill()
        gross_equity_series = pd.Series(gross_by_day).sort_index().ffill()
        if gross_equity_series.empty and not daily_equity.empty:
            gross_equity_series = daily_equity.copy()

        returns_series = daily_equity.pct_change().dropna()
        returns_count = int(len(returns_series))
        trade_count = int(len(trades))

        _maybe_cancel()
        metrics = self._compute_metrics(daily_equity)
        total_commission = sum(t.commission_paid for t in trades)
        total_spread = sum(t.spread_cost for t in trades)
        total_slippage = sum(t.slippage_cost for t in trades)
        total_swap = sum(t.swap_pnl for t in trades)
        total_gross = sum(t.gross_pnl for t in trades)
        total_net = sum(t.net_pnl for t in trades)
        total_fees = total_commission + total_spread + total_slippage
        gross_abs = abs(total_gross)
        if gross_abs <= 1e-9:
            fees_to_gross = 1.0 if total_fees > 0 else 0.0
        else:
            fees_to_gross = float(total_fees) / gross_abs

        (
            robust_score,
            score_components,
            disqualified,
            reasons,
            psr_guardrail,
        ) = self._evaluate_robust_score(
            metrics,
            fees_to_gross,
            returns_count=returns_count,
            trade_count=trade_count,
        )

        metrics.update(
            {
                "gross_pnl": float(total_gross),
                "net_pnl": float(total_net),
                "total_commission": float(total_commission),
                "total_spread_cost": float(total_spread),
                "total_slippage_cost": float(total_slippage),
                "total_swap_pnl": float(total_swap),
                "FeesToGross": float(fees_to_gross),
                "RobustScore": float(robust_score),
                "Qualified": 0.0 if disqualified else 1.0,
                "ReturnCount": float(returns_count),
                "TradeCount": float(trade_count),
            }
        )

        psr_min_returns = (
            int(psr_guardrail["min_returns"]) if psr_guardrail else 45
        )
        psr_min_trades = int(psr_guardrail["min_trades"]) if psr_guardrail else 10

        metadata = {
            "disqualified": disqualified,
            "disqualify_reasons": reasons,
            "robust_score_components": score_components,
            "robust_score_thresholds": {
                "drawdown": 0.55,
                "psr": 0.5,
                "psr_min_returns": psr_min_returns,
                "psr_min_trades": psr_min_trades,
                "fees_to_gross": 0.6,
                "turnover": 0.15,
                "sharpe": 3.0,
                "sortino": 4.0,
                "tail_ratio": 3.0,
            },
            "sample_counts": {
                "returns": returns_count,
                "trades": trade_count,
            },
        }
        if psr_guardrail:
            metadata["psr_guardrail"] = psr_guardrail

        return BTResult(
            trades=trades,
            daily_equity=daily_equity,
            gross_equity=gross_equity_series,
            metrics=metrics,
            metadata=metadata,
        )


    def _open_trade(
        self,
        strategy: BaseStrategy,
        ts: pd.Timestamp,
        row: pd.Series,
        signal: Signal,
        risk_perc: float,
        equity: float,
    ) -> tuple[Optional[Trade], float]:
        symbol = strategy.symbol or "SYMBOL"
        stop_points = float(strategy.stop_distance_points(row))
        if stop_points <= 0:
            return None, equity
        take_points = float(strategy.take_distance_points(row))
        point_value = costs.get_point_value(symbol)
        if point_value <= 0:
            return None, equity
        risk_dollars = equity * risk_perc
        volume = round(risk_dollars / (point_value * stop_points), 2)
        if volume <= 0:
            return None, equity

        commission = costs.commission_one_side(symbol, float(row["close"]), volume)
        spread_points = float(row.get("spread", 0.0)) if self.cfg.apply_spread_cost else 0.0
        spread_cost = costs.spread_cost(symbol, spread_points / 2.0, volume) if spread_points else 0.0
        slippage_points = self._slippage_points(symbol, row)
        slippage_cost_val = costs.slippage_cost(symbol, slippage_points, volume) if slippage_points else 0.0
        equity -= commission + spread_cost + slippage_cost_val

        sig_time = signal.when.tz_localize("UTC") if signal.when.tzinfo is None else signal.when.tz_convert("UTC")
        entry_time = max(sig_time, ts)
        trade = Trade(
            symbol=symbol,
            side="long" if signal.action == "buy" else "short",
            entry_time=entry_time,
            entry_price=float(row["close"]),
            volume=volume,
            stop_points=stop_points,
            take_points=max(take_points, 0.0),
            commission_paid=commission,
            spread_cost=spread_cost,
            slippage_cost=slippage_cost_val,
            gross_pnl=0.0,
            net_pnl=0.0,
        )
        trade._last_swap_day = entry_time.normalize()
        return trade, equity

    def _maybe_close_trade(
        self,
        symbol: str,
        trade: Trade,
        row: pd.Series,
        ts: pd.Timestamp,
        equity: float,
        gross_equity: float,
        trades: List[Trade],
    ) -> tuple[float, float, Optional[Trade]]:
        pv = costs.get_point_value(symbol)
        stop_hit = False
        take_hit = False
        if trade.side == "long":
            stop_price = trade.entry_price - trade.stop_points
            take_price = trade.entry_price + trade.take_points if trade.take_points > 0 else None
            if row["low"] <= stop_price:
                fill = stop_price
                stop_hit = True
            elif take_price is not None and row["high"] >= take_price:
                fill = take_price
                take_hit = True
            else:
                return equity, gross_equity, trade
            pnl = (fill - trade.entry_price) * pv * trade.volume
        else:
            stop_price = trade.entry_price + trade.stop_points
            take_price = trade.entry_price - trade.take_points if trade.take_points > 0 else None
            if row["high"] >= stop_price:
                fill = stop_price
                stop_hit = True
            elif take_price is not None and row["low"] <= take_price:
                fill = take_price
                take_hit = True
            else:
                return equity, gross_equity, trade
            pnl = (trade.entry_price - fill) * pv * trade.volume

        commission = costs.commission_one_side(symbol, float(fill), trade.volume)
        slippage_points = self._slippage_points(symbol, row)
        slippage_cost_val = costs.slippage_cost(symbol, slippage_points, trade.volume) if slippage_points else 0.0
        trade.exit_time = ts
        trade.exit_price = float(fill)
        trade.gross_pnl = pnl
        trade.commission_paid += commission
        trade.slippage_cost += slippage_cost_val
        trade.pnl = pnl - commission - slippage_cost_val
        total_costs = trade.commission_paid + trade.spread_cost + trade.slippage_cost
        trade.net_pnl = trade.gross_pnl - total_costs + trade.swap_pnl
        trade.notes["exit_stop"] = 1.0 if stop_hit else 0.0
        trade.notes["exit_take"] = 1.0 if take_hit else 0.0
        equity += trade.pnl
        gross_equity += trade.gross_pnl
        trades.append(trade)
        return equity, gross_equity, None

    def _force_close(
        self,
        symbol: str,
        trade: Trade,
        row: pd.Series,
        ts: pd.Timestamp,
        equity: float,
        gross_equity: float,
        trades: List[Trade],
    ) -> tuple[float, float, Optional[Trade]]:
        pv = costs.get_point_value(symbol)
        if trade.side == "long":
            pnl = (row["close"] - trade.entry_price) * pv * trade.volume
        else:
            pnl = (trade.entry_price - row["close"]) * pv * trade.volume
        commission = costs.commission_one_side(symbol, float(row["close"]), trade.volume)
        slippage_points = self._slippage_points(symbol, row)
        slippage_cost_val = costs.slippage_cost(symbol, slippage_points, trade.volume) if slippage_points else 0.0
        trade.exit_time = ts
        trade.exit_price = float(row["close"])
        trade.gross_pnl = pnl
        trade.commission_paid += commission
        trade.slippage_cost += slippage_cost_val
        trade.pnl = pnl - commission - slippage_cost_val
        total_costs = trade.commission_paid + trade.spread_cost + trade.slippage_cost
        trade.net_pnl = trade.gross_pnl - total_costs + trade.swap_pnl
        equity += trade.pnl
        gross_equity += trade.gross_pnl
        trades.append(trade)
        return equity, gross_equity, None

    def _tick_size(self, symbol: str) -> float:
        inst = self.instruments.get(symbol)
        if inst and inst.tick_size:
            return float(inst.tick_size)
        return 1.0

    def _slippage_points(self, symbol: str, row: pd.Series) -> float:
        tick = self._tick_size(symbol)
        base = float(self.cfg.default_slippage_points) * tick
        if self.cfg.slippage_atr_multiplier > 0 and "atr" in row and not pd.isna(row["atr"]):
            base += float(row["atr"]) * self.cfg.slippage_atr_multiplier
        return base if base else 0.0

    def _apply_overnight_swap(
        self,
        symbol: str,
        trade: Trade,
        current_day: pd.Timestamp,
        swap_override: Optional[dict],
    ) -> float:
        if not self.cfg.apply_swap_cost:
            return 0.0
        if trade._last_swap_day is None:
            trade._last_swap_day = current_day
            return 0.0
        delta_total = 0.0
        while trade._last_swap_day < current_day:
            trade._last_swap_day += pd.Timedelta(days=1)
            direction = "long" if trade.side == "long" else "short"
            swap_delta = costs.swap_cost_per_day(symbol, trade.volume, direction, static_override=swap_override)
            trade.swap_pnl += swap_delta
            delta_total += swap_delta
        return delta_total

    def _compute_metrics(self, daily_equity: pd.Series) -> Dict[str, float]:
        if daily_equity.empty or len(daily_equity) < 2:
            return {
                "CAGR": 0.0,
                "Sharpe": 0.0,
                "Sortino": 0.0,
                "MaxDD": 0.0,
                "PSR": 0.0,
                "DSR": 0.0,
                "Calmar": 0.0,
                "TailRatio": 0.0,
                "ExpectedShortfall": 0.0,
                "ReturnAutocorr": 0.0,
                "Stability": 0.0,
                "Turnover": 0.0,
            }

        eq = daily_equity.sort_index()
        returns = eq.pct_change().dropna()
        if returns.empty:
            return {
                "CAGR": 0.0,
                "Sharpe": 0.0,
                "Sortino": 0.0,
                "MaxDD": 0.0,
                "PSR": 0.0,
                "DSR": 0.0,
                "Calmar": 0.0,
                "TailRatio": 0.0,
                "ExpectedShortfall": 0.0,
                "ReturnAutocorr": 0.0,
                "Stability": 0.0,
                "Turnover": 0.0,
            }

        ann_factor = 252
        mu = returns.mean() * ann_factor
        sigma = returns.std(ddof=1) * math.sqrt(ann_factor)
        downside = returns[returns < 0].std(ddof=1) * math.sqrt(ann_factor)
        sharpe = mu / sigma if sigma > 0 else 0.0
        sortino = mu / downside if downside > 0 else 0.0
        max_dd = self._max_drawdown(eq)
        psr = self._probabilistic_sharpe(returns)
        dsr = self._deflated_sharpe(returns, sharpe)
        cagr = self._cagr(eq)
        calmar = cagr / abs(max_dd) if max_dd < 0 else 0.0
        tail_ratio = self._tail_ratio(returns)
        expected_shortfall = self._expected_shortfall(returns)
        autocorr = returns.autocorr(lag=1)
        if pd.isna(autocorr):
            autocorr = 0.0
        autocorr = float(autocorr)
        stability = max(0.0, min(1.0, 1.0 - abs(autocorr)))
        turnover = float(returns.abs().mean())

        return {
            "CAGR": cagr,
            "Sharpe": sharpe,
            "Sortino": sortino,
            "MaxDD": max_dd,
            "PSR": psr,
            "DSR": dsr,
            "Calmar": calmar,
            "TailRatio": tail_ratio,
            "ExpectedShortfall": expected_shortfall,
            "ReturnAutocorr": autocorr,
            "Stability": stability,
            "Turnover": turnover,
        }

    @staticmethod
    def _tail_ratio(returns: pd.Series) -> float:
        positive = returns[returns > 0]
        negative = returns[returns < 0]
        if positive.empty or negative.empty:
            return 0.0
        denom = abs(float(negative.mean()))
        if denom <= 0:
            return 0.0
        return float(positive.mean()) / denom

    @staticmethod
    def _expected_shortfall(returns: pd.Series, alpha: float = 0.05) -> float:
        if returns.empty:
            return 0.0
        threshold = returns.quantile(alpha)
        tail = returns[returns <= threshold]
        if tail.empty:
            return 0.0
        return float(-tail.mean())

    @staticmethod
    def _evaluate_robust_score(
        metrics: Dict[str, float],
        fees_to_gross: float,
        *,
        returns_count: int = 0,
        trade_count: int = 0,
    ) -> tuple[float, Dict[str, float], bool, List[str], Optional[Dict[str, Any]]]:
        sharpe = float(metrics.get("Sharpe") or 0.0)
        sortino = float(metrics.get("Sortino") or 0.0)
        max_dd = float(metrics.get("MaxDD") or 0.0)
        tail_ratio = float(metrics.get("TailRatio") or 0.0)
        stability = float(metrics.get("Stability") or 0.0)
        turnover = float(metrics.get("Turnover") or 0.0)
        psr = float(metrics.get("PSR") or 0.0)

        def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
            return max(lower, min(upper, value))

        def _normalize_positive(value: float, upper: float) -> float:
            if upper <= 0:
                return 0.0
            if value <= 0:
                return 0.0
            return _clamp(value / upper)

        drawdown_threshold = 0.5
        turnover_threshold = 0.15
        sharpe_score = _normalize_positive(sharpe, 3.0)
        sortino_score = _normalize_positive(sortino, 4.0)
        drawdown_penalty = _clamp(abs(max_dd) / drawdown_threshold) if drawdown_threshold > 0 else 1.0
        drawdown_score = _clamp(1.0 - drawdown_penalty)
        tail_score = _normalize_positive(tail_ratio, 3.0)
        stability_score = _clamp(stability)
        turnover_penalty = _clamp(turnover / turnover_threshold) if turnover_threshold > 0 else 1.0
        turnover_score = _clamp(1.0 - turnover_penalty)

        robust_score = (
            0.35 * sharpe_score
            + 0.15 * sortino_score
            + 0.15 * drawdown_score
            + 0.10 * tail_score
            + 0.10 * stability_score
            + 0.15 * turnover_score
        )
        robust_score = _clamp(robust_score)

        min_psr_returns = 45
        min_psr_trades = 10
        psr_guardrail: Optional[Dict[str, Any]] = {
            "eligible": bool(
                returns_count >= min_psr_returns and trade_count >= min_psr_trades
            ),
            "min_returns": int(min_psr_returns),
            "min_trades": int(min_psr_trades),
            "actual_returns": int(returns_count),
            "actual_trades": int(trade_count),
        }

        disqualify_reasons: List[str] = []
        if abs(max_dd) > 1e-9 and abs(max_dd) > 0.55:
            disqualify_reasons.append("drawdown")
        psr_eligible = bool(psr_guardrail and psr_guardrail["eligible"])
        if psr < 0.5 and psr_eligible:
            disqualify_reasons.append("psr")
        if fees_to_gross > 0.6:
            disqualify_reasons.append("fees")

        if psr_guardrail is not None and not psr_eligible and psr < 0.5:
            psr_guardrail["reason"] = "insufficient_samples"

        disqualified = bool(disqualify_reasons)
        if disqualified:
            robust_score = 0.0

        components = {
            "sharpe": sharpe_score,
            "sortino": sortino_score,
            "drawdown": drawdown_score,
            "tail_ratio": tail_score,
            "stability": stability_score,
            "turnover": turnover_score,
        }

        return robust_score, components, disqualified, disqualify_reasons, psr_guardrail

    @staticmethod
    def _cagr(eq: pd.Series) -> float:
        start = eq.iloc[0]
        end = eq.iloc[-1]
        days = (eq.index[-1] - eq.index[0]).days or 1
        years = days / 365.25
        if start <= 0 or years <= 0:
            return 0.0
        return float((end / start) ** (1 / years) - 1)

    @staticmethod
    def _max_drawdown(eq: pd.Series) -> float:
        running_max = eq.cummax()
        drawdown = (eq - running_max) / running_max.replace(0, np.nan)
        return float(drawdown.min())

    @staticmethod
    def _probabilistic_sharpe(returns: pd.Series, benchmark: float = 0.0) -> float:
        values = returns.values
        n = len(values)
        if n < 20:
            return 0.0
        mean = values.mean()
        sd = values.std(ddof=1)
        if sd <= 0:
            return 0.0
        sr_hat = (mean / sd) * math.sqrt(252)
        series = pd.Series(values)
        skew = series.skew()
        kurt = series.kurtosis()
        se = math.sqrt((1 + 0.5 * sr_hat**2 - skew * sr_hat + (kurt / 4) * sr_hat**2) / (n - 1))
        if se <= 0:
            return 0.0
        z = (sr_hat - benchmark) / se
        from math import erf, sqrt
        return 0.5 * (1 + erf(z / sqrt(2)))
    @staticmethod
    def _deflated_sharpe(returns: pd.Series, sharpe: float) -> float:
        values = returns.values
        n = len(values)
        if n < 20 or sharpe == 0:
            return 0.0
        series = pd.Series(values)
        skew = series.skew()
        kurt = series.kurtosis()
        term = math.sqrt(max(1e-9, 1 - skew * sharpe + (kurt - 1) * (sharpe ** 2) / 4))
        z = sharpe * math.sqrt(n - 1) / term
        from math import erf, sqrt
        return 0.5 * (1 + erf(z / sqrt(2)))
