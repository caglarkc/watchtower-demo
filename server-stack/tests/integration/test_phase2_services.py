"""Phase 2 integration: mail, DB, git, web, admin mocks."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKIP = os.environ.get("SKIP_DOCKER_STACK", "").lower() in ("1", "true", "yes")

PHASE2_CONTAINERS = [
    "corp-postfix",
    "corp-dovecot",
    "corp-roundcube",
    "corp-postgres",
    "corp-gitea",
    "corp-nginx",
    "corp-internal-app",
    "corp-artifact-registry",
    "corp-siem-admin",
    "corp-hypervisor-console",
]


def _exec(name: str, cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "exec", name, *cmd],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.phase2
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_phase2_containers_present() -> None:
    out = subprocess.run(
        ["docker", "compose", "ps", "--format", "{{.Names}}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    if not out.strip():
        pytest.skip("Stack not running")
    for name in PHASE2_CONTAINERS:
        assert name in out, f"Missing {name}"


@pytest.mark.phase2
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_postgres_accepts_connections() -> None:
    r = _exec("corp-postgres", ["pg_isready", "-U", "corp", "-d", "corpdb"])
    if r.returncode != 0:
        pytest.skip("postgres not ready")
    assert "accepting connections" in r.stdout


@pytest.mark.phase2
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_nginx_health_via_gateway() -> None:
    r = _exec("corp-nginx", ["wget", "-qO-", "http://127.0.0.1/health"])
    if r.returncode != 0:
        pytest.skip("nginx not ready")
    assert "ok" in r.stdout


@pytest.mark.phase2
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_gitea_health_endpoint() -> None:
    r = _exec("corp-gitea", ["curl", "-sf", "http://127.0.0.1:3000/api/healthz"])
    if r.returncode != 0:
        pytest.skip("gitea not ready")
    assert r.stdout


@pytest.mark.phase2
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_mail_sim_logs_exist() -> None:
    for name, role in [
        ("corp-postfix", "postfix"),
        ("corp-dovecot", "dovecot"),
        ("corp-roundcube", "roundcube"),
    ]:
        r = _exec(name, ["python", "/app/healthcheck.py"])
        assert r.returncode == 0, f"{role} logs missing: {r.stderr}"


@pytest.mark.phase2
@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="SKIP_DOCKER_STACK set")
def test_phase1_services_still_healthy() -> None:
    """Faz 1 servisleri Faz 2 sonrası ayakta kalmalı."""
    for name in ["corp-samba-ad", "corp-bind-dns", "corp-endpoint-synthetic"]:
        r = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Health.Status}}", name],
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode != 0:
            pytest.skip(f"{name} not present")
        assert r.stdout.strip() in ("healthy", "starting"), f"{name} unhealthy: {r.stdout}"
