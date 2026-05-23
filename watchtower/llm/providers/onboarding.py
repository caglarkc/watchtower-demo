"""Provider chain resolution with DB override for production switches."""

from __future__ import annotations

import sqlite3

from watchtower.config.settings import WatchtowerSettings
from watchtower.llm.protocol import LLMProvider
from watchtower.llm.providers.factory import build_provider_chain
from watchtower.storage.repositories.system_metadata import SystemMetadataRepository

METADATA_PROVIDER_CHAIN_KEY = "llm_provider_chain"


def resolve_provider_chain(
    settings: WatchtowerSettings,
    conn: sqlite3.Connection | None,
) -> list[LLMProvider]:
    effective = settings
    if conn is not None:
        stored = SystemMetadataRepository(conn).get(METADATA_PROVIDER_CHAIN_KEY)
        if stored:
            effective = settings.model_copy(update={"llm_provider_chain": stored})
    return build_provider_chain(effective)


def set_provider_chain(conn: sqlite3.Connection, chain: str) -> None:
    SystemMetadataRepository(conn).set(METADATA_PROVIDER_CHAIN_KEY, chain)


def clear_provider_chain(conn: sqlite3.Connection) -> None:
    SystemMetadataRepository(conn).delete(METADATA_PROVIDER_CHAIN_KEY)
