"""Scenario catalog integrity for Phase 4."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_YML = ROOT / "simulation" / "feature_catalog" / "scenarios.yml"
REPLAY_DIR = ROOT / "simulation" / "scenarios"


def test_scenario_yaml_files_exist() -> None:
    doc = yaml.safe_load(SCENARIOS_YML.read_text(encoding="utf-8"))
    ids = [s["scenario_id"] for s in doc["scenarios"]]
    assert len(ids) == 83
    for sid in ids:
        assert (REPLAY_DIR / f"{sid}_positive.yaml").exists(), sid
        assert (REPLAY_DIR / f"{sid}_negative.yaml").exists(), sid
