"""Unified normalized event and candidate event models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

SchemaFormat = Literal[
    "server_stack",
    "file_jsonl",
    "elasticsearch",
    "wazuh",
    "simulation_fixture",
]


class NormalizedEvent(BaseModel):
    """Unified Watchtower event schema (deterministic, LLM-free)."""

    id: str | None = None
    tenant_id: str
    raw_event_id: str | None = None
    source_id: str | None = None
    schema_format: SchemaFormat
    event_type: str
    actor: str | None = None
    action: str
    resource: str | None = None
    occurred_at: datetime
    feature_hint: str | None = None
    scenario_id: str | None = None
    source_path: str | None = None
    channel: str | None = None
    anomaly_flag: bool = False
    attributes: dict[str, Any] = Field(default_factory=dict)


class CandidateEvent(BaseModel):
    """Decision-graph-ready candidate (never created directly from raw logs)."""

    id: str | None = None
    tenant_id: str
    normalized_event_id: str
    feature_hint: str
    actor: str
    action: str
    resource: str
    occurred_at: datetime
    scenario_id: str | None = None
    anomaly_flag: bool = False
    attributes: dict[str, Any] = Field(default_factory=dict)


class UnknownSchemaEntry(BaseModel):
    """Pending operator mapping for unrecognized payloads."""

    id: str | None = None
    tenant_id: str
    raw_event_id: str | None = None
    schema_signature: str
    payload_sample: dict[str, Any]
    reason: str
    status: Literal["pending", "mapped", "ignored"] = "pending"
    created_at: datetime | None = None


class NormalizationOutcome(BaseModel):
    """Result of normalizing one raw payload."""

    normalized: NormalizedEvent | None = None
    unknown: UnknownSchemaEntry | None = None
