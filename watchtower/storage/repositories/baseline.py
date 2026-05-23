"""Baseline persistence."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime

from watchtower.domain.profiles import (
    AssetProfile,
    BaselineSnapshot,
    BehaviorObservation,
    DepartmentProfile,
    LearningWindow,
    MetricStats,
    RoleProfile,
    UserProfile,
)


def _metrics_to_json(metrics: dict[str, MetricStats]) -> str:
    return json.dumps(
        {k: v.model_dump() for k, v in metrics.items()},
        ensure_ascii=False,
    )


def _metrics_from_json(raw: str) -> dict[str, MetricStats]:
    data = json.loads(raw or "{}")
    return {k: MetricStats.model_validate(v) for k, v in data.items()}


class BaselineRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def insert_observation(self, obs: BehaviorObservation) -> str:
        obs_id = str(uuid.uuid4())
        self._conn.execute(
            """
            INSERT INTO behavior_observations (
                id, tenant_id, metric_name, value, observed_at,
                user_id, department_id, role_id, seniority, asset_id, feature_hint
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                obs_id,
                obs.tenant_id,
                obs.metric_name,
                obs.value,
                obs.observed_at.isoformat(),
                obs.user_id,
                obs.department_id,
                obs.role_id,
                obs.seniority,
                obs.asset_id,
                obs.feature_hint,
            ),
        )
        return obs_id

    def list_observations(
        self,
        tenant_id: str,
        start: datetime,
        end: datetime,
    ) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT metric_name, value, observed_at, user_id, department_id,
                   role_id, seniority, asset_id
            FROM behavior_observations
            WHERE tenant_id = ? AND observed_at >= ? AND observed_at <= ?
            ORDER BY observed_at
            """,
            (tenant_id, start.isoformat(), end.isoformat()),
        ).fetchall()
        return [dict(row) for row in rows]

    def upsert_user_profile(self, profile: UserProfile) -> None:
        self._conn.execute(
            """
            INSERT INTO user_profiles (
                tenant_id, user_id, department_id, role_id, seniority,
                metrics_json, confidence, window_days, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tenant_id, user_id) DO UPDATE SET
                department_id=excluded.department_id,
                role_id=excluded.role_id,
                seniority=excluded.seniority,
                metrics_json=excluded.metrics_json,
                confidence=excluded.confidence,
                window_days=excluded.window_days,
                updated_at=excluded.updated_at
            """,
            (
                profile.tenant_id,
                profile.user_id,
                profile.department_id,
                profile.role_id,
                profile.seniority,
                _metrics_to_json(profile.metrics),
                profile.confidence,
                profile.window_days,
                (profile.updated_at or datetime.now(UTC)).isoformat(),
            ),
        )

    def get_user_profile(self, tenant_id: str, user_id: str) -> UserProfile | None:
        row = self._conn.execute(
            """
            SELECT tenant_id, user_id, department_id, role_id, seniority,
                   metrics_json, confidence, window_days, updated_at
            FROM user_profiles WHERE tenant_id = ? AND user_id = ?
            """,
            (tenant_id, user_id),
        ).fetchone()
        if row is None:
            return None
        return UserProfile(
            tenant_id=row["tenant_id"],
            user_id=row["user_id"],
            department_id=row["department_id"],
            role_id=row["role_id"],
            seniority=row["seniority"],
            metrics=_metrics_from_json(row["metrics_json"]),
            confidence=float(row["confidence"]),
            window_days=int(row["window_days"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def list_user_profiles(self, tenant_id: str) -> list[UserProfile]:
        rows = self._conn.execute(
            "SELECT user_id FROM user_profiles WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchall()
        return [
            self.get_user_profile(tenant_id, row["user_id"])
            for row in rows
            if row["user_id"]
        ]

    def upsert_department_profile(self, profile: DepartmentProfile) -> None:
        self._conn.execute(
            """
            INSERT INTO department_profiles (
                tenant_id, department_id, metrics_json, confidence,
                window_days, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(tenant_id, department_id) DO UPDATE SET
                metrics_json=excluded.metrics_json,
                confidence=excluded.confidence,
                window_days=excluded.window_days,
                updated_at=excluded.updated_at
            """,
            (
                profile.tenant_id,
                profile.department_id,
                _metrics_to_json(profile.metrics),
                profile.confidence,
                profile.window_days,
                (profile.updated_at or datetime.now(UTC)).isoformat(),
            ),
        )

    def get_department_profile(
        self, tenant_id: str, department_id: str
    ) -> DepartmentProfile | None:
        row = self._conn.execute(
            """
            SELECT tenant_id, department_id, metrics_json, confidence,
                   window_days, updated_at
            FROM department_profiles WHERE tenant_id = ? AND department_id = ?
            """,
            (tenant_id, department_id),
        ).fetchone()
        if row is None:
            return None
        return DepartmentProfile(
            tenant_id=row["tenant_id"],
            department_id=row["department_id"],
            metrics=_metrics_from_json(row["metrics_json"]),
            confidence=float(row["confidence"]),
            window_days=int(row["window_days"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def upsert_role_profile(self, profile: RoleProfile) -> None:
        self._conn.execute(
            """
            INSERT INTO role_profiles (
                tenant_id, department_id, role_id, seniority,
                metrics_json, confidence, window_days, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tenant_id, department_id, role_id, seniority) DO UPDATE SET
                metrics_json=excluded.metrics_json,
                confidence=excluded.confidence,
                window_days=excluded.window_days,
                updated_at=excluded.updated_at
            """,
            (
                profile.tenant_id,
                profile.department_id,
                profile.role_id,
                profile.seniority,
                _metrics_to_json(profile.metrics),
                profile.confidence,
                profile.window_days,
                (profile.updated_at or datetime.now(UTC)).isoformat(),
            ),
        )

    def get_role_profile(
        self,
        tenant_id: str,
        department_id: str,
        role_id: str,
        seniority: str,
    ) -> RoleProfile | None:
        row = self._conn.execute(
            """
            SELECT tenant_id, department_id, role_id, seniority,
                   metrics_json, confidence, window_days, updated_at
            FROM role_profiles
            WHERE tenant_id = ? AND department_id = ? AND role_id = ? AND seniority = ?
            """,
            (tenant_id, department_id, role_id, seniority),
        ).fetchone()
        if row is None:
            return None
        return RoleProfile(
            tenant_id=row["tenant_id"],
            department_id=row["department_id"],
            role_id=row["role_id"],
            seniority=row["seniority"],
            metrics=_metrics_from_json(row["metrics_json"]),
            confidence=float(row["confidence"]),
            window_days=int(row["window_days"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def upsert_asset_profile(self, profile: AssetProfile) -> None:
        self._conn.execute(
            """
            INSERT INTO asset_profiles (
                tenant_id, asset_id, metrics_json, confidence,
                window_days, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(tenant_id, asset_id) DO UPDATE SET
                metrics_json=excluded.metrics_json,
                confidence=excluded.confidence,
                window_days=excluded.window_days,
                updated_at=excluded.updated_at
            """,
            (
                profile.tenant_id,
                profile.asset_id,
                _metrics_to_json(profile.metrics),
                profile.confidence,
                profile.window_days,
                (profile.updated_at or datetime.now(UTC)).isoformat(),
            ),
        )

    def insert_snapshot(self, snap: BaselineSnapshot) -> str:
        snap_id = str(uuid.uuid4())
        self._conn.execute(
            """
            INSERT OR REPLACE INTO baseline_snapshots (
                id, tenant_id, period, profile_kind, profile_key,
                window_start, window_end, metrics_json, confidence, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snap_id,
                snap.tenant_id,
                snap.period,
                snap.profile_kind,
                snap.profile_key,
                snap.window_start.isoformat(),
                snap.window_end.isoformat(),
                _metrics_to_json(snap.metrics),
                snap.confidence,
                datetime.now(UTC).isoformat(),
            ),
        )
        return snap_id

    def upsert_learning_window(self, lw: LearningWindow) -> None:
        self._conn.execute(
            """
            INSERT INTO learning_windows (
                tenant_id, window_days, started_at, ends_at,
                observation_count, distinct_users, confidence, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tenant_id) DO UPDATE SET
                window_days=excluded.window_days,
                started_at=excluded.started_at,
                ends_at=excluded.ends_at,
                observation_count=excluded.observation_count,
                distinct_users=excluded.distinct_users,
                confidence=excluded.confidence,
                updated_at=excluded.updated_at
            """,
            (
                lw.tenant_id,
                lw.window_days,
                lw.started_at.isoformat(),
                lw.ends_at.isoformat(),
                lw.observation_count,
                lw.distinct_users,
                lw.confidence,
                datetime.now(UTC).isoformat(),
            ),
        )

    def get_learning_window(self, tenant_id: str) -> LearningWindow | None:
        row = self._conn.execute(
            """
            SELECT tenant_id, window_days, started_at, ends_at,
                   observation_count, distinct_users, confidence
            FROM learning_windows WHERE tenant_id = ?
            """,
            (tenant_id,),
        ).fetchone()
        if row is None:
            return None
        return LearningWindow(
            tenant_id=row["tenant_id"],
            window_days=int(row["window_days"]),
            started_at=datetime.fromisoformat(row["started_at"]),
            ends_at=datetime.fromisoformat(row["ends_at"]),
            observation_count=int(row["observation_count"]),
            distinct_users=int(row["distinct_users"]),
            confidence=float(row["confidence"]),
        )

    def count_snapshots(self, tenant_id: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) AS cnt FROM baseline_snapshots WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()
        return int(row["cnt"]) if row else 0
