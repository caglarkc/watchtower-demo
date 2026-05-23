"""Baseline profile and observation domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

SnapshotPeriod = Literal["daily", "weekly", "monthly"]
SeniorityLevel = Literal["worker", "senior", "manager", "executive"]
ProfileKind = Literal["user", "department", "role", "asset"]


class MetricStats(BaseModel):
    """Aggregated statistics for one metric within a profile."""

    metric_name: str
    sample_count: int = 0
    distinct_days: int = 0
    mean: float = 0.0
    std: float = 0.0
    minimum: float = 0.0
    maximum: float = 0.0
    p50: float = 0.0
    p95: float = 0.0

    @property
    def low(self) -> float:
        if self.sample_count < 2:
            return self.mean
        return max(0.0, self.mean - max(self.std, self.mean * 0.05))

    @property
    def high(self) -> float:
        if self.sample_count < 2:
            return self.mean
        return self.mean + max(self.std * 2, self.mean * 0.2)


class BehaviorObservation(BaseModel):
    """Single metric sample used to learn baselines."""

    tenant_id: str
    metric_name: str
    value: float
    observed_at: datetime
    user_id: str | None = None
    department_id: str | None = None
    role_id: str | None = None
    seniority: SeniorityLevel = "worker"
    asset_id: str | None = None
    feature_hint: str | None = None


class UserProfile(BaseModel):
    tenant_id: str
    user_id: str
    department_id: str | None = None
    role_id: str | None = None
    seniority: SeniorityLevel = "worker"
    metrics: dict[str, MetricStats] = Field(default_factory=dict)
    confidence: float = 0.0
    window_days: int = 45
    updated_at: datetime | None = None


class DepartmentProfile(BaseModel):
    tenant_id: str
    department_id: str
    metrics: dict[str, MetricStats] = Field(default_factory=dict)
    confidence: float = 0.0
    window_days: int = 45
    updated_at: datetime | None = None


class RoleProfile(BaseModel):
    """Role norms; scoped by department + seniority (manager vs worker)."""

    tenant_id: str
    role_id: str
    department_id: str
    seniority: SeniorityLevel
    metrics: dict[str, MetricStats] = Field(default_factory=dict)
    confidence: float = 0.0
    window_days: int = 45
    updated_at: datetime | None = None

    @property
    def profile_key(self) -> str:
        return f"{self.department_id}:{self.role_id}:{self.seniority}"


class AssetProfile(BaseModel):
    tenant_id: str
    asset_id: str
    metrics: dict[str, MetricStats] = Field(default_factory=dict)
    confidence: float = 0.0
    window_days: int = 45
    updated_at: datetime | None = None


class BaselineSnapshot(BaseModel):
    tenant_id: str
    period: SnapshotPeriod
    profile_kind: ProfileKind
    profile_key: str
    window_start: datetime
    window_end: datetime
    metrics: dict[str, MetricStats] = Field(default_factory=dict)
    confidence: float = 0.0


class LearningWindow(BaseModel):
    tenant_id: str
    window_days: int
    started_at: datetime
    ends_at: datetime
    observation_count: int = 0
    distinct_users: int = 0
    confidence: float = 0.0


class RunTransitionAdvice(BaseModel):
    """Whether learn→run transition is recommended."""

    recommended: bool
    confidence: float
    reason: str
    blocking: bool = False


class BaselineEvaluation(BaseModel):
    """Result of comparing an observed value to layered baselines."""

    metric_name: str
    value: float
    is_normal: bool
    source: ProfileKind | Literal["none"]
    used_user_baseline: bool
    effective_low: float | None = None
    effective_high: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)
