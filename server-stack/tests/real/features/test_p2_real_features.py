"""RI-3 P2 real feature positive/negative replay tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / ".venv" / "bin" / "python"
RUN = ROOT / "simulation" / "real" / "run_real_feature.py"
REPORTS = ROOT / "reports" / "real" / "features"

P2_FEATURES = sorted(
    {"F-012", "F-013"}
    | {f"F-{i:03d}" for i in range(30, 37)}
    | {"F-042", "F-043", "F-044"}
    | {f"F-{i:03d}" for i in range(58, 63)}
    | {f"F-{i:03d}" for i in range(64, 67)}
    | {f"F-{i:03d}" for i in range(67, 70)},
    key=lambda x: int(x.split("-")[1]),
)


def _run(feature_id: str, mode: str) -> dict:
    subprocess.run([str(PYTHON), str(RUN), "--feature", feature_id, "--mode", mode], cwd=ROOT, check=True)
    return json.loads((REPORTS / f"{feature_id}-{mode}.json").read_text(encoding="utf-8"))


@pytest.mark.real
@pytest.mark.p2
@pytest.mark.parametrize("feature_id", P2_FEATURES)
def test_p2_real_positive(feature_id: str, require_real_stack: None) -> None:
    evidence = _run(feature_id, "positive")
    assert evidence["parity_level"] == "L2"
    assert evidence["result"] == "PASS"
    assert evidence["anomaly_detected"] is True
    assert len(evidence["raw_logs_asserted"]) >= 1


@pytest.mark.real
@pytest.mark.p2
@pytest.mark.parametrize("feature_id", P2_FEATURES)
def test_p2_real_negative(feature_id: str, require_real_stack: None) -> None:
    evidence = _run(feature_id, "negative")
    assert evidence["result"] == "PASS"
    assert evidence["anomaly_detected"] is False
