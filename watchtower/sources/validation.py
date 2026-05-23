"""Validate ingest source configs before persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def validate_connector_config(connector_type: str, config: dict[str, Any]) -> None:
    """Raise ValueError when config is invalid for the connector type."""
    if connector_type == "file_jsonl":
        _validate_file_jsonl(config)
    elif connector_type == "elasticsearch":
        _validate_elasticsearch(config)
    elif connector_type == "wazuh":
        _validate_wazuh(config)
    elif connector_type == "server_stack":
        _validate_server_stack(config)
    elif connector_type == "mock":
        return
    else:
        msg = f"unsupported connector: {connector_type}"
        raise ValueError(msg)


def _require_str(config: dict[str, Any], key: str) -> str:
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        msg = f"config.{key} must be a non-empty string"
        raise ValueError(msg)
    return value.strip()


def _validate_url(url: str, *, field_name: str = "url") -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        msg = f"{field_name} must use http or https scheme"
        raise ValueError(msg)
    if not parsed.netloc:
        msg = f"{field_name} must include host"
        raise ValueError(msg)


def _validate_file_jsonl(config: dict[str, Any]) -> None:
    path_str = _require_str(config, "file_path")
    path = Path(path_str)
    if path.exists() and not path.is_file():
        msg = f"file_path is not a file: {path_str}"
        raise ValueError(msg)
    limit = config.get("poll_limit")
    if limit is not None and (not isinstance(limit, int) or limit < 1):
        msg = "poll_limit must be a positive integer"
        raise ValueError(msg)


def _validate_elasticsearch(config: dict[str, Any]) -> None:
    base_url = _require_str(config, "base_url")
    _validate_url(base_url, field_name="base_url")
    index = config.get("index", "corp-logs-*")
    if not isinstance(index, str) or not index.strip():
        msg = "config.index must be a non-empty string"
        raise ValueError(msg)
    auth_type = config.get("auth_type")
    if auth_type is not None and auth_type not in {"basic", "bearer", "api_key"}:
        msg = "auth_type must be basic, bearer, or api_key"
        raise ValueError(msg)
    if auth_type == "basic" and not (config.get("username") and config.get("password")):
        msg = "basic auth requires username and password"
        raise ValueError(msg)
    if auth_type == "api_key" and not config.get("api_key"):
        msg = "api_key auth requires api_key"
        raise ValueError(msg)
    timeout = config.get("timeout_seconds")
    if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
        msg = "timeout_seconds must be positive"
        raise ValueError(msg)


def _validate_wazuh(config: dict[str, Any]) -> None:
    api_url = _require_str(config, "api_url")
    _validate_url(api_url, field_name="api_url")
    has_token = bool(config.get("token"))
    has_basic = bool(config.get("username")) and bool(config.get("password"))
    if not has_token and not has_basic:
        msg = "wazuh config requires token or username+password"
        raise ValueError(msg)
    window = config.get("time_window_minutes")
    if window is not None and (not isinstance(window, int) or window < 1):
        msg = "time_window_minutes must be a positive integer"
        raise ValueError(msg)


def _validate_server_stack(config: dict[str, Any]) -> None:
    logs_root = _require_str(config, "logs_root")
    path = Path(logs_root)
    if path.exists() and not path.is_dir():
        msg = f"logs_root must be a directory: {logs_root}"
        raise ValueError(msg)
    globs = config.get("include_globs")
    if globs is not None and not isinstance(globs, list):
        msg = "include_globs must be a list of glob strings"
        raise ValueError(msg)
