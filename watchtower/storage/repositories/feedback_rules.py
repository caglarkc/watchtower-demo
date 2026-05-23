"""Feedback and rule persistence."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime

from watchtower.domain.rules import (
    FeedbackEvent,
    FeedbackRule,
    PendingRule,
    RuleApproval,
    RuleEffect,
    RuleScope,
)


def _scope_to_json(scope: RuleScope) -> str:
    return scope.model_dump_json()


def _scope_from_json(raw: str) -> RuleScope:
    return RuleScope.model_validate_json(raw or "{}")


def _effect_to_json(effect: RuleEffect) -> str:
    return effect.model_dump_json()


def _effect_from_json(raw: str) -> RuleEffect:
    return RuleEffect.model_validate_json(raw or "{}")


class FeedbackRulesRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def insert_feedback_event(self, event: FeedbackEvent) -> str:
        self._conn.execute(
            """
            INSERT INTO feedback_events (
                id, tenant_id, kind, actor_id, actor_role, feature_id,
                detection_class, candidate_id, scope_json, comment,
                metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.id,
                event.tenant_id,
                event.kind,
                event.actor_id,
                event.actor_role,
                event.feature_id,
                event.detection_class,
                event.candidate_id,
                _scope_to_json(event.scope),
                event.comment,
                json.dumps(event.metadata, ensure_ascii=False),
                event.created_at.isoformat(),
            ),
        )
        return event.id

    def insert_pending_rule(self, rule: PendingRule) -> str:
        self._conn.execute(
            """
            INSERT INTO pending_rules (
                id, tenant_id, feedback_event_id, status, scope_json, effect_json,
                proposed_by, proposed_role, requires_policy_suppression_approval,
                expires_at, created_at, reviewed_at, reviewed_by, review_comment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rule.id,
                rule.tenant_id,
                rule.feedback_event_id,
                rule.status,
                _scope_to_json(rule.scope),
                _effect_to_json(rule.effect),
                rule.proposed_by,
                rule.proposed_role,
                1 if rule.requires_policy_suppression_approval else 0,
                rule.expires_at.isoformat() if rule.expires_at else None,
                rule.created_at.isoformat(),
                rule.reviewed_at.isoformat() if rule.reviewed_at else None,
                rule.reviewed_by,
                rule.review_comment,
            ),
        )
        return rule.id

    def update_pending_rule(self, rule: PendingRule) -> None:
        self._conn.execute(
            """
            UPDATE pending_rules SET
                status = ?, reviewed_at = ?, reviewed_by = ?, review_comment = ?
            WHERE id = ? AND tenant_id = ?
            """,
            (
                rule.status,
                rule.reviewed_at.isoformat() if rule.reviewed_at else None,
                rule.reviewed_by,
                rule.review_comment,
                rule.id,
                rule.tenant_id,
            ),
        )

    def get_pending_rule(self, tenant_id: str, rule_id: str) -> PendingRule | None:
        row = self._conn.execute(
            "SELECT * FROM pending_rules WHERE tenant_id = ? AND id = ?",
            (tenant_id, rule_id),
        ).fetchone()
        return self._pending_from_row(row) if row else None

    def list_pending_rules(
        self, tenant_id: str, *, status: str | None = "pending"
    ) -> list[PendingRule]:
        if status:
            rows = self._conn.execute(
                """
                SELECT * FROM pending_rules
                WHERE tenant_id = ? AND status = ?
                ORDER BY created_at
                """,
                (tenant_id, status),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM pending_rules WHERE tenant_id = ? ORDER BY created_at",
                (tenant_id,),
            ).fetchall()
        return [self._pending_from_row(r) for r in rows]

    def insert_feedback_rule(self, rule: FeedbackRule) -> str:
        self._conn.execute(
            """
            INSERT INTO feedback_rules (
                id, tenant_id, pending_rule_id, feedback_event_id,
                scope_json, effect_json, approved_by, approved_at,
                expires_at, active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rule.id,
                rule.tenant_id,
                rule.pending_rule_id,
                rule.feedback_event_id,
                _scope_to_json(rule.scope),
                _effect_to_json(rule.effect),
                rule.approved_by,
                rule.approved_at.isoformat(),
                rule.expires_at.isoformat() if rule.expires_at else None,
                1 if rule.active else 0,
            ),
        )
        return rule.id

    def list_active_feedback_rules(self, tenant_id: str) -> list[FeedbackRule]:
        rows = self._conn.execute(
            """
            SELECT * FROM feedback_rules
            WHERE tenant_id = ? AND active = 1
            ORDER BY approved_at DESC
            """,
            (tenant_id,),
        ).fetchall()
        return [self._feedback_rule_from_row(r) for r in rows]

    def deactivate_feedback_rule(self, tenant_id: str, rule_id: str) -> None:
        self._conn.execute(
            "UPDATE feedback_rules SET active = 0 WHERE tenant_id = ? AND id = ?",
            (tenant_id, rule_id),
        )

    def insert_rule_approval(self, approval: RuleApproval) -> str:
        self._conn.execute(
            """
            INSERT INTO rule_approvals (
                id, tenant_id, pending_rule_id, decision, approver_id,
                approver_role, allow_policy_suppression, comment, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                approval.id,
                approval.tenant_id,
                approval.pending_rule_id,
                approval.decision,
                approval.approver_id,
                approval.approver_role,
                1 if approval.allow_policy_suppression else 0,
                approval.comment,
                approval.created_at.isoformat(),
            ),
        )
        return approval.id

    def list_rule_approvals(self, tenant_id: str, pending_rule_id: str) -> list[RuleApproval]:
        rows = self._conn.execute(
            """
            SELECT * FROM rule_approvals
            WHERE tenant_id = ? AND pending_rule_id = ?
            ORDER BY created_at
            """,
            (tenant_id, pending_rule_id),
        ).fetchall()
        return [self._approval_from_row(r) for r in rows]

    def _pending_from_row(self, row: sqlite3.Row) -> PendingRule:
        return PendingRule(
            id=row["id"],
            tenant_id=row["tenant_id"],
            feedback_event_id=row["feedback_event_id"],
            status=row["status"],
            scope=_scope_from_json(row["scope_json"]),
            effect=_effect_from_json(row["effect_json"]),
            proposed_by=row["proposed_by"],
            proposed_role=row["proposed_role"],
            requires_policy_suppression_approval=bool(
                row["requires_policy_suppression_approval"]
            ),
            expires_at=(
                datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None
            ),
            created_at=datetime.fromisoformat(row["created_at"]),
            reviewed_at=(
                datetime.fromisoformat(row["reviewed_at"]) if row["reviewed_at"] else None
            ),
            reviewed_by=row["reviewed_by"],
            review_comment=row["review_comment"],
        )

    def _feedback_rule_from_row(self, row: sqlite3.Row) -> FeedbackRule:
        return FeedbackRule(
            id=row["id"],
            tenant_id=row["tenant_id"],
            pending_rule_id=row["pending_rule_id"],
            feedback_event_id=row["feedback_event_id"],
            scope=_scope_from_json(row["scope_json"]),
            effect=_effect_from_json(row["effect_json"]),
            approved_by=row["approved_by"],
            approved_at=datetime.fromisoformat(row["approved_at"]),
            expires_at=(
                datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None
            ),
            active=bool(row["active"]),
        )

    def _approval_from_row(self, row: sqlite3.Row) -> RuleApproval:
        return RuleApproval(
            id=row["id"],
            tenant_id=row["tenant_id"],
            pending_rule_id=row["pending_rule_id"],
            decision=row["decision"],
            approver_id=row["approver_id"],
            approver_role=row["approver_role"],
            allow_policy_suppression=bool(row["allow_policy_suppression"]),
            comment=row["comment"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())
