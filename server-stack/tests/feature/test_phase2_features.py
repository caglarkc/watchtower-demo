"""Phase 2 feature replay and evidence assertions."""

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

PHASE2_IDS = [
    "F-016", "F-017", "F-018", "F-019", "F-020", "F-021", "F-022", "F-023",
    "F-024", "F-025", "F-026", "F-027", "F-028", "F-029",
    "F-045", "F-046", "F-047", "F-048", "F-049", "F-050", "F-051", "F-052",
    "F-053", "F-054",
]


def _run(feature_id: str, mode: str) -> dict:
    cmd = [str(PYTHON), str(RUN_FEATURE), "--feature", feature_id, "--mode", mode]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    evidence_path = REPORTS / f"{feature_id}.json"
    assert evidence_path.exists(), proc.stderr
    return json.loads(evidence_path.read_text(encoding="utf-8"))


@pytest.mark.phase2
@pytest.mark.parametrize("feature_id", PHASE2_IDS)
def test_phase2_positive_replay(feature_id: str) -> None:
    assert (REPLAY_DIR / f"{feature_id}_positive.yaml").exists()
    evidence = _run(feature_id, "positive")
    assert evidence["phase"] == 2
    assert evidence["anomaly_detected"] is True
    assert evidence["status"] == "PASS"


@pytest.mark.phase2
@pytest.mark.parametrize("feature_id", PHASE2_IDS)
def test_phase2_negative_replay(feature_id: str) -> None:
    assert (REPLAY_DIR / f"{feature_id}_negative.yaml").exists()
    evidence = _run(feature_id, "negative")
    assert evidence["phase"] == 2
    assert evidence["anomaly_detected"] is False
    assert evidence["status"] == "PASS"


@pytest.mark.phase2
def test_phase2_feature_count() -> None:
    assert len(PHASE2_IDS) == 24
