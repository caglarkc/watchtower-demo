"""Policy and hard-rule evaluation (deterministic, no LLM)."""

from __future__ import annotations

from pydantic import BaseModel

from watchtower.domain.assessment import AssessmentInput, SeverityLevel
from watchtower.taxonomy.models import FeatureTaxonomyEntry

_FRONTEND_ROLE_IDS = frozenset({"frontend", "ui", "ui_dev", "web"})
_DB_RESOURCE_MARKERS = ("DB", "DATABASE", "SQL")
_DIRECT_DB_ACTIONS = frozenset(
    {"direct_sql", "sql_query", "db_connect", "database_query", "raw_sql"}
)


class PolicyResult(BaseModel):
    violated: bool = False
    severity_floor: SeverityLevel = "LOG"
    reason: str | None = None
    rule_key: str | None = None


class PolicyEngine:
    """Evaluate policy-rule and hard-rule violations."""

    def evaluate(
        self,
        inp: AssessmentInput,
        entry: FeatureTaxonomyEntry,
    ) -> PolicyResult:
        detection = entry.primary_detection_class

        if detection == "hard-rule":
            return PolicyResult(
                violated=True,
                severity_floor=entry.default_severity_floor,
                reason=f"hard-rule:{entry.feature_id}",
                rule_key=entry.feature_id,
            )

        if detection != "policy-rule":
            return PolicyResult(violated=False)

        if self._is_frontend_direct_db_access(inp):
            return PolicyResult(
                violated=True,
                severity_floor="CRITICAL",
                reason="frontend role direct database access bypasses application tier",
                rule_key="frontend_direct_db_access",
            )

        return PolicyResult(
            violated=True,
            severity_floor=entry.default_severity_floor,
            reason=f"policy-rule:{entry.feature_id}",
            rule_key=entry.feature_id,
        )

    @staticmethod
    def _is_frontend_direct_db_access(inp: AssessmentInput) -> bool:
        role = (inp.role_id or "").lower()
        if role not in _FRONTEND_ROLE_IDS:
            return False
        resource = (inp.resource or "").upper()
        if not any(marker in resource for marker in _DB_RESOURCE_MARKERS):
            return False
        action = (inp.action or "").lower()
        return action in _DIRECT_DB_ACTIONS
