"""Shared fixtures for real integration tests."""

from __future__ import annotations

import subprocess
import urllib.error
import urllib.request

import pytest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]

SERVICE_URLS = [
    "http://172.28.0.10:8080/health",
    "http://172.28.0.14:8080/health",
    "http://172.28.0.15:8080/health",
    "http://172.28.0.42:8080/health",
    "http://172.28.0.43:8080/health",
    "http://172.28.0.20:8080/health",
    "http://172.28.0.21:8080/health",
    "http://172.28.0.22:8080/health",
    "http://172.28.0.44:8080/health",
    "http://172.28.0.45:8080/health",
    "http://172.28.0.26:8080/health",
    "http://172.28.0.28:8080/health",
]


def _reachable(url: str, timeout: float = 3.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


@pytest.fixture(scope="session")
def real_stack_available() -> bool:
    return all(_reachable(u) for u in SERVICE_URLS)


@pytest.fixture(scope="session")
def require_real_stack(real_stack_available: bool) -> None:
    if not real_stack_available:
        pytest.skip("Real stack not reachable — run: make real-up")


@pytest.fixture(scope="session", autouse=False)
def seed_real_data() -> None:
    subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), "simulation/real/seed_real_identity.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), "simulation/real/seed_real_files.py"],
        cwd=ROOT,
        check=True,
    )
