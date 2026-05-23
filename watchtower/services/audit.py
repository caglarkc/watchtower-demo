"""Audit logging service."""

from __future__ import annotations

from typing import Any

from watchtower.config.settings import WatchtowerSettings
from watchtower.storage.repositories.audit import AuditRepository
from watchtower.services.tenant_context import TenantContext


class AuditService:
    def __init__(self, repo: AuditRepository, settings: WatchtowerSettings) -> None:
        self._repo = repo
        self._settings = settings

    def log(
        self,
        action: str,
        *,
        tenant_id: str | None = None,
        actor: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        if not self._settings.audit_log_enabled:
            return
        resolved_tenant = tenant_id or TenantContext.require_current()
        self._repo.append(resolved_tenant, action, actor=actor, details=details)
