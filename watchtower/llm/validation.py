"""Structured output parsing and schema validation."""

from __future__ import annotations

import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from watchtower.llm.protocol import ProviderResponseError
from watchtower.llm.schemas import LLMTaskName, TASK_SCHEMA_REGISTRY

T = TypeVar("T", bound=BaseModel)

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def extract_json_text(raw: str) -> str:
    text = raw.strip()
    match = _JSON_BLOCK_RE.search(text)
    if match:
        return match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text


def parse_and_validate(task: LLMTaskName, raw: str) -> BaseModel:
    """Parse JSON and validate against the task schema."""
    schema_cls = TASK_SCHEMA_REGISTRY[task]
    try:
        payload: dict[str, Any] = json.loads(extract_json_text(raw))
    except json.JSONDecodeError as exc:
        msg = f"Invalid JSON for task {task}: {exc}"
        raise ProviderResponseError(msg, raw_text=raw) from exc
    try:
        return schema_cls.model_validate(payload)
    except ValidationError as exc:
        msg = f"Schema validation failed for task {task}"
        raise ProviderResponseError(msg, raw_text=raw) from exc
