"""Normalization test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from watchtower.config.paths import PROJECT_ROOT
from watchtower.normalization.service import NormalizationService

FEATURE_REPLAYS = PROJECT_ROOT / "server-stack" / "simulation" / "feature_replays"
SCENARIOS = PROJECT_ROOT / "server-stack" / "simulation" / "scenarios"

TENANT_ID = "test-tenant-normalize"


@pytest.fixture
def normalizer() -> NormalizationService:
    return NormalizationService()


def load_feature_replay(feature_id: str, *, positive: bool = True) -> dict:
    suffix = "positive" if positive else "negative"
    path = FEATURE_REPLAYS / f"{feature_id}_{suffix}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_scenario_replay(scenario_id: str, *, positive: bool = True) -> dict:
    suffix = "positive" if positive else "negative"
    path = SCENARIOS / f"{scenario_id}_{suffix}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))
