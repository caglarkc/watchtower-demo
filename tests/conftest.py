"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from watchtower.config.settings import WatchtowerSettings
from watchtower.services.app import AppContext, create_app


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "watchtower_test.db"


@pytest.fixture
def settings(db_path: Path) -> WatchtowerSettings:
    return WatchtowerSettings(
        database_path=db_path,
        graph_checkpoint_path=db_path.parent / "graph_checkpoints.db",
        graph_checkpoint_enabled=True,
        graph_checkpoint_use_memory=False,
    )


@pytest.fixture
def app(settings: WatchtowerSettings) -> AppContext:
    return create_app(settings=settings, run_migrations=True)


@pytest.fixture
def tenant_id(app: AppContext) -> str:
    with app.session() as session:
        tenant, _ = session.bootstrap_service.bootstrap(
            "admin", "admin@test.local", "test-password"
        )
        return tenant.id
