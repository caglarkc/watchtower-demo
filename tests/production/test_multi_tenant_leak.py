"""Multi-tenant isolation: no cross-tenant reads."""

from __future__ import annotations

from watchtower.storage.repositories.tenant import TenantRepository


def test_multi_tenant_source_isolation(prod_app):
    with prod_app.session() as session:
        t1 = TenantRepository(session.conn).create("Tenant A", "tenant-a")
        t2 = TenantRepository(session.conn).create("Tenant B", "tenant-b")
        s1 = session.sources.create(
            t1.id, "mock", "a-source", source_id="only-a", config={"events": []}
        )
        session.conn.commit()

        leak = session.sources.get(s1.id, tenant_id=t2.id)
        own = session.sources.get(s1.id, tenant_id=t1.id)

    assert leak is None
    assert own is not None
    assert own.tenant_id == t1.id
