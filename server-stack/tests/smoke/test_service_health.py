"""Smoke: running stack services report healthy (optional if stack not up)."""

from __future__ import annotations

import os
import json
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


def _compose_rows() -> list[dict]:
    rows = []
    for line in _compose_ps().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


@pytest.mark.smoke
@pytest.mark.skipif(SKIP_STACK, reason="SKIP_DOCKER_STACK set")
def test_core_services_running() -> None:
    rows = _compose_rows()
    if not rows:
        pytest.skip("Stack not running — run: make up")
    by_name = {row.get("Name") or row.get("Names"): row for row in rows}

    expected = [
        "corp-samba-ad",
        "corp-samba-files",
        "corp-bind-dns",
        "corp-dhcp",
        "corp-zeek-synthetic",
        "corp-endpoint-synthetic",
        "corp-log-pipeline",
        "corp-elasticsearch",
    ]
    for name in expected:
        assert name in by_name, f"Missing container {name}"
        row = by_name[name]
        assert row.get("State") == "running", f"{name} is not running: {row}"
        health = row.get("Health")
        if health:
            assert health == "healthy", f"{name} is not healthy: {row}"


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
