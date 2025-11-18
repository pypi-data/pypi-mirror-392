from __future__ import annotations

import copy
import importlib
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


@dataclass
class StrategyBundle:
    strategy: Any
    risk_per_trade: float
    swap_override: Optional[dict] = None


@dataclass
class StrategyConfigEntry:
    name: str
    enabled: bool
    module: str
    class_name: str
    config_class: Optional[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    parameter_metadata: Dict[str, Any] = field(default_factory=dict)
    risk_parameter: Optional[str] = None
    risk_in_config: bool = False
    swap_attribute: Optional[str] = None
    source: str = "config"

    def as_dict(self) -> Dict[str, Any]:
        data = {
            "name": self.name,
            "enabled": self.enabled,
            "module": self.module,
            "class_name": self.class_name,
            "parameters": copy.deepcopy(self.parameters),
            "source": self.source,
        }
        if self.config_class:
            data["config_class"] = self.config_class
        if self.parameter_metadata:
            data["parameter_metadata"] = copy.deepcopy(self.parameter_metadata)
        if self.risk_parameter:
            data["risk_parameter"] = self.risk_parameter
            data["risk_in_config"] = self.risk_in_config
        if self.swap_attribute:
            data["swap_attribute"] = self.swap_attribute
        return data


DEFAULT_STRATEGY_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "breakout_index": {
        "module": "arbitrix.core.strategies.breakout_index",
        "class_name": "BreakoutIndexStrategy",
        "config_class": "BreakoutConfig",
        "risk_parameter": "risk_per_trade",
        "risk_in_config": False,
    },
    "meanrev_gold": {
        "module": "arbitrix.core.strategies.meanrev_gold",
        "class_name": "MeanRevGoldStrategy",
        "config_class": "MeanRevGoldConfig",
        "risk_parameter": "risk_per_trade",
        "risk_in_config": False,
    },
    "carry_trade": {
        "module": "arbitrix.core.strategies.carry_trade",
        "class_name": "CarryTradeStrategy",
        "config_class": "CarryConfig",
        "risk_parameter": "risk_per_pair",
        "risk_in_config": True,
        "swap_attribute": "static_swap_points",
    },
}


_RESERVED_KEYS = {
    "enabled",
    "module",
    "class_name",
    "config_class",
    "parameters",
    "parameter_metadata",
    "risk_parameter",
    "risk_in_config",
    "swap_attribute",
    "source",
}


def _strategy_roots() -> list[Path]:
    raw_paths = os.getenv("ARBITRIX_STRATEGIES_PATH")
    candidates: list[Path] = []
    if raw_paths:
        for chunk in raw_paths.split(os.pathsep):
            cleaned = chunk.strip()
            if cleaned:
                candidates.append(Path(cleaned))
    else:
        candidates.extend(
            [
                Path("runtime/strategies"),
                Path("/app/runtime/strategies"),
                Path("/app/strategies"),
            ]
        )

    ensured: list[Path] = []
    for path in candidates:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except (PermissionError, FileNotFoundError):
            continue
        normalized = path.resolve()
        if normalized not in ensured:
            ensured.append(normalized)
    if not ensured:
        fallback = Path("runtime/strategies")
        fallback.mkdir(parents=True, exist_ok=True)
        ensured.append(fallback.resolve())
    return ensured


def _strategy_root() -> Path:
    roots = _strategy_roots()
    return roots[0] if roots else Path.cwd()


def ensure_strategy_path() -> None:
    """Ensure the strategies root directory is importable."""

    for root in _strategy_roots():
        root_str = str(root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)


