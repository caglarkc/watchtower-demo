"""Tenant and bootstrap admin domain models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Tenant(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime


class BootstrapAdmin(BaseModel):
    id: str
    tenant_id: str
    username: str
    email: str
    is_active: bool = True
    created_at: datetime

    # password_hash is intentionally excluded from the public model.
