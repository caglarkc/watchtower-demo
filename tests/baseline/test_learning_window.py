"""45-day learning window and configurable duration."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from tests.baseline.conftest import seed_metric_series


def test_45_day_replay_produces_baseline(app, tenant_id):
    end = datetime(2026, 5, 23, 12, 0, 0, tzinfo=UTC)
    with app.session() as session:
        engine = session.baseline
        seed_metric_series(
            engine,
            tenant_id=tenant_id,
            metric_name="sql_query_count",
            value=50.0,
            days=45,
            user_id="alice",
            department_id="backend",
            end=end,
        )
        lw = engine.rebuild_profiles(tenant_id, as_of=end, window_days=45)
        profile = session.baseline._repo.get_user_profile(tenant_id, "alice")
        snapshots = engine.compute_snapshots(tenant_id)
        snap_count = session.baseline._repo.count_snapshots(tenant_id)

    assert lw.window_days == 45
    assert lw.observation_count == 45
    assert profile is not None
    assert "sql_query_count" in profile.metrics
    assert profile.metrics["sql_query_count"].sample_count == 45
    assert profile.confidence > 0.5
    assert len(snapshots) >= 1
    assert snap_count >= 1


def test_configurable_learning_duration(app, tenant_id):
    end = datetime(2026, 5, 23, 12, 0, 0, tzinfo=UTC)
    with app.session() as session:
        engine = session.baseline
        # 30 days of history but only 7-day window
        seed_metric_series(
            engine,
            tenant_id=tenant_id,
            metric_name="event_volume",
            value=10.0,
            days=30,
            user_id="bob",
            department_id="ops",
            end=end,
        )
        lw = engine.rebuild_profiles(
            tenant_id, as_of=end, window_days=7
        )
        profile = session.baseline._repo.get_user_profile(tenant_id, "bob")

    assert lw.window_days == 7
    assert profile is not None
    assert profile.window_days == 7
    assert profile.metrics["event_volume"].sample_count == 7
