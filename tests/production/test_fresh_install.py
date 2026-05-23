"""Fresh install: migrations + bootstrap + health."""

from __future__ import annotations

from watchtower.health.service import HealthService


def test_fresh_install_migrations_and_bootstrap(prod_app, prod_db):
    assert prod_db.is_file()
    with prod_app.session() as session:
        tenant, admin = session.bootstrap_service.bootstrap(
            "admin", "admin@install.local", "install-pass"
        )
        assert session.bootstrap_service.is_bootstrapped(tenant.id)
        assert admin.username == "admin"

    svc = HealthService()
    with prod_app.session() as session:
        report = svc.run(
            conn=session.conn,
            settings=prod_app.settings,
            session=session,
        )
    assert report.status in ("healthy", "degraded")
    assert any(c.name == "migrations" and c.status == "healthy" for c in report.checks)
