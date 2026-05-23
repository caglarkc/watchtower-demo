"""Daemon test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.daemon.helpers import replay_events_to_jsonl, register_f001_jsonl_source


@pytest.fixture
def f001_jsonl(tmp_path: Path) -> Path:
    return replay_events_to_jsonl("F-001", tmp_path / "f001.jsonl")


@pytest.fixture
def f001_source(app, tenant_id, f001_jsonl):
    return register_f001_jsonl_source(app, tenant_id, f001_jsonl)
