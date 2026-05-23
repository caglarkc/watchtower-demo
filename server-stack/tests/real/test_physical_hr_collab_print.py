"""RI-4 integration — physical, HR, collaboration, print, CRM."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"
FEATURES_YML = ROOT / "simulation" / "feature_catalog" / "features.yml"

RI4 = {"F-009", "F-014", "F-056", "F-070", "F-071", "F-072", "F-073", "F-074", "F-075", "F-076", "F-077", "F-078"}


@pytest.fixture(scope="module")
def features_doc() -> dict:
    return yaml.safe_load(FEATURES_YML.read_text(encoding="utf-8"))


@pytest.mark.real
def test_ri4_features_l2_metadata(features_doc: dict) -> None:
    by_id = {f["feature_id"]: f for f in features_doc["features"]}
    for fid in RI4:
        assert by_id[fid]["real_parity_level"] == "L2", fid


@pytest.mark.real
def test_physical_hr_seeds_exist() -> None:
    assert (ROOT / "seeds" / "real" / "hris" / "employees.yml").exists()
    assert (ROOT / "seeds" / "real" / "badge" / "locations.yml").exists()
    assert (ROOT / "seeds" / "real" / "print" / "confidential-report.pdf").exists()
    assert (ROOT / "seeds" / "real" / "crm" / "records.yml").exists()


@pytest.mark.real
def test_badge_concurrent_session_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-009", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    log = ROOT / "logs" / "badge" / "badge.jsonl"
    assert log.exists() and "concurrent_session" in log.read_text(encoding="utf-8")


@pytest.mark.real
def test_hris_offboarding_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-072", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    log = ROOT / "logs" / "hris" / "hris.jsonl"
    assert log.exists() and "offboarding_activity" in log.read_text(encoding="utf-8")


@pytest.mark.real
def test_cups_print_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-056", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    log = ROOT / "logs" / "cups" / "print.jsonl"
    assert log.exists() and "print_sensitive_correlation" in log.read_text(encoding="utf-8")


@pytest.mark.real
def test_suitecrm_record_chain_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-073", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    log = ROOT / "logs" / "suitecrm" / "crm.jsonl"
    assert log.exists() and "multi_user_record_chain" in log.read_text(encoding="utf-8")
