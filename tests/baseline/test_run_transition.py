"""Run mode transition gating by baseline confidence."""

from __future__ import annotations

from tests.baseline.conftest import seed_metric_series


def test_low_confidence_blocks_run_transition(app, tenant_id):
    with app.session() as session:
        engine = session.baseline
        seed_metric_series(
            engine,
            tenant_id=tenant_id,
            metric_name="login_count",
            value=5.0,
            days=3,  # sparse → low confidence
            user_id="sparse-user",
            department_id="hr",
        )
        engine.rebuild_profiles(tenant_id, window_days=45)
        advice = engine.recommend_run_transition(tenant_id)

    assert advice.recommended is False
    assert advice.blocking is True
    assert advice.confidence < engine.run_transition_confidence_threshold


def test_sufficient_confidence_allows_run_transition(app, tenant_id):
    with app.session() as session:
        engine = session.baseline
        for uid in ("u1", "u2", "u3"):
            seed_metric_series(
                engine,
                tenant_id=tenant_id,
                metric_name="login_count",
                value=20.0,
                days=40,
                user_id=uid,
                department_id="hr",
            )
        engine.rebuild_profiles(tenant_id, window_days=45)
        advice = engine.recommend_run_transition(tenant_id)

    assert advice.recommended is True
    assert advice.blocking is False
    assert advice.confidence >= engine.run_transition_confidence_threshold
