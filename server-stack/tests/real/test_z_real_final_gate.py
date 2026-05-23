"""RI-6 final gate (runs after feature/scenario real tests)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.real
def test_real_final_gate() -> None:
    subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), "simulation/real/report_real_final_gate.py", "--all"],
        cwd=ROOT,
        check=True,
    )
    report = json.loads((ROOT / "reports/real/coverage/real_final_gate.json").read_text(encoding="utf-8"))
    assert report["result"] == "PASS"
    assert report["gates"]["features_81_positive"]
    assert report["gates"]["features_81_negative"]
    assert report["gates"]["features_l2_or_higher"]
    assert report["gates"]["features_l3_min_40"]
    assert report["gates"]["scenarios_83_positive"]
    assert report["gates"]["scenarios_83_negative"]
    assert report["feature_evidence"]["l3_count"] >= 40
    assert report["waivers"] == []
