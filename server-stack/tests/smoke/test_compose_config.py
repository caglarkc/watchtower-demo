"""Smoke: docker compose config validates."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.smoke
def test_compose_config_exits_zero() -> None:
    result = subprocess.run(
        ["docker", "compose", "config"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


@pytest.mark.smoke
def test_compose_defines_corp_lan_network() -> None:
    result = subprocess.run(
        ["docker", "compose", "config"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "corp-lan" in result.stdout
    assert "172.28.0.0/24" in result.stdout or "172.28.0.0" in result.stdout
