"""RI-1 P0 real feature positive/negative replay tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / ".venv" / "bin" / "python"
RUN = ROOT / "simulation" / "real" / "run_real_feature.py"
REPORTS = ROOT / "reports" / "real" / "features"

P0_FEATURES = [
    "F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007", "F-008",
    "F-010", "F-011", "F-015", "F-037", "F-038", "F-039", "F-040", "F-041",
    "F-055", "F-057", "F-063", "F-079", "F-080", "F-081",
]


def _run(feature_id: str, mode: str) -> dict:
    subprocess.run(
        [str(PYTHON), str(RUN), "--feature", feature_id, "--mode", mode],
        cwd=ROOT,
        check=True,
    )
    path = REPORTS / f"{feature_id}-{mode}.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.real
@pytest.mark.p0
@pytest.mark.parametrize("feature_id", P0_FEATURES)
def test_p0_real_positive(feature_id: str, require_real_stack: None) -> None:
    evidence = _run(feature_id, "positive")
    assert evidence["feature_id"] == feature_id
    assert evidence["parity_level"] == "L3"
    assert evidence["result"] == "PASS"
    assert evidence["anomaly_detected"] is True
    assert len(evidence["actions_executed"]) >= 1
    assert len(evidence["raw_logs_asserted"]) >= 1


@pytest.mark.real
@pytest.mark.p0
@pytest.mark.parametrize("feature_id", P0_FEATURES)
def test_p0_real_negative(feature_id: str, require_real_stack: None) -> None:
    evidence = _run(feature_id, "negative")
    assert evidence["result"] == "PASS"
    assert evidence["anomaly_detected"] is False
