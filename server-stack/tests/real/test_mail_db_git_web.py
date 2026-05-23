"""RI-2 integration tests — mail, DB, Git, web/API."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"
FEATURES_YML = ROOT / "simulation" / "feature_catalog" / "features.yml"

RI2 = {f"F-{i:03d}" for i in range(16, 30)} | {f"F-{i:03d}" for i in range(45, 55)}


@pytest.fixture(scope="module")
def features_doc() -> dict:
    return yaml.safe_load(FEATURES_YML.read_text(encoding="utf-8"))


@pytest.mark.real
def test_ri2_features_have_l2_metadata(features_doc: dict) -> None:
    by_id = {f["feature_id"]: f for f in features_doc["features"]}
    for fid in RI2:
        assert by_id[fid]["real_parity_level"] == "L2", fid


@pytest.mark.real
def test_mail_seeds_exist() -> None:
    assert (ROOT / "seeds" / "real" / "mail" / "mailboxes.yml").exists()
    assert (ROOT / "seeds" / "real" / "mail" / "attachments" / "sample.pdf").exists()


@pytest.mark.real
def test_app_seeds_exist() -> None:
    assert (ROOT / "seeds" / "real" / "postgres" / "schema.sql").exists()
    assert (ROOT / "seeds" / "real" / "git" / "repos.yml").exists()
    assert (ROOT / "seeds" / "real" / "web" / "endpoints.yml").exists()


@pytest.mark.real
def test_postfix_smtp_action_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-016", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    log = ROOT / "logs" / "postfix" / "postfix.jsonl"
    assert log.exists() and "smtp_send" in log.read_text(encoding="utf-8")


@pytest.mark.real
def test_postgres_pg_audit_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-045", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    audit = ROOT / "logs" / "postgres" / "pg_audit.log"
    assert audit.exists() and "SELECT" in audit.read_text(encoding="utf-8")


@pytest.mark.real
def test_gitea_clone_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-049", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    log = ROOT / "logs" / "gitea" / "gitea-access.jsonl"
    assert log.exists() and "git_clone" in log.read_text(encoding="utf-8")
