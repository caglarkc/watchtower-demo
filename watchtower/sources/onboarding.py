"""Register ingest sources for closed-network deployments."""

from __future__ import annotations

import json
from typing import Any

from watchtower.domain.source import SourceRecord
from watchtower.security.masking import mask_mapping
from watchtower.storage.repositories.source import SourceRepository

SUPPORTED_CONNECTORS = (
    "server_stack",
    "file_jsonl",
    "elasticsearch",
    "wazuh",
    "mock",
)


class SourceOnboardingService:
    def __init__(self, sources: SourceRepository) -> None:
        self._sources = sources

    def register(
        self,
        tenant_id: str,
        connector_type: str,
        name: str,
        config: dict[str, Any] | None = None,
        *,
        source_id: str | None = None,
        enabled: bool = True,
    ) -> SourceRecord:
        if connector_type not in SUPPORTED_CONNECTORS:
            msg = f"unsupported connector: {connector_type}"
            raise ValueError(msg)
        return self._sources.create(
            tenant_id,
            connector_type,
            name,
            config or {},
            source_id=source_id,
            enabled=enabled,
        )

    @staticmethod
    def config_preview(config: dict[str, Any]) -> str:
        return json.dumps(mask_mapping(config), indent=2, ensure_ascii=False)
