from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional


@dataclass
class ProgressUpdate:
    category: str
    label: str
    completed: int
    total: int
    status: str = "running"
    extras: Optional[Dict[str, object]] = None


ProgressCallback = Callable[[ProgressUpdate], None]


def format_progress_bar(completed: int, total: int, width: int = 20) -> str:
    if total <= 0:
        return "[{}]".format("-" * width)
    completed = max(0, min(completed, total))
    ratio = completed / total
    filled = min(width, max(0, int(round(ratio * width))))
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {completed}/{total} ({ratio * 100:.1f}%)"
