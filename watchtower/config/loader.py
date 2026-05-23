"""Merge defaults, YAML config file, and environment into settings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from watchtower.config import PROJECT_ROOT
from watchtower.config.settings import WatchtowerSettings

_CONFIG_SEARCH_PATHS = (
    PROJECT_ROOT / "watchtower.yml",
    PROJECT_ROOT / "config" / "watchtower.yml",
    Path.home() / ".config" / "watchtower" / "config.yml",
)


def _load_yaml_config(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        msg = f"Config file must be a mapping: {path}"
        raise ValueError(msg)
    return data


def _resolve_config_file(explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit if explicit.is_file() else None
    for candidate in _CONFIG_SEARCH_PATHS:
        if candidate.is_file():
            return candidate
    return None


def load_settings(
    *,
    config_file: Path | None = None,
    overrides: dict[str, Any] | None = None,
) -> WatchtowerSettings:
    """Load settings: built-in defaults, optional YAML file, then env vars."""
    resolved_file = _resolve_config_file(config_file)
    file_data = _load_yaml_config(resolved_file) if resolved_file else {}

    merged: dict[str, Any] = {}
    merged.update(file_data)
    if overrides:
        merged.update(overrides)
    if resolved_file is not None:
        merged.setdefault("config_file", resolved_file)

    try:
        return WatchtowerSettings(**merged)
    except ValidationError as exc:
        msg = f"Invalid Watchtower configuration: {exc}"
        raise ValueError(msg) from exc
