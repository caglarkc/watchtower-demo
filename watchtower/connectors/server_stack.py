"""Read-only connector for Watchtower demo server-stack logs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from watchtower.connectors.base import BaseConnector, ConnectorError
from watchtower.connectors.file_jsonl import _parse_timestamp
from watchtower.domain.events import (
    ConnectorCursor,
    EventBatch,
    RawEventRecord,
    SourceHealth,
    SourceSchemaHint,
)
from watchtower.ingest.dedupe import dedupe_key_for_file_line, dedupe_key_for_payload


class ServerStackConnector(BaseConnector):
    """Poll JSONL and plain log files under server-stack/logs (read-only)."""

    connector_type = "server_stack"

    def __init__(
        self,
        source_id: str,
        logs_root: Path,
        *,
        include_globs: tuple[str, ...] = ("**/*.jsonl", "**/*.log"),
        max_files: int | None = None,
    ) -> None:
        super().__init__(source_id)
        self.logs_root = Path(logs_root)
        self.include_globs = include_globs
        self.max_files = max_files

    def _iter_log_files(self) -> list[Path]:
        if not self.logs_root.is_dir():
            return []
        found: list[Path] = []
        for pattern in self.include_globs:
            found.extend(sorted(self.logs_root.glob(pattern)))
        unique = sorted({p.resolve() for p in found if p.is_file()})
        if self.max_files is not None:
            return unique[: self.max_files]
        return unique

    def health(self) -> SourceHealth:
        if not self.logs_root.is_dir():
            return SourceHealth(
                status="unhealthy",
                message=f"server-stack logs root missing: {self.logs_root}",
            )
        files = self._iter_log_files()
        if not files:
            return SourceHealth(
                status="degraded",
                message="logs root exists but no log files matched",
                details={"root": str(self.logs_root)},
            )
        return SourceHealth(
            status="healthy",
            message="server-stack logs available",
            details={"root": str(self.logs_root), "file_count": len(files)},
        )

    def poll(self, cursor: ConnectorCursor, limit: int) -> EventBatch:
        files = self._iter_log_files()
        if not files:
            return EventBatch(events=[], next_cursor=cursor, has_more=False)

        events: list[RawEventRecord] = []
        next_cursor = ConnectorCursor(data=dict(cursor.data))
        file_index = int(cursor.data.get("file_index", 0))

        while file_index < len(files) and len(events) < limit:
            path = files[file_index]
            path_key = str(path)
            remaining = limit - len(events)
            batch, advanced, at_eof = self._poll_file(
                path, next_cursor, remaining, file_index
            )
            events.extend(batch)
            if at_eof:
                file_index += 1
                next_cursor.data["file_index"] = file_index
                next_cursor.set_file_offset(path_key, 0)
            elif advanced:
                next_cursor.data["file_index"] = file_index
            else:
                break

        has_more = file_index < len(files) or any(
            path.stat().st_size > next_cursor.file_offset(str(path))
            for path in files[file_index : file_index + 1]
            if path.is_file()
        )
        return EventBatch(events=events, next_cursor=next_cursor, has_more=has_more)

    def _poll_file(
        self,
        path: Path,
        cursor: ConnectorCursor,
        limit: int,
        file_index: int,
    ) -> tuple[list[RawEventRecord], bool, bool]:
        path_key = str(path)
        offset = cursor.file_offset(path_key)
        events: list[RawEventRecord] = []
        line_number = int(cursor.data.get("line_numbers", {}).get(path_key, 0))
        bytes_read = 0
        is_jsonl = path.suffix == ".jsonl"

        with path.open(encoding="utf-8", errors="replace") as handle:
            if offset:
                handle.seek(offset)
            while len(events) < limit:
                line = handle.readline()
                if not line:
                    break
                bytes_read += len(line.encode("utf-8"))
                line_number += 1
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                if is_jsonl:
                    try:
                        payload = json.loads(stripped)
                    except json.JSONDecodeError:
                        payload = {"_raw": stripped}
                    if not isinstance(payload, dict):
                        payload = {"_value": payload}
                    dedupe = dedupe_key_for_file_line(
                        self.source_id, path_key, line_number, stripped
                    )
                    ts = _parse_timestamp(payload)
                else:
                    payload = {
                        "_raw": stripped,
                        "_log_channel": path.parent.name,
                        "_file": path.name,
                    }
                    dedupe = dedupe_key_for_payload(self.source_id, path_key, payload)
                    ts = None

                payload.setdefault("_source_path", path_key)
                payload.setdefault("_source_index", file_index)
                events.append(
                    RawEventRecord(
                        dedupe_key=dedupe,
                        payload=payload,
                        source_path=path_key,
                        event_timestamp=ts,
                    )
                )

        new_offset = offset + bytes_read
        cursor.set_file_offset(path_key, new_offset)
        line_numbers = cursor.data.setdefault("line_numbers", {})
        line_numbers[path_key] = line_number
        at_eof = new_offset >= path.stat().st_size
        return events, bool(events), at_eof

    def ack(self, cursor: ConnectorCursor) -> None:
        return None

    def schema_hint(self) -> SourceSchemaHint:
        return SourceSchemaHint(
            format="server_stack_mixed",
            fields=["timestamp", "ts", "user", "event_type", "_raw"],
            notes="JSONL plus plain .log lines from demo stack",
        )
