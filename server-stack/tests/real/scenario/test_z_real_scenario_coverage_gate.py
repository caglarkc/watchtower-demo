"""RI-5 real scenario coverage gate (runs after replay tests)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.real
def test_real_scenario_coverage_gate() -> None:
    subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), "simulation/real/report_real_scenario_coverage.py", "--all"],
        cwd=ROOT,
        check=True,
    )
    report = json.loads(
        (ROOT / "reports" / "real" / "coverage" / "real_scenario_coverage.json").read_text(encoding="utf-8")
    )
    assert report["total_scenarios"] == 83
    assert report["positive_replays_passed"] == 83
    assert report["negative_replays_passed"] == 83
    assert report["waivers"] == []
