"""Store-backed natural language operator queries (deterministic, auditable)."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from typing import Any

from watchtower.storage.repositories.alerts import AlertRepository
from watchtower.storage.repositories.baseline import BaselineRepository


class QueryService:
    """Answer operator questions from local store data only."""

    def __init__(
        self,
        alerts: AlertRepository,
        baseline: BaselineRepository,
    ) -> None:
        self._alerts = alerts
        self._baseline = baseline

    def answer(self, tenant_id: str, query_text: str) -> dict[str, Any]:
        lowered = query_text.lower()
        since = self._parse_time_window(lowered)
        sources: list[dict[str, Any]] = []

        severity = None
        if "critical" in lowered or "kritik" in lowered:
            severity = "CRITICAL"
        elif "alert" in lowered and "warning" not in lowered:
            severity = "ALERT"

        department = None
        dept_match = re.search(r"backend|muhasebe|engineering|ops", lowered)
        if dept_match:
            department = dept_match.group(0)
            if department == "muhasebe":
                department = "accounting"

        alerts = self._alerts.list_alerts(
            tenant_id,
            severity=severity,
            department_id=department,
            since=since,
            limit=50,
        )
        sources.append({"type": "alerts", "count": len(alerts)})

        silent = self._alerts.list_silent_findings(tenant_id, since=since, limit=50)
        sources.append({"type": "silent_findings", "count": len(silent)})

        lines = [
            f"Query: {query_text}",
            f"Window: {'last 24h' if since else 'all time'}",
            f"Alerts matched: {len(alerts)}",
        ]
        if alerts:
            lines.append("Top alerts:")
            for alert in alerts[:5]:
                lines.append(
                    f"  - {alert.id[:8]} {alert.severity} {alert.status} "
                    f"{alert.feature_id} {alert.title}"
                )
        else:
            lines.append("No alerts matched the query filters.")

        if "silent" in lowered or "learn" in lowered or "bulgu" in lowered:
            lines.append(f"Silent findings in window: {len(silent)}")

        if "baseline" in lowered or "profil" in lowered:
            users = self._baseline.list_user_profiles(tenant_id)
            sources.append({"type": "user_profiles", "count": len(users)})
            lines.append(f"User baseline profiles stored: {len(users)}")

        answer_text = "\n".join(lines)
        query_id = self._alerts.new_id()
        self._alerts.insert_operator_query(
            query_id=query_id,
            tenant_id=tenant_id,
            query_text=query_text,
            answer_text=answer_text,
            sources=sources,
        )
        return {
            "query_id": query_id,
            "answer": answer_text,
            "sources": sources,
            "auditable": True,
        }

    @staticmethod
    def _parse_time_window(lowered: str) -> datetime | None:
        if "24" in lowered or "son 24" in lowered or "last 24" in lowered:
            return datetime.now(UTC) - timedelta(hours=24)
        if "7d" in lowered or "7 gün" in lowered or "7 gun" in lowered:
            return datetime.now(UTC) - timedelta(days=7)
        return None
