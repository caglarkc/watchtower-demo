"""Instantiate connectors from persisted source records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from watchtower.config.paths import PROJECT_ROOT
from watchtower.connectors.base import BaseConnector, ConnectorError
from watchtower.connectors.elasticsearch import ElasticsearchConnector
from watchtower.connectors.file_jsonl import FileJsonlConnector
from watchtower.connectors.server_stack import ServerStackConnector
from watchtower.connectors.wazuh import WazuhConnector
from watchtower.domain.tenant import SourceRecord


def build_connector(source: SourceRecord) -> BaseConnector:
    config = source.config
    connector_type = source.connector_type

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
        return ElasticsearchConnector(
            source.id,
            base_url=str(config["base_url"]),
            index=str(config.get("index", "corp-logs-*")),
            query=config.get("query"),
            http_get=config.get("http_get"),
            http_post=config.get("http_post"),
        )

    if connector_type == "wazuh":
        return WazuhConnector(
            source.id,
            api_url=str(config["api_url"]),
            username=config.get("username"),
            password=config.get("password"),
            token=config.get("token"),
            http_get=config.get("http_get"),
        )

    msg = f"Unknown connector type: {connector_type}"
    raise ConnectorError(msg)
