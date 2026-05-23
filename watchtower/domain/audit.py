"""Audit log domain model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditEntry(BaseModel):
    id: str
    tenant_id: str
    actor: str | None = None
    action: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
