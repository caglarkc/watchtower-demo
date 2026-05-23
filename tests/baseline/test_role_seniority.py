"""Manager vs worker role profiles in the same department."""

from __future__ import annotations

from tests.baseline.conftest import seed_metric_series


def test_manager_worker_role_profiles_differ(app, tenant_id):
    with app.session() as session:
        engine = session.baseline
        seed_metric_series(
            engine,
            tenant_id=tenant_id,
            metric_name="admin_action_count",
            value=15.0,
            days=25,
            user_id="worker-a",
            department_id="finance",
            role_id="analyst",
            seniority="worker",
        )
        seed_metric_series(
            engine,
            tenant_id=tenant_id,
            metric_name="admin_action_count",
            value=120.0,
            days=25,
            user_id="manager-a",
            department_id="finance",
            role_id="analyst",
            seniority="manager",
        )
        engine.rebuild_profiles(tenant_id, window_days=45)

        worker_role = session.baseline._repo.get_role_profile(
            tenant_id, "finance", "analyst", "worker"
        )
        manager_role = session.baseline._repo.get_role_profile(
            tenant_id, "finance", "analyst", "manager"
        )

    assert worker_role is not None
    assert manager_role is not None
    w_mean = worker_role.metrics["admin_action_count"].mean
    m_mean = manager_role.metrics["admin_action_count"].mean
    assert m_mean > w_mean * 3
