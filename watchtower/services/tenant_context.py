"""Per-request tenant isolation via context variables."""

from __future__ import annotations

from contextvars import ContextVar

_tenant_id: ContextVar[str | None] = ContextVar("watchtower_tenant_id", default=None)


class TenantIsolationError(RuntimeError):
    """Raised when tenant context is missing or mismatched."""


class TenantContext:
    @staticmethod
    def set_current(tenant_id: str) -> None:
        _tenant_id.set(tenant_id)

    @staticmethod
    def get_current() -> str | None:
        return _tenant_id.get()

    @staticmethod
    def require_current() -> str:
        tenant_id = _tenant_id.get()
        if tenant_id is None:
            msg = "Tenant context is not set"
            raise TenantIsolationError(msg)
        return tenant_id

    @staticmethod
    def clear() -> None:
        _tenant_id.set(None)

    @staticmethod
    def assert_tenant(expected: str) -> None:
        current = TenantContext.require_current()
        if current != expected:
            msg = f"Tenant isolation violation: expected {expected}, got {current}"
            raise TenantIsolationError(msg)
