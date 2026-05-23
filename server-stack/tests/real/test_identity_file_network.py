"""RI-1 integration tests — identity, file, DNS, DHCP, network."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"
FEATURES_YML = ROOT / "simulation" / "feature_catalog" / "features.yml"
RI1 = {
    "F-001", "F-002", "F-003", "F-005", "F-006", "F-007", "F-008",
    "F-010", "F-011", "F-015", "F-037", "F-038", "F-039", "F-040", "F-041",
    "F-055", "F-057", "F-063", "F-079", "F-080", "F-081",
}


@pytest.fixture(scope="module")
def features_doc() -> dict:
    return yaml.safe_load(FEATURES_YML.read_text(encoding="utf-8"))


@pytest.mark.real
def test_ri1_features_have_l2_metadata(features_doc: dict) -> None:
    by_id = {f["feature_id"]: f for f in features_doc["features"]}
    for fid in sorted(RI1, key=lambda x: int(x.split("-")[1])):
        feat = by_id[fid]
        assert feat["real_parity_level"] == "L2", fid
        assert feat.get("real_tool")
        assert "make real-feature" in feat["real_action_command"]


@pytest.mark.real
def test_seed_identity_and_files_exist(seed_real_data: None) -> None:
    assert (ROOT / "seeds" / "real" / "identity" / "users.csv").exists()
    assert (ROOT / "seeds" / "real" / "files" / "finance").is_dir()
    assert (ROOT / "seeds" / "real" / "baseline" / "normal_day.yml").exists()


@pytest.mark.real
def test_samba_ad_action_writes_log(require_real_stack: None) -> None:
    import urllib.request

    data = json.dumps({"user": "testuser", "count": 3}).encode()
    req = urllib.request.Request(
        "http://172.28.0.10:8080/action/auth-fail-burst",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200
    log = ROOT / "logs" / "identity" / "ad_events.jsonl"
    assert log.exists() and "4625" in log.read_text(encoding="utf-8")


@pytest.mark.real
def test_bind_query_log_path(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-003", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    qlog = ROOT / "logs" / "dns" / "query.log"
    assert qlog.exists() and qlog.stat().st_size > 0


@pytest.mark.real
def test_samba_files_audit_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-038", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    audit = ROOT / "logs" / "samba" / "audit.log"
    assert audit.exists() and "read" in audit.read_text(encoding="utf-8")


@pytest.mark.real
def test_zeek_conn_log_after_f002(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-002", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    conn = ROOT / "logs" / "zeek" / "conn.log"
    assert conn.exists()
    lines = [ln for ln in conn.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) >= 3
