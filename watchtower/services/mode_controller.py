"""Operating mode controller."""

from __future__ import annotations

from watchtower.domain.mode import DEFAULT_MODE, VALID_MODES, WatchtowerMode
from watchtower.services.audit import AuditService
from watchtower.storage.repositories.mode import ModeRepository


class ModeController:
    def __init__(self, repo: ModeRepository, audit: AuditService) -> None:
        self._repo = repo
        self._audit = audit

    def get_mode(self, tenant_id: str) -> WatchtowerMode:
        return self._repo.get_mode(tenant_id)

    def set_mode(
        self,
        tenant_id: str,
        mode: WatchtowerMode,
        *,
        actor: str | None = None,
    ) -> WatchtowerMode:
        if mode not in VALID_MODES:
            msg = f"Unsupported mode: {mode}"
            raise ValueError(msg)
        previous = self._repo.get_mode(tenant_id)
        self._repo.set_mode(tenant_id, mode)
        self._audit.log(
            "mode.changed",
            tenant_id=tenant_id,
            actor=actor,
            details={"from": previous, "to": mode},
        )
        return mode

    def default_mode(self) -> WatchtowerMode:
        return DEFAULT_MODE
