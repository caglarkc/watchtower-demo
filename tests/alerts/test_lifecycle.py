"""Alert lifecycle and suppression tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from watchtower.alerts.service import AlertLifecycleError


def _create_alert(session, tenant_id: str):
    return session.alerts.create_alert(
        tenant_id,
        feature_id="F-001",
        severity="ALERT",
        title="SQL spike",
        user_id="mehmet",
        department_id="backend",
        resource="HR-DB-01",
        action="sql_query",
    )


def test_open_to_investigating_to_true_positive(app, tenant_id):
    with app.session() as session:
        alert, _ = _create_alert(session, tenant_id)
        assert alert.status == "open"
        investigating = session.alerts.acknowledge(tenant_id, alert.id)
        assert investigating.status == "investigating"
        closed = session.alerts.close(
            tenant_id, alert.id, "true_positive", actor="sec-1"
        )
        assert closed.status == "true_positive"


def test_false_positive_creates_pending_rule(app, tenant_id):
    with app.session() as session:
        alert, _ = _create_alert(session, tenant_id)
        session.alerts.acknowledge(tenant_id, alert.id)
        session.alerts.close(tenant_id, alert.id, "false_positive", actor="mgr-1")
        pending = session.rules._repo.list_pending_rules(tenant_id, status="pending")
    assert len(pending) >= 1
    assert pending[0].scope.user_id == "mehmet"


def test_suppress_duration_expiry(app, tenant_id):
    with app.session() as session:
        alert, _ = _create_alert(session, tenant_id)
        session.alerts.suppress(tenant_id, alert.id, "1m", actor="op")
        assert session.alerts.is_suppressed(tenant_id, alert.id) is True
        # Force expiry
        windows = session.alerts._repo.list_active_suppressions(
            tenant_id, as_of=datetime.now(UTC) + timedelta(minutes=2)
        )
        assert len(windows) == 0
        session.alerts.expire_suppressions(tenant_id)
        assert session.alerts.is_suppressed(tenant_id, alert.id) is False


def test_invalid_transition_rejected(app, tenant_id):
    with app.session() as session:
        alert, _ = _create_alert(session, tenant_id)
        session.alerts.acknowledge(tenant_id, alert.id)
        session.alerts.close(tenant_id, alert.id, "true_positive")
        with pytest.raises(AlertLifecycleError):
            session.alerts.acknowledge(tenant_id, alert.id)
