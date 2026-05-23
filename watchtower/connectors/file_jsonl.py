"""Read-only JSONL file connector with rotation/truncation-safe cursors."""

from __future__ import annotations

import json
import os
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


def _file_identity(path: Path) -> tuple[int, int]:
    stat = path.stat()
    inode = int(getattr(stat, "st_ino", 0) or 0)
    return inode, int(stat.st_size)


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
        inode, size = _file_identity(self.file_path)
        return SourceHealth(
            status="healthy",
            message="jsonl file readable",
            details={
                "path": str(self.file_path),
                "size": size,
                "inode": inode,
            },
        )

    def _reset_file_cursor(self, cursor: ConnectorCursor, path_key: str, reason: str) -> None:
        cursor.set_file_state(
            path_key,
            offset=0,
            line_number=0,
            partial="",
            inode=_file_identity(self.file_path)[0],
            size=_file_identity(self.file_path)[1],
            reset_reason=reason,
        )

    def poll(self, cursor: ConnectorCursor, limit: int) -> EventBatch:
        path_key = str(self.file_path.resolve())
        if not self.file_path.is_file():
            raise ConnectorError(f"file not found: {self.file_path}")

        inode, size = _file_identity(self.file_path)
        state = cursor.file_state(path_key)
        offset = int(state.get("offset", 0))
        line_number = int(state.get("line_number", 0))
        partial = str(state.get("partial", "") or "")

        prev_inode = state.get("inode")
        prev_size = state.get("size")
        if prev_inode is not None and int(prev_inode) != inode:
            self._reset_file_cursor(cursor, path_key, "inode_rotation")
            offset = 0
            line_number = 0
            partial = ""
            state = cursor.file_state(path_key)
        elif prev_size is not None and size < int(prev_size):
            self._reset_file_cursor(cursor, path_key, "truncation")
            offset = 0
            line_number = 0
            partial = ""
            state = cursor.file_state(path_key)
        elif offset > size:
            self._reset_file_cursor(cursor, path_key, "offset_past_eof")
            offset = 0
            line_number = 0
            partial = ""

        events: list[RawEventRecord] = []
        bytes_read = 0

        with self.file_path.open(encoding="utf-8", errors="replace") as handle:
            if offset:
                handle.seek(offset)
            buffer = partial
            while len(events) < limit:
                line = handle.readline()
                if not line:
                    if buffer.strip():
                        partial = buffer
                    else:
                        partial = ""
                    break
                bytes_read += len(line.encode("utf-8"))
                buffer += line
                if not line.endswith("\n"):
                    partial = buffer
                    break
                buffer = ""
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
        cursor.set_file_state(
            path_key,
            offset=new_offset,
            line_number=line_number,
            partial=partial,
            inode=inode,
            size=size,
        )
        has_more = new_offset < size or bool(partial)
        next_cursor = ConnectorCursor(data=dict(cursor.data))
        return EventBatch(events=events, next_cursor=next_cursor, has_more=has_more)

    def ack(self, cursor: ConnectorCursor) -> None:
        return None

    def schema_hint(self) -> SourceSchemaHint:
        return SourceSchemaHint(
            format="jsonl",
            fields=["timestamp", "user", "event_type"],
            notes="Byte-offset cursor with rotation/truncation detection",
        )
