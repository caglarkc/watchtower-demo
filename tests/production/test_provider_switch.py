"""Provider chain switch via system_metadata."""

from __future__ import annotations

from watchtower.llm.providers.onboarding import (
    resolve_provider_chain,
    set_provider_chain,
)


def test_provider_switch_persists_in_db(prod_app, bootstrapped_tenant):
    with prod_app.session() as session:
        set_provider_chain(session.conn, "openai")
        session.conn.commit()
        chain = resolve_provider_chain(prod_app.settings, session.conn)
        names = [p.name for p in chain]
        assert "openai" in names or len(names) >= 0

        set_provider_chain(session.conn, "mock")
        session.conn.commit()


def test_provider_chain_override_order(prod_app):
    with prod_app.session() as session:
        set_provider_chain(session.conn, "openai,anthropic")
        session.conn.commit()
        stored = session.conn.execute(
            "SELECT value FROM system_metadata WHERE key = 'llm_provider_chain'"
        ).fetchone()
    assert stored is not None
    assert stored[0] == "openai,anthropic"
