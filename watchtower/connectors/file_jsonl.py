"""Read-only JSONL file connector."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from watchtower.connectors.base import BaseConnector, ConnectorError
from watchtower.domain.events import (
    ConnectorCursor,
    EventBatch,
    RawEventRecord,
    SourceHealth,
    SourceSchemaHint,
)
from watchtower.ingest.dedupe import dedupe_key_for_file_line


def _parse_timestamp(payload: dict[str, Any]) -> datetime | None:
    for key in ("timestamp", "ts", "@timestamp", "event_time"):
        value = payload.get(key)
        if value is None:
            continue
        try:
            normalized = str(value).replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except ValueError:
            continue
    return None


class FileJsonlConnector(BaseConnector):
    connector_type = "file_jsonl"

    def __init__(self, source_id: str, file_path: Path) -> None:
        super().__init__(source_id)
        self.file_path = Path(file_path)

    def health(self) -> SourceHealth:
        if not self.file_path.is_file():
            return SourceHealth(
                status="unhealthy",
                message=f"file not found: {self.file_path}",
            )
        return SourceHealth(
            status="healthy",
            message="jsonl file readable",
            details={"path": str(self.file_path), "size": self.file_path.stat().st_size},
        )

    def poll(self, cursor: ConnectorCursor, limit: int) -> EventBatch:
        path_key = str(self.file_path.resolve())
        if not self.file_path.is_file():
            raise ConnectorError(f"file not found: {self.file_path}")

        offset = cursor.file_offset(path_key)
        events: list[RawEventRecord] = []
        line_number = 0
        bytes_read = 0

        with self.file_path.open(encoding="utf-8") as handle:
            if offset:
                handle.seek(offset)
            while len(events) < limit:
                line = handle.readline()
                if not line:
                    break
                bytes_read += len(line.encode("utf-8"))
                line_number += 1
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    payload = json.loads(stripped)
                except json.JSONDecodeError:
                    payload = {"_raw": stripped, "_parse_error": "invalid_json"}
                if not isinstance(payload, dict):
                    payload = {"_raw": payload}

                events.append(
                    RawEventRecord(
                        dedupe_key=dedupe_key_for_file_line(
                            self.source_id, path_key, line_number, stripped
                        ),
                        payload=payload,
                        source_path=path_key,
                        event_timestamp=_parse_timestamp(payload),
                    )
                )

        new_offset = offset + bytes_read
        next_cursor = ConnectorCursor(data=dict(cursor.data))
        next_cursor.set_file_offset(path_key, new_offset)
        has_more = bool(events) and new_offset < self.file_path.stat().st_size
        return EventBatch(events=events, next_cursor=next_cursor, has_more=has_more)

    def ack(self, cursor: ConnectorCursor) -> None:
        return None

    def schema_hint(self) -> SourceSchemaHint:
        return SourceSchemaHint(
            format="jsonl",
            fields=["timestamp", "user", "event_type"],
            notes="One JSON object per line",
        )
