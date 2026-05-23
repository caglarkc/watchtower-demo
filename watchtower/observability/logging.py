"""Structured JSON logs for operator and container log aggregation."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from watchtower.security.masking import mask_mapping, mask_text


def _classify_error(exc: BaseException | None, error_text: str | None) -> str | None:
    if exc is not None:
        return type(exc).__name__
    if error_text:
        lowered = error_text.lower()
        if "timeout" in lowered:
            return "TimeoutError"
        if "connection" in lowered:
            return "ConnectionError"
        if "auth" in lowered or "401" in lowered or "403" in lowered:
            return "AuthError"
        return "RuntimeError"
    return None


def emit_structured_log(
    logger: logging.Logger,
    level: int,
    message: str,
    *,
    tenant_id: str | None = None,
    source_id: str | None = None,
    run_id: str | None = None,
    graph_thread_id: str | None = None,
    event_counts: dict[str, int] | None = None,
    severity: str | None = None,
    error_class: str | None = None,
    exc: BaseException | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Emit one JSON log line with secret masking."""
    payload: dict[str, Any] = {
        "ts": datetime.now(UTC).isoformat(),
        "message": mask_text(message),
    }
    if tenant_id:
        payload["tenant_id"] = tenant_id
    if source_id:
        payload["source_id"] = source_id
    if run_id:
        payload["run_id"] = run_id
    if graph_thread_id:
        payload["graph_thread_id"] = graph_thread_id
    if event_counts:
        payload["event_counts"] = event_counts
    if severity:
        payload["severity"] = severity
    err_cls = error_class or _classify_error(exc, message if level >= logging.WARNING else None)
    if err_cls:
        payload["error_class"] = err_cls
    if extra:
        payload.update(mask_mapping(extra))
    logger.log(level, json.dumps(payload, ensure_ascii=False))
