"""Daily/weekly/monthly snapshot generation."""

from __future__ import annotations

from tests.baseline.conftest import seed_metric_series


def test_daily_weekly_monthly_snapshots(app, tenant_id):
    with app.session() as session:
        engine = session.baseline
        seed_metric_series(
            engine,
            tenant_id=tenant_id,
            metric_name="bytes_read",
            value=500.0,
            days=35,
            user_id="snap-user",
            department_id="infra",
        )
        engine.rebuild_profiles(tenant_id)
        snaps = engine.compute_snapshots(tenant_id)
        periods = {s.period for s in snaps if s.profile_key == "snap-user"}

    assert "daily" in periods
    assert "weekly" in periods
    assert "monthly" in periods
