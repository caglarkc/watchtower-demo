"""Validate scenario coverage JSON gate after replay tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"


@pytest.mark.coverage_gate
def test_scenario_coverage_report_gate() -> None:
    subprocess.run(
        [str(PYTHON), "simulation/scenarios/report_scenario_coverage.py", "--all"],
        cwd=ROOT,
        check=True,
    )
    report = json.loads((ROOT / "reports" / "coverage" / "scenario_coverage.json").read_text(encoding="utf-8"))
    assert report["total_scenarios"] == 83
    assert report["implemented"] == 83
    assert report["positive_replays_passed"] == 83
    assert report["negative_replays_passed"] == 83
