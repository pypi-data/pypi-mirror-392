"""Arbitrix algorithmic trading toolkit."""

from ._version import __version__

__all__ = ["__version__"]

try:  # pragma: no cover - optional dependency guard
    from .config import load_config, AppConfig  # noqa: F401
except ModuleNotFoundError as exc:  # pragma: no cover - triggered if pyyaml missing or config omitted
    if exc.name not in {"yaml", "arbitrix.config", "config"}:
        raise

    def load_config(*_args, **_kwargs):  # type: ignore
        raise ModuleNotFoundError(
            "Configuration support is unavailable; install the full Arbitrix package to enable it."
        ) from exc

    AppConfig = None  # type: ignore
else:  # pragma: no cover - executed when config is available
    __all__.extend(["load_config", "AppConfig"])
