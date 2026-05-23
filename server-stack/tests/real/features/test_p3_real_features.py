"""RI-4 P3 real feature positive/negative replay tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / ".venv" / "bin" / "python"
RUN = ROOT / "simulation" / "real" / "run_real_feature.py"
REPORTS = ROOT / "reports" / "real" / "features"

P3_FEATURES = sorted(
    {"F-009", "F-014", "F-056", "F-070", "F-071", "F-072", "F-073", "F-074", "F-075", "F-076", "F-077", "F-078"},
    key=lambda x: int(x.split("-")[1]),
)


def _run(feature_id: str, mode: str) -> dict:
    subprocess.run([str(PYTHON), str(RUN), "--feature", feature_id, "--mode", mode], cwd=ROOT, check=True)
    return json.loads((REPORTS / f"{feature_id}-{mode}.json").read_text(encoding="utf-8"))


@pytest.mark.real
@pytest.mark.p3
@pytest.mark.parametrize("feature_id", P3_FEATURES)
def test_p3_real_positive(feature_id: str, require_real_stack: None) -> None:
    evidence = _run(feature_id, "positive")
    assert evidence["parity_level"] == "L2"
    assert evidence["result"] == "PASS"
    assert evidence["anomaly_detected"] is True
    assert len(evidence["raw_logs_asserted"]) >= 1


@pytest.mark.real
@pytest.mark.p3
@pytest.mark.parametrize("feature_id", P3_FEATURES)
def test_p3_real_negative(feature_id: str, require_real_stack: None) -> None:
    evidence = _run(feature_id, "negative")
    assert evidence["result"] == "PASS"
    assert evidence["anomaly_detected"] is False
