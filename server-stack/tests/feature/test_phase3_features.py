"""Phase 3 feature replay and evidence assertions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"
RUN_FEATURE = ROOT / "simulation" / "event_generator" / "run_feature.py"
REPLAY_DIR = ROOT / "simulation" / "feature_replays"
REPORTS = ROOT / "reports" / "features"

PHASE3_IDS = [
    "F-009", "F-012", "F-013", "F-014",
    "F-030", "F-031", "F-032", "F-033", "F-034", "F-035", "F-036",
    "F-042", "F-043", "F-044",
    "F-056", "F-058",
    "F-059", "F-060", "F-061", "F-062", "F-064", "F-065", "F-066",
    "F-067", "F-068", "F-069",
    "F-070", "F-071", "F-072", "F-073", "F-074",
    "F-075", "F-076", "F-077", "F-078",
]


def _run(feature_id: str, mode: str) -> dict:
    cmd = [str(PYTHON), str(RUN_FEATURE), "--feature", feature_id, "--mode", mode]
    subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    path = REPORTS / f"{feature_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.phase3
@pytest.mark.parametrize("feature_id", PHASE3_IDS)
def test_phase3_positive_replay(feature_id: str) -> None:
    assert (REPLAY_DIR / f"{feature_id}_positive.yaml").exists()
    evidence = _run(feature_id, "positive")
    assert evidence["phase"] == 3
    assert evidence["anomaly_detected"] is True
    assert evidence["status"] == "PASS"
    assert evidence["event_count"] >= 1


@pytest.mark.phase3
@pytest.mark.parametrize("feature_id", PHASE3_IDS)
def test_phase3_negative_replay(feature_id: str) -> None:
    assert (REPLAY_DIR / f"{feature_id}_negative.yaml").exists()
    evidence = _run(feature_id, "negative")
    assert evidence["phase"] == 3
    assert evidence["anomaly_detected"] is False
    assert evidence["status"] == "PASS"


@pytest.mark.phase3
def test_phase3_feature_count() -> None:
    assert len(PHASE3_IDS) == 35
