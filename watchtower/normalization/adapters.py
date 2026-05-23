"""Known schema adapters (deterministic, no LLM)."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from watchtower.domain.normalized_event import NormalizationOutcome, NormalizedEvent, UnknownSchemaEntry
from watchtower.domain.normalized_event import SchemaFormat
from watchtower.normalization.registry import resolve_feature_hint


def _parse_timestamp(payload: dict[str, Any]) -> datetime | None:
    for key in ("timestamp", "ts", "@timestamp", "event_time", "occurred_at"):
        value = payload.get(key)
        if value is None:
            continue
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            continue
    return None


def _schema_signature(payload: dict[str, Any]) -> str:
    keys = sorted(payload.keys())
    material = json.dumps(keys, ensure_ascii=False)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def _actor_from_payload(payload: dict[str, Any]) -> str | None:
    for key in ("user", "username", "actor", "id.orig_h", "agent", "account"):
        value = payload.get(key)
        if value is not None and str(value).strip():
            return str(value)
    return None


def _resource_from_payload(payload: dict[str, Any], event_type: str) -> str:
    for key in (
        "resource",
        "target",
        "share",
        "host",
        "id.resp_h",
        "path",
        "index",
        "mailbox",
        "domain",
    ):
        value = payload.get(key)
        if value is not None and str(value).strip():
            return str(value)
    channel = payload.get("log_channel") or payload.get("_log_channel")
    if channel:
        return f"{channel}/{event_type}"
    return event_type


def _event_type_from_payload(payload: dict[str, Any]) -> str | None:
    for key in ("event_type", "detection_type", "event_id"):
        if payload.get(key) is not None:
            return str(payload[key])
    if payload.get("_raw") and not payload.get("event_type"):
        return "raw_log_line"
    return None


class BaseAdapter:
    schema_format: SchemaFormat

    def normalize(
        self,
        payload: dict[str, Any],
        *,
        tenant_id: str,
        raw_event_id: str | None = None,
        source_id: str | None = None,
        source_path: str | None = None,
        context_feature_id: str | None = None,
    ) -> NormalizationOutcome:
        if not isinstance(payload, dict) or not payload:
            return NormalizationOutcome(
                unknown=UnknownSchemaEntry(
                    tenant_id=tenant_id,
                    raw_event_id=raw_event_id,
                    schema_signature="empty",
                    payload_sample={},
                    reason="empty payload",
                )
            )

        event_type = _event_type_from_payload(payload)
        if event_type is None:
            return NormalizationOutcome(
                unknown=UnknownSchemaEntry(
                    tenant_id=tenant_id,
                    raw_event_id=raw_event_id,
                    schema_signature=_schema_signature(payload),
                    payload_sample=dict(list(payload.items())[:12]),
                    reason="missing event_type/detection_type",
                )
            )

        occurred_at = _parse_timestamp(payload) or datetime.now(UTC)
        actor = _actor_from_payload(payload)
        action = event_type
        resource = _resource_from_payload(payload, event_type)
        feature_hint = resolve_feature_hint(
            payload, context_feature_id=context_feature_id
        )
        channel = payload.get("log_channel") or payload.get("_log_channel")
        if channel is None and source_path:
            channel = source_path.split("/")[-2] if "/" in source_path else None

        normalized = NormalizedEvent(
            tenant_id=tenant_id,
            raw_event_id=raw_event_id,
            source_id=source_id,
            schema_format=self.schema_format,
            event_type=event_type,
            actor=actor,
            action=action,
            resource=resource,
            occurred_at=occurred_at,
            feature_hint=feature_hint,
            scenario_id=payload.get("scenario_id"),
            source_path=source_path or payload.get("_source_path"),
            channel=str(channel) if channel else None,
            anomaly_flag=bool(payload.get("anomaly", False)),
            attributes={
                k: v
                for k, v in payload.items()
                if k
                not in {
                    "timestamp",
                    "ts",
                    "@timestamp",
                    "user",
                    "event_type",
                    "detection_type",
                }
            },
        )
        return NormalizationOutcome(normalized=normalized)


class ServerStackAdapter(BaseAdapter):
    schema_format: SchemaFormat = "server_stack"


class FileJsonlAdapter(BaseAdapter):
    schema_format: SchemaFormat = "file_jsonl"


class ElasticsearchAdapter(BaseAdapter):
    schema_format: SchemaFormat = "elasticsearch"


class WazuhAdapter(BaseAdapter):
    schema_format: SchemaFormat = "wazuh"


class SimulationFixtureAdapter(BaseAdapter):
    schema_format: SchemaFormat = "simulation_fixture"


ADAPTER_BY_FORMAT: dict[str, BaseAdapter] = {
    "server_stack": ServerStackAdapter(),
    "file_jsonl": FileJsonlAdapter(),
    "elasticsearch": ElasticsearchAdapter(),
    "wazuh": WazuhAdapter(),
    "simulation_fixture": SimulationFixtureAdapter(),
}

CONNECTOR_TO_FORMAT: dict[str, SchemaFormat] = {
    "server_stack": "server_stack",
    "file_jsonl": "file_jsonl",
    "elasticsearch": "elasticsearch",
    "wazuh": "wazuh",
    "mock": "simulation_fixture",
}


def adapter_for_connector(connector_type: str) -> BaseAdapter:
    fmt = CONNECTOR_TO_FORMAT.get(connector_type, "server_stack")
    return ADAPTER_BY_FORMAT[fmt]
