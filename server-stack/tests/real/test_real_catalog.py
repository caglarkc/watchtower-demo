"""RI-0 real parity catalog integrity — 81 feature metadata."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
FEATURES_YML = ROOT / "simulation" / "feature_catalog" / "features.yml"
SEEDS_REAL = ROOT / "seeds" / "real"

REQUIRED_REAL_FIELDS = (
    "real_parity_level",
    "real_tool",
    "real_action_command",
    "raw_log_assertion",
    "ingest_assertion",
)

VALID_LEVELS = {"L0", "L1", "L2", "L3"}


@pytest.fixture(scope="module")
def features_doc() -> dict:
    return yaml.safe_load(FEATURES_YML.read_text(encoding="utf-8"))


@pytest.mark.real
def test_feature_count_is_81(features_doc: dict) -> None:
    assert features_doc["total_features"] == 81
    assert len(features_doc["features"]) == 81


@pytest.mark.real
@pytest.mark.parametrize(
    "field",
    REQUIRED_REAL_FIELDS,
)
def test_all_features_have_real_field(features_doc: dict, field: str) -> None:
    for feat in features_doc["features"]:
        fid = feat["feature_id"]
        assert feat.get(field), f"{fid}: missing {field}"


RI1 = {
    "F-001", "F-002", "F-003", "F-005", "F-006", "F-007", "F-008",
    "F-010", "F-011", "F-015", "F-037", "F-038", "F-039", "F-040", "F-041",
    "F-055", "F-057", "F-063", "F-079", "F-080", "F-081",
}
RI2 = {f"F-{i:03d}" for i in range(16, 30)} | {f"F-{i:03d}" for i in range(45, 55)}
RI3 = (
    {"F-012", "F-013"}
    | {f"F-{i:03d}" for i in range(30, 37)}
    | {"F-042", "F-043", "F-044"}
    | {f"F-{i:03d}" for i in range(58, 63)}
    | {f"F-{i:03d}" for i in range(64, 67)}
    | {f"F-{i:03d}" for i in range(67, 70)}
)


@pytest.mark.real
def test_real_parity_levels_are_valid(features_doc: dict) -> None:
    for feat in features_doc["features"]:
        fid = feat["feature_id"]
        level = feat["real_parity_level"]
        target = feat.get("real_parity_target", "L2")
        assert level in VALID_LEVELS, fid
        assert target in VALID_LEVELS, fid
        if fid in RI1 or fid in RI2 or fid in RI3:
            assert level == "L2", fid


@pytest.mark.real
def test_real_action_commands_use_make_real_feature(features_doc: dict) -> None:
    for feat in features_doc["features"]:
        fid = feat["feature_id"]
        assert f"make real-feature FEATURE={fid}" in feat["real_action_command"]
        assert feat.get("real_negative_command"), fid
        assert f"make real-feature-negative FEATURE={fid}" in feat["real_negative_command"]


@pytest.mark.real
def test_real_evidence_paths_under_reports_real(features_doc: dict) -> None:
    for feat in features_doc["features"]:
        fid = feat["feature_id"]
        assert feat["real_evidence_positive"] == f"reports/real/features/{fid}-positive.json"
        assert feat["real_evidence_negative"] == f"reports/real/features/{fid}-negative.json"


@pytest.mark.real
def test_reports_real_directory_layout() -> None:
    for sub in ("features", "scenarios", "coverage", "logs"):
        assert (ROOT / "reports" / "real" / sub).is_dir(), sub


@pytest.mark.real
def test_seed_real_directory_exists() -> None:
    if not SEEDS_REAL.is_dir():
        subprocess.run(
            [str(ROOT / ".venv" / "bin" / "python"), "simulation/real/seed_real_all.py"],
            cwd=ROOT,
            check=True,
        )
    assert SEEDS_REAL.is_dir()
    assert (SEEDS_REAL / "identity").is_dir()
    assert (SEEDS_REAL / "baseline").is_dir()
