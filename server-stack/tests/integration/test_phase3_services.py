"""Phase 3 integration: AI, proxy, HR, badge, peripheral mocks."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKIP = os.environ.get("SKIP_DOCKER_STACK", "").lower() in ("1", "true", "yes")

PHASE3_CONTAINERS = [
    "corp-ai-gateway",
    "corp-proxy-sink",
    "corp-cloud-storage",
    "corp-vault",
    "corp-mattermost",
    "corp-cups",
    "corp-badge-api",
    "corp-hris",
    "corp-suitecrm",
    "corp-wiki",
    "corp-dlp",
    "corp-activity-generator",
]


def _exec(name: str, cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "exec", name, *cmd],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.phase3
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_phase3_containers_present() -> None:
    out = subprocess.run(
        ["docker", "compose", "ps", "--format", "{{.Names}}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    if not out.strip():
        pytest.skip("Stack not running")
    for name in PHASE3_CONTAINERS:
        assert name in out


@pytest.mark.phase3
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_ai_gateway_health_and_prompt() -> None:
    r = _exec("corp-ai-gateway", ["curl", "-sf", "http://127.0.0.1:8080/health"])
    assert r.returncode == 0, r.stderr
    r2 = _exec(
        "corp-ai-gateway",
        [
            "curl", "-sf", "-X", "POST", "http://127.0.0.1:8080/v1/prompt",
            "-H", "Content-Type: application/json",
            "-d", '{"prompt":"internal host list","user":"dev1"}',
        ],
    )
    assert r2.returncode == 0, r2.stderr


@pytest.mark.phase3
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_proxy_sink_upload() -> None:
    r = _exec(
        "corp-proxy-sink",
        [
            "curl", "-sf", "-X", "POST", "http://127.0.0.1:8080/upload",
            "-H", "Content-Type: application/json",
            "-d", '{"destination":"personal-cloud","bytes":2100000000}',
        ],
    )
    assert r.returncode == 0, r.stderr


@pytest.mark.phase3
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_badge_and_hris_health() -> None:
    for name in ("corp-badge-api", "corp-hris"):
        r = _exec(name, ["curl", "-sf", "http://127.0.0.1:8080/health"])
        assert r.returncode == 0, f"{name}: {r.stderr}"


@pytest.mark.phase3
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_phase1_phase2_still_running() -> None:
    for name in ("corp-samba-ad", "corp-postgres", "corp-gitea"):
        r = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", name],
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode != 0:
            pytest.skip(f"{name} missing")
        assert r.stdout.strip() == "running"
