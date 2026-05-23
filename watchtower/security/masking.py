"""Secret masking for logs, audit, and CLI output."""

from __future__ import annotations

import re
from typing import Any

_SENSITIVE_KEY_RE = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|authorization|credential)",
    re.IGNORECASE,
)
_MASK = "***REDACTED***"


def mask_secret(value: str | None) -> str | None:
    if value is None or value == "":
        return value
    if len(value) <= 4:
        return _MASK
    return f"{value[:2]}…{_MASK}"


def mask_mapping(data: dict[str, Any]) -> dict[str, Any]:
    masked: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            masked[key] = mask_mapping(value)
        elif isinstance(value, list):
            masked[key] = [
                mask_mapping(item) if isinstance(item, dict) else item for item in value
            ]
        elif _SENSITIVE_KEY_RE.search(str(key)):
            masked[key] = _MASK if value is not None else None
        else:
            masked[key] = value
    return masked


def mask_text(text: str) -> str:
    """Best-effort masking of bearer tokens and key=value secrets in free text."""
    text = re.sub(
        r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*\S+",
        lambda m: m.group(0).split("=")[0] + f"={_MASK}",
        text,
    )
    text = re.sub(r"Bearer\s+\S+", f"Bearer {_MASK}", text, flags=re.IGNORECASE)
    return text
