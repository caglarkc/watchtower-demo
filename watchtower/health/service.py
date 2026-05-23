"""Aggregate health checks for CLI and container probes."""

from __future__ import annotations

import json
import shutil
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from watchtower import __version__
from watchtower.config.settings import WatchtowerSettings
from watchtower.llm.providers.onboarding import resolve_provider_chain
from watchtower.observability.metrics import (
    METRIC_LOOP_DURATION_LAST,
    METRIC_SOURCE_ERRORS,
)
from watchtower.storage.migrations.runner import MigrationRunner

HealthStatus = Literal["healthy", "degraded", "unhealthy"]


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthReport:
    status: HealthStatus
    version: str
    checks: list[HealthCheck] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "version": self.version,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class HealthService:
    def run(
        self,
        *,
        conn: sqlite3.Connection,
        settings: WatchtowerSettings,
        session: Any | None = None,
    ) -> HealthReport:
        checks: list[HealthCheck] = []
        checks.append(self._check_database(settings.database_path))
        checks.append(self._check_migrations(conn, settings))
        checks.append(self._check_disk(settings))
        if session is not None:
            checks.extend(self._check_runtime(session, settings, conn))
            tenant = session.bootstrap_service.get_default_tenant()
            if tenant is not None and hasattr(session, "metrics"):
                checks.append(self._check_metrics(session, tenant.id))
        status = _aggregate_status(checks)
        return HealthReport(status=status, version=__version__, checks=checks)

    @staticmethod
    def _check_database(db_path: Path) -> HealthCheck:
        if not db_path.exists():
            return HealthCheck(
                "database",
                "degraded",
                "database file not created yet (fresh install)",
                {"path": str(db_path)},
            )
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute("SELECT 1")
        except sqlite3.Error as exc:
            return HealthCheck("database", "unhealthy", str(exc), {"path": str(db_path)})
        return HealthCheck("database", "healthy", "sqlite reachable", {"path": str(db_path)})

    @staticmethod
    def _check_migrations(conn: sqlite3.Connection, settings: WatchtowerSettings) -> HealthCheck:
        runner = MigrationRunner(settings.migrations_dir)
        pending = runner.list_pending(conn)
        if pending:
            return HealthCheck(
                "migrations",
                "unhealthy",
                f"{len(pending)} pending migration(s)",
                {"pending": [p.stem for p in pending]},
            )
        return HealthCheck("migrations", "healthy", "schema up to date")

    @staticmethod
    def _check_disk(settings: WatchtowerSettings) -> HealthCheck:
        db_parent = settings.database_path.parent
        db_parent.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(db_parent)
        free_pct = (usage.free / usage.total) * 100 if usage.total else 100.0
        status: HealthStatus = "healthy"
        if free_pct < 5:
            status = "unhealthy"
        elif free_pct < 15:
            status = "degraded"
        return HealthCheck(
            "disk",
            status,
            f"{free_pct:.1f}% free on data volume",
            {"free_bytes": usage.free, "total_bytes": usage.total},
        )

    def _check_runtime(
        self,
        session: Any,
        settings: WatchtowerSettings,
        conn: sqlite3.Connection,
    ) -> list[HealthCheck]:
        checks: list[HealthCheck] = []
        tenant = session.bootstrap_service.get_default_tenant()
        if tenant is None:
            checks.append(
                HealthCheck("bootstrap", "degraded", "not bootstrapped — run wt bootstrap")
            )
        else:
            bootstrapped = session.bootstrap_service.is_bootstrapped(tenant.id)
            checks.append(
                HealthCheck(
                    "bootstrap",
                    "healthy" if bootstrapped else "degraded",
                    "bootstrapped" if bootstrapped else "bootstrap admin missing",
                    {"tenant_id": tenant.id},
                )
            )
            sources = session.sources.list_for_tenant(tenant.id)
            unhealthy = 0
            for source in sources:
                health = session.ingest.check_health(source)
                if health.status == "unhealthy":
                    unhealthy += 1
            src_status: HealthStatus = "healthy"
            if unhealthy and unhealthy == len(sources) and sources:
                src_status = "unhealthy"
            elif unhealthy:
                src_status = "degraded"
            checks.append(
                HealthCheck(
                    "sources",
                    src_status,
                    f"{len(sources)} source(s), {unhealthy} unhealthy",
                    {"registered": len(sources), "unhealthy": unhealthy},
                )
            )

        providers = resolve_provider_chain(settings, conn)
        if not providers:
            checks.append(
                HealthCheck(
                    "providers",
                    "degraded",
                    "no LLM providers configured (fail-open only)",
                )
            )
        else:
            checks.append(
                HealthCheck(
                    "providers",
                    "healthy",
                    "provider chain available",
                    {"providers": [p.name for p in providers]},
                )
            )
        return checks

    @staticmethod
    def _check_metrics(session: Any, tenant_id: str) -> HealthCheck:
        snap = session.metrics.snapshot(tenant_id)
        source_errors = int(snap.get(METRIC_SOURCE_ERRORS))
        loop_last = snap.get(METRIC_LOOP_DURATION_LAST)
        details = snap.to_dict()
        if source_errors >= 10:
            return HealthCheck(
                "metrics",
                "degraded",
                f"elevated source_errors_total={source_errors}",
                details,
            )
        if source_errors >= 1:
            return HealthCheck(
                "metrics",
                "degraded",
                f"recent source_errors_total={source_errors}",
                details,
            )
        msg = "runtime metrics nominal"
        if loop_last:
            msg = f"{msg}; last loop {loop_last:.0f}ms"
        return HealthCheck("metrics", "healthy", msg, details)


def _aggregate_status(checks: list[HealthCheck]) -> HealthStatus:
    if any(c.status == "unhealthy" for c in checks):
        return "unhealthy"
    if any(c.status == "degraded" for c in checks):
        return "degraded"
    return "healthy"
