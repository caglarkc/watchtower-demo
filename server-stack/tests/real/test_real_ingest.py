"""RI-6 real ingest pipeline and final gate tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"


@pytest.mark.real
def test_log_pipeline_health(require_real_stack: None) -> None:
    import urllib.request

    with urllib.request.urlopen("http://172.28.0.16:9201/health", timeout=5) as resp:
        body = json.loads(resp.read().decode())
    assert body["status"] == "ok"
    assert body["elasticsearch"] in ("green", "yellow", "unknown")


@pytest.mark.real
def test_elasticsearch_cluster_health(require_real_stack: None) -> None:
    import urllib.request

    with urllib.request.urlopen("http://172.28.0.17:9200/_cluster/health", timeout=8) as resp:
        body = json.loads(resp.read().decode())
    assert body["status"] in ("green", "yellow")


@pytest.mark.real
def test_real_feature_l3_ingest_after_replay(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-001", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    evidence = json.loads((ROOT / "reports/real/features/F-001-positive.json").read_text(encoding="utf-8"))
    assert evidence["parity_level"] == "L3"
    assert evidence["result"] == "PASS"
    assert evidence["ingest_assertions"][0]["result"] == "PASS"
    assert evidence["ingest_assertions"][0]["index_query"]["count"] >= 1


@pytest.mark.real
def test_ingest_l3_feature_count() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "simulation/real"))
    from config import INGEST_L3_FEATURES  # noqa: WPS433

    assert len(INGEST_L3_FEATURES) >= 40
