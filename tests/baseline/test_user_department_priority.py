"""User-specific baseline must not be overridden by department average."""

from __future__ import annotations

from tests.baseline.conftest import seed_metric_series


def test_user_high_volume_stays_normal_despite_low_department_average(app, tenant_id):
    """Mehmet ~1000 vs dept ~100 — user profile keeps high band; dept does not shrink it."""
    with app.session() as session:
        engine = session.baseline
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

        mehmet_prof = session.baseline._repo.get_user_profile(tenant_id, "mehmet")
        dept_prof = session.baseline._repo.get_department_profile(tenant_id, "backend")

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

    assert mehmet_prof is not None and dept_prof is not None
    mehmet_mean = mehmet_prof.metrics["sql_query_count"].mean
    dept_mean = dept_prof.metrics["sql_query_count"].mean
    assert mehmet_mean > dept_mean * 2

    assert mehmet_eval.used_user_baseline is True
    assert mehmet_eval.is_normal is True
    assert mehmet_eval.source == "user"

    assert yigit_eval.used_user_baseline is True
    assert yigit_eval.is_normal is False
