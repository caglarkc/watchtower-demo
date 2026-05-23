"""RI-3 integration — security, proxy, AI, cloud, endpoint behavior."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"
FEATURES_YML = ROOT / "simulation" / "feature_catalog" / "features.yml"

RI3 = (
    {"F-012", "F-013"}
    | {f"F-{i:03d}" for i in range(30, 37)}
    | {"F-042", "F-043", "F-044"}
    | {f"F-{i:03d}" for i in range(58, 63)}
    | {f"F-{i:03d}" for i in range(64, 67)}
    | {f"F-{i:03d}" for i in range(67, 70)}
)


@pytest.fixture(scope="module")
def features_doc() -> dict:
    return yaml.safe_load(FEATURES_YML.read_text(encoding="utf-8"))


@pytest.mark.real
def test_ri3_features_l2_metadata(features_doc: dict) -> None:
    by_id = {f["feature_id"]: f for f in features_doc["features"]}
    for fid in RI3:
        assert by_id[fid]["real_parity_level"] == "L2", fid


@pytest.mark.real
def test_security_seeds_exist() -> None:
    assert (ROOT / "seeds" / "real" / "vault" / "secrets.yml").exists()
    assert (ROOT / "seeds" / "real" / "ai" / "prompts.yml").exists()
    assert (ROOT / "seeds" / "real" / "ai" / "uploads" / "sample.bin").exists()


@pytest.mark.real
def test_endpoint_seeds_exist() -> None:
    assert (ROOT / "seeds" / "real" / "baseline" / "endpoint_roles.yml").exists()


@pytest.mark.real
def test_vault_secret_read_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-013", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    log = ROOT / "logs" / "vault" / "audit.jsonl"
    assert log.exists() and "secret_read" in log.read_text(encoding="utf-8")


@pytest.mark.real
def test_proxy_tunnel_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-069", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    log = ROOT / "logs" / "proxy" / "proxy_sink.jsonl"
    assert log.exists() and "encrypted_tunnel" in log.read_text(encoding="utf-8")


@pytest.mark.real
def test_ai_gateway_prompt_log(require_real_stack: None) -> None:
    subprocess.run(
        [str(PYTHON), "simulation/real/run_real_feature.py", "--feature", "F-030", "--mode", "positive"],
        cwd=ROOT,
        check=True,
    )
    log = ROOT / "logs" / "ai_gateway" / "ai_gateway.jsonl"
    assert log.exists() and "prompt" in log.read_text(encoding="utf-8")
