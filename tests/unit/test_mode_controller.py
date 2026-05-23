"""Mode controller tests."""

from __future__ import annotations

import pytest

from watchtower.services.bootstrap import BootstrapRequiredError


def _bootstrap(app):
    with app.session() as session:
        tenant, _ = session.bootstrap_service.bootstrap(
            "admin", "admin@test.local", "pw"
        )
        return tenant.id


def test_mode_default_is_learn(app):
    tenant_id = _bootstrap(app)
    with app.session() as session:
        assert session.mode_controller.get_mode(tenant_id) == "learn"
        assert session.mode_controller.default_mode() == "learn"


def test_mode_switch_learn_run_hybrid(app):
    tenant_id = _bootstrap(app)
    with app.session() as session:
        assert session.mode_controller.get_mode(tenant_id) == "learn"
        session.mode_controller.set_mode(tenant_id, "run")
        assert session.mode_controller.get_mode(tenant_id) == "run"
        session.mode_controller.set_mode(tenant_id, "hybrid")
        assert session.mode_controller.get_mode(tenant_id) == "hybrid"


def test_mode_get_requires_bootstrap(app):
    with app.session() as session:
        with pytest.raises(BootstrapRequiredError):
            tenant = session.tenants.create("X", "x")
            session.bootstrap_service.require_bootstrapped(tenant.id)
