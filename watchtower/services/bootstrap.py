"""Bootstrap admin and first-run setup."""

from __future__ import annotations

from watchtower.domain.tenant import BootstrapAdmin, Tenant
from watchtower.services.audit import AuditService
from watchtower.services.mode_controller import ModeController
from watchtower.storage.repositories.bootstrap import BootstrapRepository
from watchtower.storage.repositories.tenant import TenantRepository


class BootstrapRequiredError(RuntimeError):
    """Raised when bootstrap admin is required but missing."""


class BootstrapService:
    def __init__(
        self,
        tenants: TenantRepository,
        bootstrap: BootstrapRepository,
        modes: ModeController,
        audit: AuditService,
        *,
        default_tenant_slug: str = "default",
    ) -> None:
        self._tenants = tenants
        self._bootstrap = bootstrap
        self._modes = modes
        self._audit = audit
        self._default_slug = default_tenant_slug

    def get_default_tenant(self) -> Tenant | None:
        return self._tenants.get_by_slug(self._default_slug)

    def is_bootstrapped(self, tenant_id: str) -> bool:
        return self._bootstrap.has_active_admin(tenant_id)

    def require_bootstrapped(self, tenant_id: str) -> None:
        if not self.is_bootstrapped(tenant_id):
            msg = (
                "Bootstrap admin is required. Run `wt bootstrap` to create the "
                "system administrator account."
            )
            raise BootstrapRequiredError(msg)

    def bootstrap(
        self,
        username: str,
        email: str,
        password: str,
        *,
        tenant_name: str = "Default Organization",
    ) -> tuple[Tenant, BootstrapAdmin]:
        existing = self.get_default_tenant()
        if existing is not None and self.is_bootstrapped(existing.id):
            msg = "Watchtower is already bootstrapped for the default tenant"
            raise ValueError(msg)

        tenant = existing or self._tenants.create(tenant_name, self._default_slug)
        admin = self._bootstrap.create_admin(tenant.id, username, email, password)
        self._modes.get_mode(tenant.id)  # ensure runtime row with default learn
        self._audit.log(
            "bootstrap.completed",
            tenant_id=tenant.id,
            actor=username,
            details={"email": email},
        )
        return tenant, admin
