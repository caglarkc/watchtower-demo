"""Tenant isolation tests."""

from __future__ import annotations

from watchtower.services.tenant_context import TenantContext, TenantIsolationError


def test_audit_log_isolated_per_tenant(app):
    with app.session() as session:
        tenant_a = session.tenants.create("Tenant A", "tenant-a")
        tenant_b = session.tenants.create("Tenant B", "tenant-b")

        session.audit.log("test.event", tenant_id=tenant_a.id, details={"n": 1})
        session.audit.log("test.event", tenant_id=tenant_b.id, details={"n": 2})

        logs_a = session.audit_repo.list_for_tenant(tenant_a.id)
        logs_b = session.audit_repo.list_for_tenant(tenant_b.id)

    assert len(logs_a) == 1
    assert logs_a[0].tenant_id == tenant_a.id
    assert logs_a[0].details["n"] == 1

    assert len(logs_b) == 1
    assert logs_b[0].tenant_id == tenant_b.id
    assert logs_b[0].details["n"] == 2


def test_tenant_context_requires_set():
    TenantContext.clear()
    try:
        TenantContext.require_current()
    except TenantIsolationError:
        pass
    else:
        raise AssertionError("expected TenantIsolationError")
