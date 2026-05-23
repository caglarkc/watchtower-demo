"""Shared HTTP client for connectors: auth, TLS, timeout, retry/backoff."""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable

from watchtower.connectors.base import ConnectorError


@dataclass
class HttpClientConfig:
    timeout_seconds: float = 10.0
    max_retries: int = 2
    backoff_base_seconds: float = 0.5
    verify_tls: bool = True
    ca_cert_path: str | None = None
    auth_type: str | None = None  # basic | bearer | api_key
    username: str | None = None
    password: str | None = None
    token: str | None = None
    api_key: str | None = None
    api_key_header: str = "Authorization"
    api_key_prefix: str = "ApiKey"


@dataclass
class HttpCallStats:
    retries: int = 0
    last_latency_ms: float | None = None


class ConnectorHttpClient:
    """Synchronous HTTP helper with production auth/TLS/retry behavior."""

    def __init__(
        self,
        config: HttpClientConfig | None = None,
        *,
        http_get: Callable[[str, dict[str, str]], dict[str, Any]] | None = None,
        http_post: Callable[[str, dict[str, Any], dict[str, str]], dict[str, Any]] | None = None,
    ) -> None:
        self._config = config or HttpClientConfig()
        self._stats = HttpCallStats()
        self._http_get = http_get
        self._http_post = http_post

    @property
    def stats(self) -> HttpCallStats:
        return self._stats

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> dict[str, Any]:
        if self._http_get is not None:
            return self._http_get(url, headers or {})
        return self._request("GET", url, body=None, extra_headers=headers)

    def post(
        self,
        url: str,
        body: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if self._http_post is not None:
            return self._http_post(url, body, headers or {})
        return self._request("POST", url, body=body, extra_headers=headers)

    def auth_headers(self) -> dict[str, str]:
        cfg = self._config
        headers: dict[str, str] = {}
        if cfg.auth_type == "bearer" and cfg.token:
            headers["Authorization"] = f"Bearer {cfg.token}"
        elif cfg.auth_type == "api_key" and cfg.api_key:
            prefix = cfg.api_key_prefix.strip()
            value = f"{prefix} {cfg.api_key}".strip() if prefix else cfg.api_key
            headers[cfg.api_key_header] = value
        elif cfg.auth_type == "basic" and cfg.username and cfg.password:
            import base64

            token = base64.b64encode(
                f"{cfg.username}:{cfg.password}".encode("utf-8")
            ).decode("ascii")
            headers["Authorization"] = f"Basic {token}"
        elif cfg.token and not cfg.auth_type:
            headers["Authorization"] = f"Bearer {cfg.token}"
        return headers

    def _request(
        self,
        method: str,
        url: str,
        *,
        body: dict[str, Any] | None,
        extra_headers: dict[str, str] | None,
    ) -> dict[str, Any]:
        cfg = self._config
        headers = {**self.auth_headers(), **(extra_headers or {})}
        data = json.dumps(body).encode("utf-8") if body is not None else None
        if body is not None:
            headers.setdefault("Content-Type", "application/json")

        last_error: Exception | None = None
        for attempt in range(cfg.max_retries + 1):
            if attempt > 0:
                self._stats.retries += 1
                delay = cfg.backoff_base_seconds * (2 ** (attempt - 1))
                time.sleep(delay)
            started = time.monotonic()
            request = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(
                    request,
                    timeout=cfg.timeout_seconds,
                    context=self._ssl_context(),
                ) as response:
                    raw = response.read().decode("utf-8")
                    self._stats.last_latency_ms = (time.monotonic() - started) * 1000
                    if not raw.strip():
                        return {}
                    return json.loads(raw)
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code in {429, 502, 503, 504} and attempt < cfg.max_retries:
                    continue
                raise ConnectorError(f"HTTP {exc.code}: {exc.reason}") from exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < cfg.max_retries:
                    continue
                raise ConnectorError(str(exc)) from exc
        raise ConnectorError(str(last_error or "request failed"))

    def _ssl_context(self) -> ssl.SSLContext | None:
        cfg = self._config
        if not cfg.verify_tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return ctx
        if cfg.ca_cert_path:
            return ssl.create_default_context(cafile=cfg.ca_cert_path)
        return None
