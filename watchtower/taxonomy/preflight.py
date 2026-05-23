"""Preflight checks for taxonomy reference artifacts."""

from __future__ import annotations

from pathlib import Path

from watchtower.config.paths import PREFLIGHT_REFERENCES


def preflight_missing(project_root: Path | None = None) -> list[str]:
    """Return names of missing preflight reference files."""
    root = project_root
    if root is None:
        from watchtower.config.paths import PROJECT_ROOT

        root = PROJECT_ROOT

    missing: list[str] = []
    for name, path in PREFLIGHT_REFERENCES.items():
        resolved = path if path.is_absolute() else root / path
        if not resolved.is_file():
            missing.append(name)
    return missing


def check_preflight_references(project_root: Path | None = None) -> None:
    """Raise FileNotFoundError when any preflight reference is missing."""
    missing = preflight_missing(project_root)
    if missing:
        details = ", ".join(sorted(missing))
        msg = f"Preflight reference files missing: {details}"
        raise FileNotFoundError(msg)
