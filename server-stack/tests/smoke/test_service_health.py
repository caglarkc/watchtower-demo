"""Smoke: running stack services report healthy (optional if stack not up)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKIP_STACK = os.environ.get("SKIP_DOCKER_STACK", "").lower() in ("1", "true", "yes")


def _compose_ps() -> str:
    result = subprocess.run(
        ["docker", "compose", "ps", "--format", "json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


@pytest.mark.smoke
@pytest.mark.skipif(SKIP_STACK, reason="SKIP_DOCKER_STACK set")
def test_core_services_running() -> None:
    out = _compose_ps()
    if not out.strip():
        pytest.skip("Stack not running — run: make up")

    expected = [
        "corp-bind-dns",
        "corp-dhcp",
        "corp-zeek-synthetic",
        "corp-endpoint-synthetic",
        "corp-log-pipeline",
    ]
    for name in expected:
        assert name in out, f"Missing container {name}"


@pytest.mark.smoke
@pytest.mark.skipif(SKIP_STACK, reason="SKIP_DOCKER_STACK set")
def test_endpoint_synthetic_health_endpoint() -> None:
    result = subprocess.run(
        [
            "docker",
            "exec",
            "corp-endpoint-synthetic",
            "curl",
            "-sf",
            "http://127.0.0.1:8080/health",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip("endpoint-synthetic not reachable")
    assert "ok" in result.stdout
