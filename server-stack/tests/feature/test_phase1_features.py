"""Phase 1 feature replay and evidence assertions."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"
RUN_FEATURE = ROOT / "simulation" / "event_generator" / "run_feature.py"
REPLAY_DIR = ROOT / "simulation" / "feature_replays"
REPORTS = ROOT / "reports" / "features"


def _run(feature_id: str, mode: str) -> dict:
    cmd = [str(PYTHON), str(RUN_FEATURE), "--feature", feature_id, "--mode", mode]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    evidence_path = REPORTS / f"{feature_id}.json"
    assert evidence_path.exists(), proc.stderr
    return json.loads(evidence_path.read_text(encoding="utf-8"))


@pytest.mark.phase1
@pytest.mark.parametrize("feature_id", [
    "F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007", "F-008",
    "F-010", "F-011", "F-015", "F-037", "F-038", "F-039", "F-040", "F-041",
    "F-055", "F-057", "F-063", "F-079", "F-080", "F-081",
])
def test_phase1_positive_replay(feature_id: str) -> None:
    replay = REPLAY_DIR / f"{feature_id}_positive.yaml"
    assert replay.exists(), f"Missing replay: {replay}"
    evidence = _run(feature_id, "positive")
    assert evidence["feature_id"] == feature_id
    assert evidence["mode"] == "positive"
    assert evidence["anomaly_detected"] is True
    assert evidence["status"] == "PASS"
    assert evidence["event_count"] >= 1


@pytest.mark.phase1
@pytest.mark.parametrize("feature_id", [
    "F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007", "F-008",
    "F-010", "F-011", "F-015", "F-037", "F-038", "F-039", "F-040", "F-041",
    "F-055", "F-057", "F-063", "F-079", "F-080", "F-081",
])
def test_phase1_negative_replay(feature_id: str) -> None:
    replay = REPLAY_DIR / f"{feature_id}_negative.yaml"
    assert replay.exists(), f"Missing replay: {replay}"
    evidence = _run(feature_id, "negative")
    assert evidence["feature_id"] == feature_id
    assert evidence["mode"] == "negative"
    assert evidence["anomaly_detected"] is False
    assert evidence["status"] == "PASS"


@pytest.mark.phase1
def test_phase1_feature_count(phase1_ids: list[str]) -> None:
    assert len(phase1_ids) == 22
