"""Provider-independent LLM gateway with retry, fallback, and fail-open."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from watchtower.llm.protocol import (
    LLMProvider,
    ProviderResponseError,
    ProviderUnavailableError,
)
from watchtower.llm.schemas import (
    LLMTaskName,
    assert_task_allowed,
    task_json_schema,
)
from watchtower.llm.validation import parse_and_validate
from watchtower.storage.repositories.llm_audit import LLMCallAuditRepository

FAIL_OPEN_NOTE = "LLM unavailable - manual review required"


@dataclass
class LLMGatewayResult:
    success: bool
    task: LLMTaskName
    data: BaseModel | None = None
    provider: str | None = None
    model: str | None = None
    attempts: int = 0
    fail_open: bool = False
    note: str | None = None
    audit_id: str | None = None
    errors: list[str] = field(default_factory=list)


class LLMGateway:
    """Structured LLM calls with validation, retry (max 2), fallback, and audit."""

    def __init__(
        self,
        providers: list[LLMProvider],
        *,
        audit_repo: LLMCallAuditRepository | None = None,
        max_retries: int = 2,
    ) -> None:
        if not providers:
            msg = "At least one LLM provider is required"
            raise ValueError(msg)
        self._providers = providers
        self._audit = audit_repo
        self._max_retries = max(0, min(max_retries, 2))

    @property
    def provider_names(self) -> list[str]:
        return [p.name for p in self._providers]

    def invoke(
        self,
        task: str,
        prompt: str,
        *,
        tenant_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> LLMGatewayResult:
        allowed_task = assert_task_allowed(task)
        schema = task_json_schema(allowed_task)
        errors: list[str] = []
        total_attempts = 0

        for provider in self._providers:
            for attempt in range(self._max_retries + 1):
                total_attempts += 1
                try:
                    response = provider.complete_structured(
                        task=allowed_task,
                        prompt=prompt,
                        json_schema=schema,
                        max_tokens=2048,
                    )
                    validated = parse_and_validate(allowed_task, response.raw_text)
                    audit_id = self._write_audit(
                        tenant_id=tenant_id,
                        task=allowed_task,
                        provider=provider.name,
                        model=response.model,
                        success=True,
                        attempts=attempt + 1,
                        prompt=prompt,
                        context=context,
                        response=validated.model_dump(),
                        error=None,
                    )
                    return LLMGatewayResult(
                        success=True,
                        task=allowed_task,
                        data=validated,
                        provider=provider.name,
                        model=response.model,
                        attempts=attempt + 1,
                        audit_id=audit_id,
                    )
                except (ProviderUnavailableError, ProviderResponseError) as exc:
                    errors.append(f"{provider.name}[{attempt}]: {exc}")
                    if attempt < self._max_retries:
                        continue
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{provider.name}[{attempt}]: {exc}")
                    if attempt < self._max_retries:
                        continue

        audit_id = self._write_audit(
            tenant_id=tenant_id,
            task=allowed_task,
            provider=None,
            model=None,
            success=False,
            attempts=total_attempts,
            prompt=prompt,
            context=context,
            response=None,
            error="; ".join(errors) or "all providers failed",
        )
        return LLMGatewayResult(
            success=False,
            task=allowed_task,
            fail_open=True,
            note=FAIL_OPEN_NOTE,
            attempts=total_attempts,
            audit_id=audit_id,
            errors=errors,
        )

    def _write_audit(
        self,
        *,
        tenant_id: str | None,
        task: LLMTaskName,
        provider: str | None,
        model: str | None,
        success: bool,
        attempts: int,
        prompt: str,
        context: dict[str, Any] | None,
        response: dict[str, Any] | None,
        error: str | None,
    ) -> str | None:
        if self._audit is None:
            return None
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        return self._audit.insert(
            audit_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            task_name=task,
            provider=provider,
            model=model,
            success=success,
            attempts=attempts,
            prompt_hash=prompt_hash,
            request_json=json.dumps(
                {"task": task, "context": context or {}}, ensure_ascii=False
            ),
            response_json=json.dumps(response, ensure_ascii=False) if response else None,
            error=error,
            created_at=datetime.now(UTC),
        )
