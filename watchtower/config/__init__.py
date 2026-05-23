"""Watchtower configuration paths and loaders."""

from pathlib import Path

from watchtower.config.loader import load_settings
from watchtower.config.settings import DEFAULT_SETTINGS, WatchtowerMode, WatchtowerSettings

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PACKAGE_ROOT.parent
FEATURE_TAXONOMY_PATH = PACKAGE_ROOT / "config" / "feature_taxonomy.yml"

# Preflight reference artifacts (relative to watchtower-demo project root).
PREFLIGHT_REFERENCES: dict[str, Path] = {
    "watchtower_features_final": PROJECT_ROOT
    / "server-stack"
    / "watchtower-features-final.md",
    "server_stack_features_yml": PROJECT_ROOT
    / "server-stack"
    / "simulation"
    / "feature_catalog"
    / "features.yml",
    "real_final_gate_json": PROJECT_ROOT
    / "server-stack"
    / "reports"
    / "real"
    / "coverage"
    / "real_final_gate.json",
}

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
