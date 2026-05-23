"""Bootstrap admin requirement tests."""

from __future__ import annotations

import pytest

from watchtower.services.bootstrap import BootstrapRequiredError


def test_bootstrap_admin_required_for_protected_flow(app):
    with app.session() as session:
        tenant = session.bootstrap_service.get_default_tenant()
        assert tenant is None

        with pytest.raises(BootstrapRequiredError):
            session.bootstrap_service.require_bootstrapped("missing-tenant-id")


def test_bootstrap_creates_admin_and_default_mode_learn(app):
    with app.session() as session:
        tenant, admin = session.bootstrap_service.bootstrap(
            "sysadmin",
            "admin@corp.local",
            "secure-password-1",
        )
        assert session.bootstrap_service.is_bootstrapped(tenant.id)
        assert admin.username == "sysadmin"
        assert session.mode_controller.get_mode(tenant.id) == "learn"


def test_bootstrap_is_idempotent_guard(app):
    with app.session() as session:
        session.bootstrap_service.bootstrap("admin", "a@b.c", "pw-1")
        with pytest.raises(ValueError, match="already bootstrapped"):
            session.bootstrap_service.bootstrap("admin2", "b@c.d", "pw-2")
