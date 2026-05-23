"""RI-5 real scenario replay — 83 scenarios × positive/negative."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / ".venv" / "bin" / "python"
RUN = ROOT / "simulation" / "real" / "run_real_scenario.py"
REPORTS = ROOT / "reports" / "real" / "scenarios"
SCENARIOS_YML = ROOT / "simulation" / "feature_catalog" / "scenarios.yml"


def _all_scenario_ids() -> list[str]:
    doc = yaml.safe_load(SCENARIOS_YML.read_text(encoding="utf-8"))
    return [s["scenario_id"] for s in doc["scenarios"]]


def _run(scenario_id: str, mode: str) -> dict:
    subprocess.run(
        [str(PYTHON), str(RUN), "--scenario", scenario_id, "--mode", mode],
        cwd=ROOT,
        check=True,
    )
    return json.loads((REPORTS / f"{scenario_id}-{mode}.json").read_text(encoding="utf-8"))


@pytest.mark.real
@pytest.mark.scenario
@pytest.mark.parametrize("scenario_id", _all_scenario_ids())
def test_real_scenario_positive(scenario_id: str, require_real_stack: None) -> None:
    evidence = _run(scenario_id, "positive")
    assert evidence["scenario_id"] == scenario_id
    assert evidence["parity_level"] == "L2"
    assert evidence["result"] == "PASS"
    assert evidence["anomaly_detected"] is True
    assert len(evidence["feature_ids"]) >= 1
    assert len(evidence["actions_executed"]) >= 1
    assert len(evidence["raw_logs_asserted"]) >= 1
    assert evidence["seed_refs"]


@pytest.mark.real
@pytest.mark.scenario
@pytest.mark.parametrize("scenario_id", _all_scenario_ids())
def test_real_scenario_negative(scenario_id: str, require_real_stack: None) -> None:
    evidence = _run(scenario_id, "negative")
    assert evidence["result"] == "PASS"
    assert evidence["anomaly_detected"] is False


@pytest.mark.real
def test_real_scenario_count_is_83() -> None:
    assert len(_all_scenario_ids()) == 83