def parse_strategy_entry(name: str, raw: Dict[str, Any]) -> StrategyConfigEntry:
    data = copy.deepcopy(raw or {})
    defaults = DEFAULT_STRATEGY_TEMPLATES.get(name, {})
    enabled = bool(data.get("enabled", False))
    module = data.get("module") or defaults.get("module")
    class_name = data.get("class_name") or defaults.get("class_name")
    config_class = data.get("config_class") or defaults.get("config_class")
    if not module or not class_name:
        raise ValueError(f"Strategy '{name}' is missing module/class definition")
    parameters = data.get("parameters")
    if parameters is None:
        parameters = {k: v for k, v in data.items() if k not in _RESERVED_KEYS}
    risk_parameter = data.get("risk_parameter") or defaults.get("risk_parameter")
    risk_in_config = bool(data.get("risk_in_config", defaults.get("risk_in_config", False)))
    swap_attribute = data.get("swap_attribute") or defaults.get("swap_attribute")
    return StrategyConfigEntry(
        name=name,
        enabled=enabled,
        module=module,
        class_name=class_name,
        config_class=config_class,
        parameters=parameters,
        parameter_metadata=copy.deepcopy(data.get("parameter_metadata", {})),
        risk_parameter=risk_parameter,
        risk_in_config=risk_in_config,
        swap_attribute=swap_attribute,
        source=data.get("source", "config"),
    )


def _strategy_mapping(cfg: Any) -> Dict[str, Any]:
    if cfg is None:
        return {}
    if isinstance(cfg, Mapping):
        return dict(cfg)
    data = getattr(cfg, "strategies", None)
    if isinstance(data, Mapping):
        return dict(data)
    return {}


def _risk_settings(cfg: Any) -> Dict[str, Any]:
    if cfg is None:
        return {}
    if isinstance(cfg, Mapping):
        raw = cfg.get("risk", {})
        return dict(raw) if isinstance(raw, Mapping) else {}
    risk = getattr(cfg, "risk", None)
    if isinstance(risk, Mapping):
        return dict(risk)
    return {}


def load_strategy_entries(cfg: Any) -> Dict[str, StrategyConfigEntry]:
    ensure_strategy_path()
    entries: Dict[str, StrategyConfigEntry] = {}
    for name, raw in _strategy_mapping(cfg).items():
        try:
            entries[name] = parse_strategy_entry(name, raw)
        except ValueError:
            continue
    return entries


def build_strategy_bundle(
    cfg: Any,
    entry: StrategyConfigEntry,
    overrides: Optional[Dict[str, Any]] = None,
    force_enabled: Optional[bool] = None,
) -> Optional[StrategyBundle]:
    if force_enabled is not None:
        enabled = force_enabled
    else:
        enabled = entry.enabled
    if not enabled:
        return None

    params = copy.deepcopy(entry.parameters)
    if overrides:
        params.update(copy.deepcopy(overrides))

    risk_cfg = _risk_settings(cfg)
    risk_value = risk_cfg.get("risk_per_trade_default", 0.01)
    if entry.risk_parameter:
        risk_raw = params.get(entry.risk_parameter)
        if risk_raw is not None:
            try:
                risk_value = float(risk_raw)
            except (TypeError, ValueError):
                pass
        if not entry.risk_in_config:
            params.pop(entry.risk_parameter, None)

    module = importlib.import_module(entry.module)
    strategy_cls = getattr(module, entry.class_name)
    if entry.config_class:
        config_cls = getattr(module, entry.config_class)
        config_obj = config_cls(**params)
        strategy = strategy_cls(config_obj)
        strategy_cfg = getattr(strategy, "cfg", config_obj)
    else:
        strategy = strategy_cls(**params)
        strategy_cfg = getattr(strategy, "cfg", None)

    swap_override = None
    if entry.swap_attribute:
        target = strategy_cfg or strategy
        swap_override = getattr(target, entry.swap_attribute, None)

    return StrategyBundle(strategy=strategy, risk_per_trade=float(risk_value), swap_override=swap_override)


def select_strategy_bundles(
    cfg: Any,
    overrides: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, StrategyBundle]:
    bundles: Dict[str, StrategyBundle] = {}
    entries = load_strategy_entries(cfg)
    overrides = overrides or {}
    for name, entry in entries.items():
        override = overrides.get(name)
        if override:
            enabled = override.get("enabled")
            bundle = build_strategy_bundle(
                cfg,
                entry,
                overrides=override.get("parameters"),
                force_enabled=entry.enabled if enabled is None else bool(enabled),
            )
        else:
            bundle = build_strategy_bundle(cfg, entry)
        if bundle:
            bundles[name] = bundle
    return bundles
