"""Case timeline and operator workflow on graph-produced alerts."""

from __future__ import annotations

from tests.alerts.helpers import produce_real_alert_via_graph


def test_graph_alert_has_case_and_timeline_created(app, tenant_id):
    alert_id, case_id, _state = produce_real_alert_via_graph(app, tenant_id)
    with app.session() as session:
        alert = session.alerts.get_alert(tenant_id, alert_id)
        case = session.alerts.get_case(tenant_id, case_id)
        timeline = session.alerts.get_timeline(tenant_id, case_id=case_id)
    assert alert is not None
    assert case is not None
    assert case.alert_id == alert_id
    types = [t.event_type for t in timeline]
    assert "created" in types


def test_operator_workflow_timeline_events(app, tenant_id):
    alert_id, case_id, _state = produce_real_alert_via_graph(app, tenant_id)
    with app.session() as session:
        session.alerts.acknowledge(tenant_id, alert_id, actor="op-1")
        session.alerts.assign_case(tenant_id, case_id, "analyst-a", actor="lead")
        session.alerts.add_case_comment(
            tenant_id, case_id, "initial triage", actor="analyst-a"
        )
        session.alerts.link_ticket(
            tenant_id, alert_id, "INC-9001", actor="analyst-a"
        )
        session.conn.commit()
        timeline = session.alerts.get_timeline(tenant_id, case_id=case_id)
    types = [t.event_type for t in timeline]
    assert "acknowledged" in types
    assert "assigned" in types
    assert "comment_added" in types
    assert "ticket_linked" in types


def test_false_positive_feedback_on_timeline(app, tenant_id):
    alert_id, case_id, _state = produce_real_alert_via_graph(app, tenant_id)
    with app.session() as session:
        session.alerts.acknowledge(tenant_id, alert_id)
        session.alerts.close(
            tenant_id, alert_id, "false_positive", actor="mgr-1", comment="benign"
        )
        pending = session.rules._repo.list_pending_rules(tenant_id, status="pending")
        timeline = session.alerts.get_timeline(tenant_id, case_id=case_id)
        session.conn.commit()
    assert len(pending) >= 1
    feedback_events = [t for t in timeline if t.event_type == "feedback_submitted"]
    assert feedback_events
    assert feedback_events[0].metadata.get("pending_rule_id") == pending[0].id
    assert any(t.event_type == "closed" for t in timeline)


def test_alert_show_includes_score_breakdown(app, tenant_id):
    alert_id, _case_id, _state = produce_real_alert_via_graph(app, tenant_id)
    with app.session() as session:
        detail = session.alerts.get_alert_detail(tenant_id, alert_id)
    assert detail is not None
    assert detail.score_breakdown is not None
    assert detail.score_breakdown.get("components")
    assert detail.assessment is not None
    assert detail.source_evidence.get("graph_audit")


def test_export_case_json_and_markdown(app, tenant_id):
    alert_id, case_id, _state = produce_real_alert_via_graph(app, tenant_id)
    with app.session() as session:
        json_body = session.alerts.export_case(tenant_id, case_id, fmt="json")
        md_body = session.alerts.export_case(tenant_id, case_id, fmt="md")
    assert alert_id in json_body
    assert "Score breakdown" in md_body
    assert "Timeline" in md_body
