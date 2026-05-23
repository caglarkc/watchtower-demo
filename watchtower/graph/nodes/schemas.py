"""Validated node output schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModeOutput(BaseModel):
    mode: str


class IdentityOutput(BaseModel):
    user_id: str
    department_id: str | None = None
    role_id: str | None = None
    seniority: str = "worker"


class AssetOutput(BaseModel):
    asset_id: str
    resource: str
    criticality: str = "medium"


class TaxonomyOutput(BaseModel):
    feature_id: str
    primary_detection_class: str
    requires_baseline: bool = False


class PolicyContextOutput(BaseModel):
    violated: bool = False
    severity_floor: str = "LOG"


class BaselineContextOutput(BaseModel):
    is_normal: bool | None = None
    source: str | None = None


class FeedbackContextOutput(BaseModel):
    matched: bool = False
    pending_rule_id: str | None = None
    suppress_alert: bool = False


class ChangeContextOutput(BaseModel):
    ticket_id: str | None = None
    maintenance_window: bool = False


class AssessmentOutput(BaseModel):
    severity: str
    should_alert: bool
    detection_class: str


class RouteOutput(BaseModel):
    mode: str
    should_persist_silent: bool
    should_create_alert: bool
    should_enqueue_learning: bool
    baseline_update_allowed: bool


class FinalizeOutput(BaseModel):
    status: str
    alert_case_id: str | None = None
    silent_finding_id: str | None = None
    learning_event_id: str | None = None
