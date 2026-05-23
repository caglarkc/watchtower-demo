"""Health check aggregation."""

from __future__ import annotations

from watchtower.health.service import HealthService


def test_health_report_after_bootstrap(prod_app, bootstrapped_tenant):
    svc = HealthService()
    with prod_app.session() as session:
        report = svc.run(
            conn=session.conn,
            settings=prod_app.settings,
            session=session,
        )
    assert report.version
    names = {c.name for c in report.checks}
    assert "database" in names
    assert "migrations" in names
    assert "bootstrap" in names
    assert "metrics" in names
