"""Alert lifecycle and suppression service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from watchtower.domain.alerts import (
    TERMINAL_STATUSES,
    VALID_TRANSITIONS,
    Alert,
    AlertCase,
    AlertLifecycleEvent,
    AlertStatus,
    SuppressionWindow,
)
from watchtower.domain.rules import RuleScope
from watchtower.alerts.duration import parse_duration
from watchtower.feedback.service import FeedbackService
from watchtower.storage.repositories.alerts import AlertRepository

CloseOutcome = Literal["true_positive", "false_positive"]


class AlertLifecycleError(Exception):
    """Invalid lifecycle transition."""


class AlertService:
    def __init__(
        self,
        repo: AlertRepository,
        feedback: FeedbackService | None = None,
    ) -> None:
        self._repo = repo
        self._feedback = feedback

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
        return self._transition(tenant_id, alert_id, "investigating", actor=actor)

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
        if outcome == "false_positive" and self._feedback is not None:
            self._feedback.submit_feedback(
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
        return alert

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
