"""Durable LangGraph checkpoint storage (SQLite) with retention."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from watchtower.config.settings import WatchtowerSettings

CheckpointerKind = Literal["sqlite", "memory"]


@dataclass
class GraphCheckpointStore:
    """Process-scoped checkpoint backend (separate SQLite file from product DB)."""

    kind: CheckpointerKind
    path: Path | None
    _conn: sqlite3.Connection | None = None
    _saver: BaseCheckpointSaver | None = None
    _memory: MemorySaver | None = None

    @classmethod
    def from_settings(cls, settings: WatchtowerSettings) -> GraphCheckpointStore:
        if settings.graph_checkpoint_use_memory or not settings.graph_checkpoint_enabled:
            return cls(kind="memory", path=None)
        path = settings.graph_checkpoint_path
        path.parent.mkdir(parents=True, exist_ok=True)
        return cls(kind="sqlite", path=path)

    def get_checkpointer(self) -> BaseCheckpointSaver:
        if self._saver is not None:
            return self._saver
        if self.kind == "memory":
            self._memory = MemorySaver()
            self._saver = self._memory
            return self._saver
        if self._conn is None:
            assert self.path is not None
            self._conn = sqlite3.connect(
                str(self.path),
                check_same_thread=False,
            )
            self._conn.execute("PRAGMA journal_mode=WAL")
        saver = SqliteSaver(self._conn)
        saver.setup()
        self._saver = saver
        return self._saver

    def thread_has_checkpoint(self, thread_id: str) -> bool:
        if self.kind == "memory":
            self.get_checkpointer()
            if self._memory is None:
                return False
            config = {"configurable": {"thread_id": thread_id}}
            return self._memory.get_tuple(config) is not None
        self.get_checkpointer()
        assert self._conn is not None
        row = self._conn.execute(
            "SELECT 1 FROM checkpoints WHERE thread_id = ? LIMIT 1",
            (thread_id,),
        ).fetchone()
        return row is not None

    def delete_thread(self, thread_id: str) -> None:
        saver = self.get_checkpointer()
        if isinstance(saver, SqliteSaver):
            saver.delete_thread(thread_id)

    def prune_threads(self, thread_ids: list[str]) -> int:
        if not thread_ids:
            return 0
        saver = self.get_checkpointer()
        if isinstance(saver, SqliteSaver):
            for tid in thread_ids:
                saver.delete_thread(tid)
        return len(thread_ids)

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        self._saver = None
        self._memory = None


def prune_completed_checkpoints(
    product_conn: sqlite3.Connection,
    store: GraphCheckpointStore,
    *,
    retention_days: int,
) -> int:
    """Remove checkpoint blobs for completed graph runs older than retention."""
    if retention_days <= 0 or store.kind != "sqlite":
        return 0
    cutoff = (datetime.now(UTC) - timedelta(days=retention_days)).isoformat()
    rows = product_conn.execute(
        """
        SELECT thread_id FROM graph_runs
        WHERE status = 'completed'
          AND thread_id IS NOT NULL
          AND finished_at IS NOT NULL
          AND finished_at < ?
        """,
        (cutoff,),
    ).fetchall()
    thread_ids = [str(r[0]) for r in rows if r[0]]
    return store.prune_threads(thread_ids)
