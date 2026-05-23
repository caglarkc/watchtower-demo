"""Production readiness test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from watchtower.config.settings import WatchtowerSettings
from watchtower.services.app import create_app


@pytest.fixture
def prod_db(tmp_path: Path) -> Path:
    return tmp_path / "production_test.db"


@pytest.fixture
def prod_settings(prod_db: Path, tmp_path: Path) -> WatchtowerSettings:
    return WatchtowerSettings(
        database_path=prod_db,
        backup_dir=tmp_path / "backups",
        retention_raw_events_days=7,
        retention_normalized_events_days=7,
        retention_audit_days=7,
        retention_llm_audit_days=7,
        llm_provider_chain="mock",
        openai_api_key=None,
        gemini_api_key=None,
    )


@pytest.fixture
def prod_app(prod_settings: WatchtowerSettings):
    return create_app(settings=prod_settings, run_migrations=True)


@pytest.fixture
def bootstrapped_tenant(prod_app):
    with prod_app.session() as session:
        tenant, _ = session.bootstrap_service.bootstrap(
            "admin", "admin@test.local", "test-password"
        )
        session.conn.commit()
        return tenant.id
