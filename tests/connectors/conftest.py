"""Connector test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.daemon.helpers import replay_events_to_jsonl


@pytest.fixture
def f001_jsonl(tmp_path: Path) -> Path:
    return replay_events_to_jsonl("F-001", tmp_path / "f001.jsonl")
