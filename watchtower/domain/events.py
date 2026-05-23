"""Connector and raw event domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

SourceHealthStatus = Literal["healthy", "degraded", "unhealthy"]


class SourceHealth(BaseModel):
    status: SourceHealthStatus
    message: str = ""
    details: dict[str, Any] = Field(default_factory=dict)


class ConnectorCursor(BaseModel):
    """Opaque cursor state persisted per source."""

    data: dict[str, Any] = Field(default_factory=dict)

    def file_offset(self, path: str) -> int:
        files = self.data.setdefault("files", {})
        entry = files.get(path, {})
        return int(entry.get("offset", 0))

    def set_file_offset(self, path: str, offset: int) -> None:
        files = self.data.setdefault("files", {})
        entry = files.get(path, {})
        if isinstance(entry, dict):
            entry["offset"] = offset
            files[path] = entry
        else:
            files[path] = {"offset": offset}

    def file_state(self, path: str) -> dict[str, Any]:
        files = self.data.setdefault("files", {})
        entry = files.get(path, {})
        return entry if isinstance(entry, dict) else {}

    def set_file_state(self, path: str, **fields: Any) -> None:
        files = self.data.setdefault("files", {})
        entry = dict(files.get(path, {})) if isinstance(files.get(path), dict) else {}
        entry.update(fields)
        files[path] = entry

    def es_search_after(self) -> list[Any] | None:
        es = self.data.get("elasticsearch")
        if not isinstance(es, dict):
            return None
        value = es.get("search_after")
        return value if isinstance(value, list) else None

    def set_es_search_after(self, search_after: list[Any] | None) -> None:
        es = self.data.setdefault("elasticsearch", {})
        es["search_after"] = search_after

    def wazuh_state(self) -> dict[str, Any]:
        wazuh = self.data.get("wazuh")
        return wazuh if isinstance(wazuh, dict) else {}

    def set_wazuh_state(self, **fields: Any) -> None:
        wazuh = self.data.setdefault("wazuh", {})
        wazuh.update(fields)


class SourceSchemaHint(BaseModel):
    format: str
    fields: list[str] = Field(default_factory=list)
    notes: str = ""


class RawEventRecord(BaseModel):
    """One raw event produced by a connector poll."""

    dedupe_key: str
    payload: dict[str, Any]
    source_path: str | None = None
    event_timestamp: datetime | None = None


class EventBatch(BaseModel):
    events: list[RawEventRecord] = Field(default_factory=list)
    next_cursor: ConnectorCursor = Field(default_factory=ConnectorCursor)
    has_more: bool = False


class IngestResult(BaseModel):
    source_id: str
    polled: int = 0
    stored: int = 0
    duplicates: int = 0
    skipped: int = 0
    has_more: bool = False
    health_status: SourceHealthStatus = "healthy"
    error: str | None = None
    degraded: bool = False
