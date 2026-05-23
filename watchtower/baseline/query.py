"""Baseline engine query API for decision path."""

from __future__ import annotations

from watchtower.baseline.engine import BaselineEngine
from watchtower.domain.profiles import BaselineEvaluation


class BaselineQueryAPI:
    """Thin query facade over BaselineEngine.evaluate."""

    def __init__(self, engine: BaselineEngine) -> None:
        self._engine = engine

    def evaluate_metric(
        self,
        tenant_id: str,
        metric_name: str,
        value: float,
        *,
        user_id: str | None = None,
        department_id: str | None = None,
        role_id: str | None = None,
        seniority: str = "worker",
    ) -> BaselineEvaluation:
        return self._engine.evaluate(
            tenant_id,
            metric_name,
            value,
            user_id=user_id,
            department_id=department_id,
            role_id=role_id,
            seniority=seniority,
        )
