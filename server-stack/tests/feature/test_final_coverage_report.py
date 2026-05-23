"""Validate final coverage JSON gates after evidence generation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"


@pytest.mark.coverage_gate
def test_feature_coverage_report_gate() -> None:
    subprocess.run(
        [str(PYTHON), "simulation/feature_catalog/report_coverage.py", "--all"],
        cwd=ROOT,
        check=True,
    )
    report = json.loads((ROOT / "reports" / "coverage" / "feature_coverage.json").read_text(encoding="utf-8"))
    assert report["total_features"] == 81
    assert report["implemented"] == 81
    assert report["positive_tests_passed"] == 81
    assert report["negative_tests_passed"] == 81

