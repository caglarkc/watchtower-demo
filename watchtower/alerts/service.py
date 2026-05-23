"""Alert lifecycle and suppression service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from watchtower.domain.alerts import (
    TERMINAL_STATUSES,
    VALID_TRANSITIONS,
    Alert,
    AlertCase,
    AlertDetailView,
    AlertLifecycleEvent,
    AlertStatus,
    CaseTimelineEntry,
    CaseTimelineEventType,
    SuppressionWindow,
)
from watchtower.domain.rules import RuleScope
from watchtower.alerts.duration import parse_duration
from watchtower.alerts.explain import explain_alert
from watchtower.alerts.export import export_case_json, export_case_markdown
from watchtower.alerts.timeline import CaseTimelineRecorder
from watchtower.feedback.service import FeedbackService
from watchtower.llm.gateway import LLMGateway
from watchtower.storage.repositories.alerts import AlertRepository

CloseOutcome = Literal["true_positive", "false_positive"]


class AlertLifecycleError(Exception):
    """Invalid lifecycle transition."""


class AlertService:
    def __init__(
        self,
        repo: AlertRepository,
        feedback: FeedbackService | None = None,
        llm: LLMGateway | None = None,
    ) -> None:
        self._repo = repo
        self._feedback = feedback
        self._llm = llm
        self._timeline = CaseTimelineRecorder(repo)

    def create_alert(
        self,
        tenant_id: str,
        *,
        feature_id: str,
        severity: str,
        title: str,
        summary: str | None = None,
        user_id: str | None = None,
        department_id: str | None = None,
        resource: str | None = None,
        action: str | None = None,
        graph_run_id: str | None = None,
        run_id: str | None = None,
        candidate_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> tuple[Alert, AlertCase]:
        now = datetime.now(UTC)
        alert_id = self._repo.new_id()
        case_id = self._repo.new_id()
        alert = Alert(
            id=alert_id,
            tenant_id=tenant_id,
            feature_id=feature_id,
            severity=severity,
            status="open",
            title=title,
            summary=summary,
            user_id=user_id,
            department_id=department_id,
            resource=resource,
            action=action,
            graph_run_id=graph_run_id,
            payload=payload or {},
            created_at=now,
            updated_at=now,
        )
        resolved_run_id = run_id or graph_run_id or self._repo.new_id()
        self._repo.ensure_graph_run(tenant_id, resolved_run_id)
        case = AlertCase(
            id=case_id,
            tenant_id=tenant_id,
            alert_id=alert_id,
            status="open",
            run_id=resolved_run_id,
            candidate_id=candidate_id,
            payload={
                "feature_id": feature_id,
                "severity": severity,
                **(payload or {}),
            },
            created_at=now,
            updated_at=now,
        )
        self._repo.insert_alert(alert)
        self._repo.insert_case(case)
        self._record_event(
            tenant_id,
            alert_id,
            case_id,
            None,
            "open",
            actor="system",
            comment="alert created",
        )
        self._timeline.record(
            tenant_id,
            alert_id,
            case_id,
            "created",
            actor="system",
            comment="alert and case created",
            metadata={"graph_run_id": resolved_run_id, "candidate_id": candidate_id},
        )
        return alert, case

    def get_alert(self, tenant_id: str, alert_id: str) -> Alert | None:
        return self._repo.get_alert(tenant_id, alert_id)

    def list_alerts(self, tenant_id: str, **kwargs: Any) -> list[Alert]:
        return self._repo.list_alerts(tenant_id, **kwargs)

    def acknowledge(
        self,
        tenant_id: str,
        alert_id: str,
        *,
        actor: str = "operator",
    ) -> Alert:
        alert = self._transition(
            tenant_id, alert_id, "investigating", actor=actor, comment=None
        )
        case = self._repo.get_case_by_alert(tenant_id, alert_id)
        self._timeline.record(
            tenant_id,
            alert_id,
            case.id if case else None,
            "acknowledged",
            actor=actor,
        )
        return alert

    def close(
        self,
        tenant_id: str,
        alert_id: str,
        outcome: CloseOutcome,
        *,
        actor: str = "operator",
        comment: str | None = None,
    ) -> Alert:
        alert = self._transition(
            tenant_id,
            alert_id,
            outcome,
            actor=actor,
            comment=comment,
        )
        case = self._repo.get_case_by_alert(tenant_id, alert_id)
        pending_meta: dict[str, Any] = {}
        if outcome == "false_positive" and self._feedback is not None:
            _rule, pending = self._feedback.submit_feedback(
                tenant_id,
                kind="false_positive",
                actor_id=actor,
                actor_role="operator",
                feature_id=alert.feature_id,
                scope=RuleScope(
                    user_id=alert.user_id,
                    department_id=alert.department_id,
                    resource=alert.resource,
                    action=alert.action,
                    feature_id=alert.feature_id,
                ),
                comment=comment or "closed as false positive",
            )
            if pending is not None:
                pending_meta["pending_rule_id"] = pending.id
                self._timeline.record(
                    tenant_id,
                    alert_id,
                    case.id if case else None,
                    "feedback_submitted",
                    actor=actor,
                    comment=comment,
                    metadata=pending_meta,
                )
        self._timeline.record(
            tenant_id,
            alert_id,
            case.id if case else None,
            "closed",
            actor=actor,
            comment=comment or outcome,
            metadata={"outcome": outcome, **pending_meta},
        )
        return alert

    def suppress(
        self,
        tenant_id: str,
        alert_id: str,
        duration: str,
        *,
        actor: str = "operator",
        reason: str | None = None,
    ) -> SuppressionWindow:
        alert = self._repo.get_alert(tenant_id, alert_id)
        if alert is None:
            msg = f"Alert not found: {alert_id}"
            raise ValueError(msg)
        now = datetime.now(UTC)
        expires = parse_duration(duration, base=now)
        window = SuppressionWindow(
            id=self._repo.new_id(),
            tenant_id=tenant_id,
            alert_id=alert_id,
            scope={
                "feature_id": alert.feature_id,
                "user_id": alert.user_id,
                "department_id": alert.department_id,
                "resource": alert.resource,
            },
            starts_at=now,
            expires_at=expires,
            reason=reason,
            created_by=actor,
            active=True,
        )
        self._repo.insert_suppression(window)
        self._transition(
            tenant_id,
            alert_id,
            "suppressed",
            actor=actor,
            comment=reason or f"suppressed for {duration}",
        )
        return window

    def link_ticket(
        self,
        tenant_id: str,
        alert_id: str,
        ticket_id: str,
        *,
        actor: str = "operator",
    ) -> Alert:
        alert = self._transition(
            tenant_id,
            alert_id,
            "ticket_linked",
            actor=actor,
            comment=f"linked ticket {ticket_id}",
        )
        case = self._repo.get_case_by_alert(tenant_id, alert_id)
        if case:
            self._repo.update_case(
                tenant_id, case.id, status="ticket_linked", ticket_id=ticket_id
            )
            self._timeline.record(
                tenant_id,
                alert_id,
                case.id,
                "ticket_linked",
                actor=actor,
                metadata={"ticket_id": ticket_id},
            )
        return alert

    def list_cases(self, tenant_id: str, **kwargs: Any) -> list[AlertCase]:
        return self._repo.list_cases(tenant_id, **kwargs)

    def get_case(self, tenant_id: str, case_id: str) -> AlertCase | None:
        return self._repo.get_case(tenant_id, case_id)

    def assign_case(
        self,
        tenant_id: str,
        case_id: str,
        assignee: str,
        *,
        actor: str = "operator",
    ) -> AlertCase:
        case = self._repo.get_case(tenant_id, case_id)
        if case is None:
            msg = f"Case not found: {case_id}"
            raise ValueError(msg)
        self._repo.update_case(
            tenant_id, case_id, status=case.status, assigned_to=assignee
        )
        self._timeline.record(
            tenant_id,
            case.alert_id,
            case_id,
            "assigned",
            actor=actor,
            metadata={"assignee": assignee},
        )
        updated = self._repo.get_case(tenant_id, case_id)
        assert updated is not None
        return updated

    def add_case_comment(
        self,
        tenant_id: str,
        case_id: str,
        text: str,
        *,
        actor: str = "operator",
    ) -> CaseTimelineEntry:
        case = self._repo.get_case(tenant_id, case_id)
        if case is None:
            msg = f"Case not found: {case_id}"
            raise ValueError(msg)
        return self._timeline.record(
            tenant_id,
            case.alert_id,
            case_id,
            "comment_added",
            actor=actor,
            comment=text,
        )

    def get_timeline(
        self,
        tenant_id: str,
        *,
        alert_id: str | None = None,
        case_id: str | None = None,
    ) -> list:
        return self._repo.list_timeline(
            tenant_id, alert_id=alert_id, case_id=case_id
        )

    def get_alert_detail(
        self,
        tenant_id: str,
        alert_id: str,
        *,
        include_llm: bool = False,
    ) -> AlertDetailView | None:
        alert = self._repo.get_alert(tenant_id, alert_id)
        if alert is None:
            return None
        case = self._repo.get_case_by_alert(tenant_id, alert_id)
        assessment = None
        score_breakdown = None
        source_evidence: dict[str, Any] = {}
        run_id = alert.graph_run_id or (case.run_id if case else None)
        if run_id:
            assessment = self._repo.get_graph_run_assessment(run_id)
            if assessment:
                breakdown = assessment.get("breakdown")
                if isinstance(breakdown, dict):
                    score_breakdown = breakdown
            source_evidence["graph_audit"] = self._repo.get_graph_run_audit_summary(
                run_id
            )
        if alert.payload.get("assessment"):
            assessment = assessment or alert.payload.get("assessment")
        timeline = self._repo.list_timeline(tenant_id, alert_id=alert_id)
        llm_explanation = alert.payload.get("llm_explanation")
        detail = AlertDetailView(
            alert=alert,
            case=case,
            score_breakdown=score_breakdown,
            assessment=assessment,
            source_evidence=source_evidence,
            llm_explanation=llm_explanation,
            timeline=timeline,
        )
        if include_llm and self._llm is not None:
            explanation, _result = explain_alert(self._llm, detail, tenant_id=tenant_id)
            detail.llm_explanation = explanation
        return detail

    def generate_explanation(
        self,
        tenant_id: str,
        alert_id: str,
    ) -> dict[str, Any]:
        if self._llm is None:
            return {"skipped": True, "reason": "LLM gateway not configured"}
        detail = self.get_alert_detail(tenant_id, alert_id)
        if detail is None:
            msg = f"Alert not found: {alert_id}"
            raise ValueError(msg)
        explanation, _result = explain_alert(self._llm, detail, tenant_id=tenant_id)
        return explanation

    def export_case(
        self,
        tenant_id: str,
        case_id: str,
        *,
        fmt: str = "json",
        include_llm: bool = False,
    ) -> str:
        case = self._repo.get_case(tenant_id, case_id)
        if case is None:
            msg = f"Case not found: {case_id}"
            raise ValueError(msg)
        detail = self.get_alert_detail(
            tenant_id, case.alert_id, include_llm=include_llm
        )
        if detail is None:
            msg = f"Alert not found for case: {case_id}"
            raise ValueError(msg)
        detail.timeline = self._repo.list_timeline(
            tenant_id, case_id=case_id
        ) or detail.timeline
        if fmt == "md" or fmt == "markdown":
            return export_case_markdown(detail)
        return export_case_json(detail)

    def is_suppressed(self, tenant_id: str, alert_id: str) -> bool:
        return self._repo.is_alert_suppressed(
            tenant_id, alert_id, as_of=datetime.now(UTC)
        )

    def expire_suppressions(self, tenant_id: str) -> int:
        return self._repo.deactivate_expired_suppressions(
            tenant_id, as_of=datetime.now(UTC)
        )

    def list_silent_findings(
        self,
        tenant_id: str,
        *,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return self._repo.list_silent_findings(tenant_id, since=since, limit=limit)

    def _transition(
        self,
        tenant_id: str,
        alert_id: str,
        to_status: AlertStatus,
        *,
        actor: str,
        comment: str | None,
    ) -> Alert:
        alert = self._repo.get_alert(tenant_id, alert_id)
        if alert is None:
            msg = f"Alert not found: {alert_id}"
            raise ValueError(msg)
        if alert.status in TERMINAL_STATUSES and to_status not in VALID_TRANSITIONS.get(
            alert.status, frozenset()
        ):
            if alert.status == to_status:
                return alert
        allowed = VALID_TRANSITIONS.get(alert.status, frozenset())
        if to_status not in allowed and alert.status != to_status:
            msg = f"Cannot transition {alert.status} -> {to_status}"
            raise AlertLifecycleError(msg)
        from_status = alert.status
        now = datetime.now(UTC)
        self._repo.update_alert_status(tenant_id, alert_id, to_status, updated_at=now)
        case = self._repo.get_case_by_alert(tenant_id, alert_id)
        if case:
            self._repo.update_case(tenant_id, case.id, status=to_status)
        self._record_event(
            tenant_id,
            alert_id,
            case.id if case else None,
            from_status,
            to_status,
            actor=actor,
            comment=comment,
        )
        updated = self._repo.get_alert(tenant_id, alert_id)
        assert updated is not None
        return updated

    def _record_event(
        self,
        tenant_id: str,
        alert_id: str,
        case_id: str | None,
        from_status: str | None,
        to_status: str,
        *,
        actor: str,
        comment: str | None,
    ) -> None:
        event = AlertLifecycleEvent(
            id=self._repo.new_id(),
            tenant_id=tenant_id,
            alert_id=alert_id,
            alert_case_id=case_id,
            from_status=from_status,
            to_status=to_status,
            actor=actor,
            comment=comment,
            created_at=datetime.now(UTC),
        )
        self._repo.insert_lifecycle_event(event)
