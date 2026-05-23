"""User-specific baseline must not be overridden by department average."""

from __future__ import annotations

from tests.baseline.conftest import seed_metric_series


def test_user_high_volume_stays_normal_despite_low_department_average(app, tenant_id):
    """Mehmet 1000 vs dept ~100 — 1000 is normal for Mehmet, anomalous for Yiğit."""
    with app.session() as session:
        engine = session.baseline
        # Department: many workers around 100
        for user in ("worker1", "worker2", "worker3", "yigit"):
            seed_metric_series(
                engine,
                tenant_id=tenant_id,
                metric_name="sql_query_count",
                value=100.0,
                days=30,
                user_id=user,
                department_id="backend",
                role_id="engineer",
                seniority="worker",
            )
        # Mehmet high volume
        seed_metric_series(
            engine,
            tenant_id=tenant_id,
            metric_name="sql_query_count",
            value=1000.0,
            days=30,
            user_id="mehmet",
            department_id="backend",
            role_id="engineer",
            seniority="worker",
            daily_jitter=20.0,
        )
        engine.rebuild_profiles(tenant_id, window_days=45)

        mehmet_eval = engine.evaluate(
            tenant_id,
            "sql_query_count",
            1000.0,
            user_id="mehmet",
            department_id="backend",
            role_id="engineer",
        )
        yigit_eval = engine.evaluate(
            tenant_id,
            "sql_query_count",
            1000.0,
            user_id="yigit",
            department_id="backend",
            role_id="engineer",
        )
        dept_only = engine.evaluate(
            tenant_id,
            "sql_query_count",
            1000.0,
            department_id="backend",
        )

    assert mehmet_eval.used_user_baseline is True
    assert mehmet_eval.is_normal is True
    assert mehmet_eval.source == "user"

    assert yigit_eval.used_user_baseline is True
    assert yigit_eval.is_normal is False

    assert dept_only.source == "department"
    assert dept_only.is_normal is False
