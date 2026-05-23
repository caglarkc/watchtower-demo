"""Per-source exponential backoff for daemon ingest polls."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class _BackoffState:
    failures: int = 0
    next_allowed_at: float = 0.0


class SourceBackoffTracker:
    """In-memory backoff state (per daemon process)."""

    def __init__(
        self,
        *,
        base_seconds: float = 5.0,
        max_seconds: float = 300.0,
    ) -> None:
        self._base = base_seconds
        self._max = max_seconds
        self._states: dict[str, _BackoffState] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not hasattr(self, "_states"):
            self._states = {}

    def is_blocked(self, source_id: str) -> bool:
        state = self._states.get(source_id)
        if state is None:
            return False
        return time.monotonic() < state.next_allowed_at

    def record_success(self, source_id: str) -> None:
        self._states.pop(source_id, None)

    def record_failure(self, source_id: str) -> float:
        state = self._states.setdefault(source_id, _BackoffState())
        state.failures += 1
        delay = min(self._base * (2 ** (state.failures - 1)), self._max)
        state.next_allowed_at = time.monotonic() + delay
        return delay
