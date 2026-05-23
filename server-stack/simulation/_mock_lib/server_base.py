"""Shared HTTP mock server utilities for Phase 3 simulation services."""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Callable


def append_log(log_path: Path, payload: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def run_http_server(port: int, handler_cls: type[BaseHTTPRequestHandler], baseline: Callable[[], None] | None = None) -> None:
    if baseline:
        baseline()
        def loop() -> None:
            while True:
                baseline()
                time.sleep(60)
        threading.Thread(target=loop, daemon=True).start()
    HTTPServer(("0.0.0.0", port), handler_cls).serve_forever()
