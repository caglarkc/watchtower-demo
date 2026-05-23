"""Ingest source domain model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SourceRecord(BaseModel):
    id: str
    tenant_id: str
    connector_type: str
    name: str
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
