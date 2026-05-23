"""Shared fixtures for feature tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = ROOT / "simulation" / "feature_catalog" / "features.yml"


@pytest.fixture(scope="session")
def all_features() -> list[dict]:
    doc = yaml.safe_load(FEATURES_PATH.read_text(encoding="utf-8"))
    return doc["features"]


@pytest.fixture(scope="session")
def phase1_features(all_features: list[dict]) -> list[dict]:
    return [f for f in all_features if f.get("phase") == 1]


@pytest.fixture(scope="session")
def phase1_ids(phase1_features: list[dict]) -> list[str]:
    return [f["feature_id"] for f in phase1_features]
