"""Alert, alert case, and suppression domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

AlertStatus = Literal[
    "open",
    "investigating",
    "true_positive",
    "false_positive",
    "suppressed",
    "ticket_linked",
]

TERMINAL_STATUSES: frozenset[str] = frozenset(
    {"true_positive", "false_positive", "suppressed", "ticket_linked"}
)

VALID_TRANSITIONS: dict[str, frozenset[str]] = {
    "open": frozenset({"investigating", "suppressed"}),
    "investigating": frozenset(
        {"true_positive", "false_positive", "suppressed", "ticket_linked"}
    ),
    "suppressed": frozenset({"open", "investigating"}),
    "ticket_linked": frozenset({"investigating", "true_positive", "false_positive"}),
    "true_positive": frozenset(),
    "false_positive": frozenset(),
}


class Alert(BaseModel):
    id: str
    tenant_id: str
    feature_id: str
    severity: str
    status: AlertStatus = "open"
    title: str
    summary: str | None = None
    user_id: str | None = None
    department_id: str | None = None
    resource: str | None = None
    action: str | None = None
    graph_run_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class AlertCase(BaseModel):
    id: str
    tenant_id: str
    alert_id: str
    status: AlertStatus
    run_id: str | None = None
    candidate_id: str | None = None
    ticket_id: str | None = None
    assigned_to: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class SuppressionWindow(BaseModel):
    id: str
    tenant_id: str
    alert_id: str
    scope: dict[str, Any] = Field(default_factory=dict)
    starts_at: datetime
    expires_at: datetime
    reason: str | None = None
    created_by: str | None = None
    active: bool = True


class AlertLifecycleEvent(BaseModel):
    id: str
    tenant_id: str
    alert_id: str
    alert_case_id: str | None = None
    from_status: str | None = None
    to_status: str
    actor: str | None = None
    comment: str | None = None
    created_at: datetime
