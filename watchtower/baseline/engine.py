"""Baseline learning, snapshots, evaluation, and run-transition advice."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from watchtower.domain.profiles import (
    AssetProfile,
    BaselineEvaluation,
    BaselineSnapshot,
    BehaviorObservation,
    DepartmentProfile,
    LearningWindow,
    MetricStats,
    RoleProfile,
    RunTransitionAdvice,
    UserProfile,
)
from watchtower.baseline.stats import aggregate_observations, compute_metric_stats, profile_confidence
from watchtower.storage.repositories.baseline import BaselineRepository


class BaselineEngine:
    """45-day default learning window with user-first evaluation."""

    def __init__(
        self,
        repo: BaselineRepository,
        *,
        learning_window_days: int = 45,
        min_user_samples: int = 5,
        run_transition_confidence_threshold: float = 0.65,
    ) -> None:
        self._repo = repo
        self.learning_window_days = learning_window_days
        self.min_user_samples = min_user_samples
        self.run_transition_confidence_threshold = run_transition_confidence_threshold

    def record_observation(self, observation: BehaviorObservation) -> str:
        return self._repo.insert_observation(observation)

    def rebuild_profiles(
        self,
        tenant_id: str,
        *,
        as_of: datetime | None = None,
        window_days: int | None = None,
    ) -> LearningWindow:
        window = window_days or self.learning_window_days
        end = as_of or datetime.now(UTC)
        start = end - timedelta(days=window)

        observations = self._repo.list_observations(tenant_id, start, end)
        users = self._group_by(observations, "user_id")
        departments = self._group_by(observations, "department_id")
        assets = self._group_by(observations, "asset_id")

        for user_id, rows in users.items():
            if not user_id:
                continue
            metrics = self._metrics_from_rows(rows, window_days=window)
            profile = UserProfile(
                tenant_id=tenant_id,
                user_id=user_id,
                department_id=rows[0].get("department_id"),
                role_id=rows[0].get("role_id"),
                seniority=rows[0].get("seniority") or "worker",
                metrics=metrics,
                confidence=profile_confidence(metrics, window_days=window),
                window_days=window,
                updated_at=end,
            )
            self._repo.upsert_user_profile(profile)

        for department_id, rows in departments.items():
            if not department_id:
                continue
            metrics = self._metrics_from_rows(rows, window_days=window)
            profile = DepartmentProfile(
                tenant_id=tenant_id,
                department_id=department_id,
                metrics=metrics,
                confidence=profile_confidence(metrics, window_days=window),
                window_days=window,
                updated_at=end,
            )
            self._repo.upsert_department_profile(profile)

        role_groups: dict[tuple[str, str, str], list[dict]] = {}
        for row in observations:
            dept = row.get("department_id")
            role = row.get("role_id")
            seniority = row.get("seniority") or "worker"
            if dept and role:
                role_groups.setdefault((dept, role, seniority), []).append(row)

        for (department_id, role_id, seniority), rows in role_groups.items():
            metrics = self._metrics_from_rows(rows, window_days=window)
            profile = RoleProfile(
                tenant_id=tenant_id,
                role_id=role_id,
                department_id=department_id,
                seniority=seniority,  # type: ignore[arg-type]
                metrics=metrics,
                confidence=profile_confidence(metrics, window_days=window),
                window_days=window,
                updated_at=end,
            )
            self._repo.upsert_role_profile(profile)

        for asset_id, rows in assets.items():
            if not asset_id:
                continue
            metrics = self._metrics_from_rows(rows, window_days=window)
            profile = AssetProfile(
                tenant_id=tenant_id,
                asset_id=asset_id,
                metrics=metrics,
                confidence=profile_confidence(metrics, window_days=window),
                window_days=window,
                updated_at=end,
            )
            self._repo.upsert_asset_profile(profile)

        distinct_users = len([u for u in users if u])
        lw = LearningWindow(
            tenant_id=tenant_id,
            window_days=window,
            started_at=start,
            ends_at=end,
            observation_count=len(observations),
            distinct_users=distinct_users,
            confidence=self._tenant_confidence(tenant_id),
        )
        self._repo.upsert_learning_window(lw)
        return lw

    def compute_snapshots(
        self,
        tenant_id: str,
        *,
        as_of: datetime | None = None,
    ) -> list[BaselineSnapshot]:
        end = as_of or datetime.now(UTC)
        snapshots: list[BaselineSnapshot] = []
        for period, delta in (
            ("daily", timedelta(days=1)),
            ("weekly", timedelta(days=7)),
            ("monthly", timedelta(days=30)),
        ):
            start = end - delta
            observations = self._repo.list_observations(tenant_id, start, end)
            for profile_kind, key_field in (
                ("user", "user_id"),
                ("department", "department_id"),
                ("asset", "asset_id"),
            ):
                groups = self._group_by(observations, key_field)
                for key, rows in groups.items():
                    if not key:
                        continue
                    metrics = self._metrics_from_rows(
                        rows, window_days=max(1, delta.days)
                    )
                    snap = BaselineSnapshot(
                        tenant_id=tenant_id,
                        period=period,  # type: ignore[arg-type]
                        profile_kind=profile_kind,  # type: ignore[arg-type]
                        profile_key=key,
                        window_start=start,
                        window_end=end,
                        metrics=metrics,
                        confidence=profile_confidence(
                            metrics, window_days=max(1, delta.days)
                        ),
                    )
                    self._repo.insert_snapshot(snap)
                    snapshots.append(snap)
        return snapshots

    def evaluate(
        self,
        tenant_id: str,
        metric_name: str,
        value: float,
        *,
        user_id: str | None = None,
        department_id: str | None = None,
        role_id: str | None = None,
        seniority: str = "worker",
    ) -> BaselineEvaluation:
        user_prof = (
            self._repo.get_user_profile(tenant_id, user_id) if user_id else None
        )
        dept_prof = (
            self._repo.get_department_profile(tenant_id, department_id)
            if department_id
            else None
        )
        role_prof = None
        if department_id and role_id:
            role_prof = self._repo.get_role_profile(
                tenant_id, department_id, role_id, seniority
            )

        stats, source, used_user = self._resolve_stats(
            metric_name,
            user_prof,
            dept_prof,
            role_prof,
        )

        if stats is None or stats.sample_count == 0:
            return BaselineEvaluation(
                metric_name=metric_name,
                value=value,
                is_normal=False,
                source="none",
                used_user_baseline=False,
                details={"reason": "no baseline"},
            )

        is_normal = stats.low <= value <= stats.high
        return BaselineEvaluation(
            metric_name=metric_name,
            value=value,
            is_normal=is_normal,
            source=source,
            used_user_baseline=used_user,
            effective_low=stats.low,
            effective_high=stats.high,
            details={
                "mean": stats.mean,
                "std": stats.std,
                "sample_count": stats.sample_count,
            },
        )

    def recommend_run_transition(self, tenant_id: str) -> RunTransitionAdvice:
        lw = self._repo.get_learning_window(tenant_id)
        confidence = lw.confidence if lw else 0.0
        if confidence < self.run_transition_confidence_threshold:
            return RunTransitionAdvice(
                recommended=False,
                confidence=confidence,
                reason=(
                    f"baseline confidence {confidence:.2f} below threshold "
                    f"{self.run_transition_confidence_threshold:.2f}"
                ),
                blocking=True,
            )
        return RunTransitionAdvice(
            recommended=True,
            confidence=confidence,
            reason="baseline confidence sufficient for run mode",
            blocking=False,
        )

    def _resolve_stats(
        self,
        metric_name: str,
        user_prof: UserProfile | None,
        dept_prof: DepartmentProfile | None,
        role_prof: RoleProfile | None,
    ) -> tuple[MetricStats | None, str, bool]:
        """User baseline wins; department average never overrides user."""
        if user_prof:
            user_stats = user_prof.metrics.get(metric_name)
            if user_stats and user_stats.sample_count >= self.min_user_samples:
                return user_stats, "user", True

        if role_prof:
            role_stats = role_prof.metrics.get(metric_name)
            if role_stats and role_stats.sample_count >= self.min_user_samples:
                return role_stats, "role", False

        if dept_prof:
            dept_stats = dept_prof.metrics.get(metric_name)
            if dept_stats and dept_stats.sample_count > 0:
                return dept_stats, "department", False

        if user_prof:
            user_stats = user_prof.metrics.get(metric_name)
            if user_stats and user_stats.sample_count > 0:
                return user_stats, "user", True

        return None, "none", False

    def _tenant_confidence(self, tenant_id: str) -> float:
        profiles = self._repo.list_user_profiles(tenant_id)
        if not profiles:
            return 0.0
        return round(sum(p.confidence for p in profiles) / len(profiles), 4)

    @staticmethod
    def _group_by(rows: list[dict], field: str) -> dict[str | None, list[dict]]:
        groups: dict[str | None, list[dict]] = {}
        for row in rows:
            key = row.get(field)
            groups.setdefault(key, []).append(row)
        return groups

    @staticmethod
    def _metrics_from_rows(
        rows: list[dict],
        *,
        window_days: int,
    ) -> dict[str, MetricStats]:
        aggregated = aggregate_observations(rows)
        return {
            metric: compute_metric_stats(metric, values, days)
            for metric, (values, days) in aggregated.items()
        }
