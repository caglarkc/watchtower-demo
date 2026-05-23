"""LLM must not be bound to decision engine."""

from __future__ import annotations

import inspect

from watchtower.decision.service import DecisionService
from watchtower.llm.schemas import FORBIDDEN_TASK_NAMES, TASK_SCHEMA_REGISTRY


def test_llm_decision_schema_not_registered():
    for forbidden in FORBIDDEN_TASK_NAMES:
        assert forbidden not in TASK_SCHEMA_REGISTRY


def test_decision_service_does_not_import_llm_gateway():
    source = inspect.getsource(DecisionService.assess)
    assert "llm" not in source.lower()
    assert "LLMGateway" not in source
