"""Watchtower configuration paths and loaders."""

from watchtower.config.loader import load_settings
from watchtower.config.paths import (
    FEATURE_TAXONOMY_PATH,
    PACKAGE_ROOT,
    PREFLIGHT_REFERENCES,
    PROJECT_ROOT,
)
from watchtower.config.settings import DEFAULT_SETTINGS, WatchtowerMode, WatchtowerSettings

__all__ = [
    "DEFAULT_SETTINGS",
    "FEATURE_TAXONOMY_PATH",
    "PACKAGE_ROOT",
    "PREFLIGHT_REFERENCES",
    "PROJECT_ROOT",
    "WatchtowerMode",
    "WatchtowerSettings",
    "load_settings",
]
