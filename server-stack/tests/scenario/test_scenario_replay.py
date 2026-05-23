"""Phase 4 scenario replay and evidence assertions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"
RUN_SCENARIO = ROOT / "simulation" / "scenarios" / "run_scenario.py"
REPLAY_DIR = ROOT / "simulation" / "scenarios"
REPORTS = ROOT / "reports" / "scenarios"
SCENARIOS_YML = ROOT / "simulation" / "feature_catalog" / "scenarios.yml"


def _all_scenario_ids() -> list[str]:
    doc = yaml.safe_load(SCENARIOS_YML.read_text(encoding="utf-8"))
    return [s["scenario_id"] for s in doc["scenarios"]]


def _run(scenario_id: str, mode: str) -> dict:
    cmd = [str(PYTHON), str(RUN_SCENARIO), "--scenario", scenario_id, "--mode", mode]
    subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    path = REPORTS / f"{scenario_id}-{mode}.json"
    assert path.exists()
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.scenario
@pytest.mark.parametrize("scenario_id", _all_scenario_ids())
def test_scenario_positive_replay(scenario_id: str) -> None:
    assert (REPLAY_DIR / f"{scenario_id}_positive.yaml").exists()
    evidence = _run(scenario_id, "positive")
    assert evidence["scenario_id"] == scenario_id
    assert evidence["anomaly_detected"] is True
    assert evidence["status"] == "PASS"
    assert len(evidence["feature_ids"]) >= 1
    assert len(evidence["services"]) >= 1
    assert evidence["event_count"] >= 2


@pytest.mark.scenario
@pytest.mark.parametrize("scenario_id", _all_scenario_ids())
def test_scenario_negative_replay(scenario_id: str) -> None:
    assert (REPLAY_DIR / f"{scenario_id}_negative.yaml").exists()
    evidence = _run(scenario_id, "negative")
    assert evidence["scenario_id"] == scenario_id
    assert evidence["anomaly_detected"] is False
    assert evidence["status"] == "PASS"


@pytest.mark.scenario
def test_scenario_count_is_83() -> None:
    assert len(_all_scenario_ids()) == 83
