"""Pydantic models for the Watchtower feature taxonomy."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

DetectionClass = Literal[
    "policy-rule",
    "hard-rule",
    "baseline-anomaly",
    "cross-signal",
]

SeverityFloor = Literal["LOG", "WARNING", "ALERT", "CRITICAL"]

VALID_DETECTION_CLASSES: frozenset[str] = frozenset(
    {"policy-rule", "hard-rule", "baseline-anomaly", "cross-signal"}
)

REQUIRED_ENTRY_FIELDS: frozenset[str] = frozenset(
    {
        "feature_id",
        "primary_detection_class",
        "secondary_detection_classes",
        "default_severity_floor",
        "requires_baseline",
        "can_be_feedback_learned",
        "requires_approval_for_suppression",
        "required_context",
        "server_stack_replay_refs",
    }
)

BASELINE_CONTEXT_TOKENS: frozenset[str] = frozenset(
    {
        "user_baseline",
        "department_baseline",
        "role_baseline",
        "role_in_department_baseline",
        "peer_group_baseline",
        "baseline",
    }
)


class FeatureTaxonomyEntry(BaseModel):
    """Single feature taxonomy record."""

    feature_id: str
    primary_detection_class: DetectionClass
    secondary_detection_classes: list[DetectionClass] = Field(default_factory=list)
    default_severity_floor: SeverityFloor
    requires_baseline: bool
    can_be_feedback_learned: bool
    requires_approval_for_suppression: bool
    required_context: list[str] = Field(min_length=1)
    server_stack_replay_refs: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def secondary_must_differ_from_primary(self) -> FeatureTaxonomyEntry:
        if self.primary_detection_class in self.secondary_detection_classes:
            msg = (
                "secondary_detection_classes cannot repeat primary: "
                f"{self.primary_detection_class}"
            )
            raise ValueError(msg)
        return self

    def has_baseline_context(self) -> bool:
        return any(
            token in ctx or ctx.endswith("_baseline")
            for ctx in self.required_context
            for token in BASELINE_CONTEXT_TOKENS
        )


class FeatureTaxonomy(BaseModel):
    """Root taxonomy document."""

    version: str
    total_features: int
    policy_rule_features: list[str] = Field(default_factory=list)
    features: list[FeatureTaxonomyEntry]

    @property
    def feature_ids(self) -> set[str]:
        return {entry.feature_id for entry in self.features}

    def by_id(self) -> dict[str, FeatureTaxonomyEntry]:
        return {entry.feature_id: entry for entry in self.features}
