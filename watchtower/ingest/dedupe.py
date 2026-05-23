"""Deduplication key helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def dedupe_key_from_parts(*parts: str) -> str:
    material = "\x1f".join(parts)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def dedupe_key_for_file_line(source_id: str, path: str, line_number: int, line: str) -> str:
    line_hash = hashlib.sha256(line.encode("utf-8")).hexdigest()[:16]
    return dedupe_key_from_parts(source_id, path, str(line_number), line_hash)


def dedupe_key_for_payload(source_id: str, path: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    payload_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return dedupe_key_from_parts(source_id, path, payload_hash)


def dedupe_key_for_es_doc(source_id: str, index: str, doc_id: str) -> str:
    return dedupe_key_from_parts(source_id, index, doc_id)
