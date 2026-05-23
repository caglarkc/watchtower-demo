"""Instantiate connectors from persisted source records."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from watchtower.config.paths import PROJECT_ROOT
from watchtower.connectors.base import BaseConnector, ConnectorError
from watchtower.connectors.elasticsearch import ElasticsearchConnector
from watchtower.connectors.file_jsonl import FileJsonlConnector
from watchtower.connectors.mock import MockConnector
from watchtower.connectors.server_stack import ServerStackConnector
from watchtower.connectors.wazuh import WazuhConnector
from watchtower.domain.events import RawEventRecord
from watchtower.domain.source import SourceRecord
from watchtower.sources.validation import validate_connector_config


def build_connector(source: SourceRecord) -> BaseConnector:
    config = source.config
    connector_type = source.connector_type
    validate_connector_config(connector_type, config)

    if connector_type == "server_stack":
        logs_root = Path(config.get("logs_root", PROJECT_ROOT / "server-stack" / "logs"))
        return ServerStackConnector(
            source.id,
            logs_root,
            include_globs=tuple(config.get("include_globs", ("**/*.jsonl", "**/*.log"))),
            max_files=config.get("max_files"),
        )

    if connector_type == "file_jsonl":
        file_path = Path(config["file_path"])
        return FileJsonlConnector(source.id, file_path)

    if connector_type == "elasticsearch":
        http_config = {
            k: config[k]
            for k in (
                "timeout_seconds",
                "max_retries",
                "backoff_base_seconds",
                "verify_tls",
                "ca_cert_path",
                "auth_type",
                "username",
                "password",
                "token",
                "api_key",
                "api_key_header",
                "api_key_prefix",
            )
            if k in config
        }
        return ElasticsearchConnector(
            source.id,
            base_url=str(config["base_url"]),
            index=str(config.get("index", "corp-logs-*")),
            query=config.get("query"),
            http_config=http_config,
            http_get=config.get("http_get"),
            http_post=config.get("http_post"),
        )

    if connector_type == "wazuh":
        return WazuhConnector(
            source.id,
            api_url=str(config["api_url"]),
            config=config,
            username=config.get("username"),
            password=config.get("password"),
            token=config.get("token"),
            time_window_minutes=int(config.get("time_window_minutes", 60)),
            http_get=config.get("http_get"),
            http_post=config.get("http_post"),
        )

    if connector_type == "mock":
        raw_events = config.get("events", [])
        events = [
            e if isinstance(e, RawEventRecord) else RawEventRecord.model_validate(e)
            for e in raw_events
        ]
        return MockConnector(
            source.id,
            events=events,
            fail_health=bool(config.get("fail_health", False)),
            fail_poll=bool(config.get("fail_poll", False)),
        )

    msg = f"Unknown connector type: {connector_type}"
    raise ConnectorError(msg)
