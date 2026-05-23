"""Faz 4 final coverage gate — 81 features × 2 modes."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"
FEATURES_YML = ROOT / "simulation" / "feature_catalog" / "features.yml"
REPORTS = ROOT / "reports" / "features"


def _feature_ids() -> list[str]:
    doc = yaml.safe_load(FEATURES_YML.read_text(encoding="utf-8"))
    return [f["feature_id"] for f in doc["features"]]


@pytest.mark.coverage_gate
def test_feature_catalog_has_81_entries() -> None:
    assert len(_feature_ids()) == 81


@pytest.mark.coverage_gate
@pytest.mark.parametrize("feature_id", _feature_ids())
def test_feature_positive_evidence_file(feature_id: str) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/event_generator/run_feature.py", "--feature", feature_id, "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    path = REPORTS / f"{feature_id}-positive.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["anomaly_detected"] is True


@pytest.mark.coverage_gate
@pytest.mark.parametrize("feature_id", _feature_ids())
def test_feature_negative_evidence_file(feature_id: str) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/event_generator/run_feature.py", "--feature", feature_id, "--mode", "negative"],
        cwd=ROOT,
        check=True,
    )
    path = REPORTS / f"{feature_id}-negative.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["anomaly_detected"] is False
