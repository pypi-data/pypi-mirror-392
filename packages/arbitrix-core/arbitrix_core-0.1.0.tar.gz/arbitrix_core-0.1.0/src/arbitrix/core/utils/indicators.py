from __future__ import annotations

from typing import Tuple
import numpy as np
import pandas as pd

__all__ = [
    "sma",
    "ema",
    "rsi",
    "atr",
    "bollinger",
    "resample_ohlcv_to_daily",
]

def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=window).mean()

def ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()

def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    gain = up.ewm(alpha=1 / window, adjust=False).mean()
    loss = down.ewm(alpha=1 / window, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50.0)

def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False).mean()

def bollinger(series: pd.Series, window: int = 20, mult: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    mid = sma(series, window)
    std = series.rolling(window, min_periods=window).std()
    upper = mid + mult * std
    lower = mid - mult * std
    bandwidth = (upper - lower) / mid.replace(0, np.nan)
    return upper, mid, lower, bandwidth

def resample_ohlcv_to_daily(df: pd.DataFrame) -> pd.DataFrame:
    open_ = df["open"].resample("1D").first()
    high_ = df["high"].resample("1D").max()
    low_ = df["low"].resample("1D").min()
    close_ = df["close"].resample("1D").last()
    volume_src = df.get("real_volume", df.get("tick_volume", pd.Series(index=df.index, dtype=float)))
    volume_ = volume_src.resample("1D").sum()
    out = pd.DataFrame({"open": open_, "high": high_, "low": low_, "close": close_, "volume": volume_})
    return out.dropna(how="any")
