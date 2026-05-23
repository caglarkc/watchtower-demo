"""Normalize raw events into unified schema."""

from __future__ import annotations

from typing import Any

from watchtower.domain.normalized_event import NormalizationOutcome
from watchtower.normalization.adapters import SimulationFixtureAdapter, adapter_for_connector


class NormalizationService:
    """LLM-free deterministic normalization path."""

    def normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        tenant_id: str,
        connector_type: str = "simulation_fixture",
        raw_event_id: str | None = None,
        source_id: str | None = None,
        source_path: str | None = None,
        context_feature_id: str | None = None,
    ) -> NormalizationOutcome:
        if connector_type == "simulation_fixture":
            adapter = SimulationFixtureAdapter()
        else:
            adapter = adapter_for_connector(connector_type)
        return adapter.normalize(
            payload,
            tenant_id=tenant_id,
            raw_event_id=raw_event_id,
            source_id=source_id,
            source_path=source_path,
            context_feature_id=context_feature_id,
        )
