"""CI-friendly short soak: repeated health checks."""

from __future__ import annotations

from watchtower.health.service import HealthService


def test_short_soak_health_iterations(prod_app, bootstrapped_tenant):
    svc = HealthService()
    iterations = 5
    for _ in range(iterations):
        with prod_app.session() as session:
            report = svc.run(
                conn=session.conn,
                settings=prod_app.settings,
                session=session,
            )
        assert report.status in ("healthy", "degraded")
