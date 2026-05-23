"""E2E coverage report writer."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from watchtower.config.paths import PROJECT_ROOT

REPORT_DIR = PROJECT_ROOT / "reports" / "watchtower"


def write_e2e_summary(summary: dict[str, Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / "e2e_summary.json"
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        **summary,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
