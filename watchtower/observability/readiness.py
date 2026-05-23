"""Production readiness payload including metrics and optional soak evidence."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from watchtower import __version__
from watchtower.config.settings import WatchtowerSettings
from watchtower.health.service import HealthService
from watchtower.observability.service import MetricsService


def build_production_readiness_report(
    *,
    conn: Any,
    settings: WatchtowerSettings,
    session: Any | None,
    metrics: MetricsService | None,
    tenant_id: str | None,
    soak_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    health = HealthService().run(
        conn=conn,
        settings=settings,
        session=session,
    )
    metrics_payload: dict[str, Any] | None = None
    if metrics is not None and tenant_id:
        metrics_payload = metrics.snapshot(tenant_id).to_dict()
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "version": __version__,
        "health": health.to_dict(),
        "metrics": metrics_payload,
        "soak": soak_summary,
    }
