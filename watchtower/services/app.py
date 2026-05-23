"""Application context wiring migrations, repositories, and services."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from watchtower.config.loader import load_settings
from watchtower.config.settings import WatchtowerSettings
from watchtower.services.audit import AuditService
from watchtower.services.bootstrap import BootstrapService
from watchtower.services.mode_controller import ModeController
from watchtower.services.tenant_context import TenantContext
from watchtower.storage.database import Database
from watchtower.storage.migrations.runner import apply_migrations
from watchtower.storage.repositories.audit import AuditRepository
from watchtower.storage.repositories.bootstrap import BootstrapRepository
from watchtower.storage.repositories.mode import ModeRepository
from watchtower.baseline.engine import BaselineEngine
from watchtower.baseline.query import BaselineQueryAPI
from watchtower.decision.service import DecisionService
from watchtower.graph.checkpointing import GraphCheckpointStore
from watchtower.graph.runner import GraphRunner, build_graph_runner
from watchtower.llm.gateway import LLMGateway
from watchtower.llm.providers.onboarding import resolve_provider_chain
from watchtower.storage.repositories.llm_audit import LLMCallAuditRepository
from watchtower.storage.repositories.graph import GraphRepository
from watchtower.feedback.engine import FeedbackEngine
from watchtower.feedback.service import FeedbackService
from watchtower.rules.engine import RuleEngine
from watchtower.candidates.service import CandidatePipelineService
from watchtower.ingest.service import IngestService
from watchtower.normalization.service import NormalizationService
from watchtower.storage.repositories.candidate_event import CandidateEventRepository
from watchtower.storage.repositories.normalized_event import NormalizedEventRepository
from watchtower.storage.repositories.raw_event import RawEventRepository
from watchtower.storage.repositories.unknown_schema import UnknownSchemaRepository
from watchtower.storage.repositories.baseline import BaselineRepository
from watchtower.storage.repositories.feedback_rules import FeedbackRulesRepository
from watchtower.storage.repositories.alerts import AlertRepository
from watchtower.alerts.service import AlertService
from watchtower.query.service import QueryService
from watchtower.storage.repositories.source import SourceRepository
from watchtower.storage.repositories.source_cursor import SourceCursorRepository
from watchtower.storage.repositories.tenant import TenantRepository


@dataclass
class SessionContext:
    """Connection-scoped services for one database transaction."""

    conn: sqlite3.Connection
    settings: WatchtowerSettings
    database: Database
    tenants: TenantRepository
    bootstrap: BootstrapRepository
    modes: ModeRepository
    audit_repo: AuditRepository
    audit: AuditService
    mode_controller: ModeController
    bootstrap_service: BootstrapService
    sources: SourceRepository
    source_cursors: SourceCursorRepository
    raw_events: RawEventRepository
    ingest: IngestService
    normalized_events: NormalizedEventRepository
    unknown_schema: UnknownSchemaRepository
    candidate_events: CandidateEventRepository
    normalizer: NormalizationService
    pipeline: CandidatePipelineService
    baseline: BaselineEngine
    feedback: FeedbackService
    rules: RuleEngine
    decision: DecisionService
    graph: GraphRepository
    graph_runner: GraphRunner
    llm: LLMGateway
    alerts: AlertService
    query: QueryService

    def set_default_tenant_context(self) -> str | None:
        tenant = self.bootstrap_service.get_default_tenant()
        if tenant is None:
            TenantContext.clear()
            return None
        TenantContext.set_current(tenant.id)
        return tenant.id


@dataclass
class AppContext:
    settings: WatchtowerSettings
    database: Database
    checkpoint_store: GraphCheckpointStore

    def run_migrations(self) -> list[str]:
        with self.database.session() as conn:
            return apply_migrations(conn, self.settings.migrations_dir)

    @contextmanager
    def session(self) -> Iterator[SessionContext]:
        with self.database.session() as conn:
            ctx = _build_session(conn, self.settings, self.database, self.checkpoint_store)
            tenant_id = ctx.set_default_tenant_context()
            try:
                yield ctx
            finally:
                if tenant_id is not None:
                    TenantContext.clear()


def _build_session(
    conn: sqlite3.Connection,
    settings: WatchtowerSettings,
    database: Database,
    checkpoint_store: GraphCheckpointStore,
) -> SessionContext:
    tenants = TenantRepository(conn)
    bootstrap = BootstrapRepository(conn)
    modes = ModeRepository(conn)
    audit_repo = AuditRepository(conn)
    audit = AuditService(audit_repo, settings)
    mode_controller = ModeController(modes, audit)
    bootstrap_service = BootstrapService(
        tenants,
        bootstrap,
        mode_controller,
        audit,
        default_tenant_slug=settings.default_tenant_slug,
    )
    sources = SourceRepository(conn)
    source_cursors = SourceCursorRepository(conn)
    raw_events = RawEventRepository(conn)
    ingest = IngestService(sources, source_cursors, raw_events)
    normalized_events = NormalizedEventRepository(conn)
    unknown_schema = UnknownSchemaRepository(conn)
    candidate_events = CandidateEventRepository(conn)
    normalizer = NormalizationService()
    pipeline = CandidatePipelineService(
        raw_events,
        normalized_events,
        unknown_schema,
        candidate_events,
        normalizer,
    )
    baseline_repo = BaselineRepository(conn)
    baseline = BaselineEngine(
        baseline_repo,
        learning_window_days=settings.baseline_learning_window_days,
        min_user_samples=settings.baseline_min_user_samples,
        run_transition_confidence_threshold=settings.baseline_run_transition_confidence_threshold,
    )
    feedback_rules_repo = FeedbackRulesRepository(conn)
    feedback = FeedbackService(feedback_rules_repo)
    rules = RuleEngine(feedback_rules_repo)
    baseline_query = BaselineQueryAPI(baseline)
    feedback_engine = FeedbackEngine(rules)
    decision = DecisionService(
        baseline=baseline_query,
        feedback=feedback_engine,
    )
    graph_repo = GraphRepository(conn)
    llm_audit = LLMCallAuditRepository(conn)
    provider_chain = resolve_provider_chain(settings, conn)
    llm_gateway = LLMGateway(
        provider_chain,
        audit_repo=llm_audit,
        max_retries=settings.llm_max_retries,
    )
    alert_repo = AlertRepository(conn)
    alert_service = AlertService(alert_repo, feedback=feedback)
    query_service = QueryService(alert_repo, baseline_repo)
    graph_runner = build_graph_runner(
        mode_controller=mode_controller,
        decision=decision,
        baseline=baseline,
        feedback=feedback,
        rules=rules,
        graph_repo=graph_repo,
        conn=conn,
        checkpoint_store=checkpoint_store,
        llm_gateway=llm_gateway,
        alerts=alert_service,
    )
    return SessionContext(
        conn=conn,
        settings=settings,
        database=database,
        tenants=tenants,
        bootstrap=bootstrap,
        modes=modes,
        audit_repo=audit_repo,
        audit=audit,
        mode_controller=mode_controller,
        bootstrap_service=bootstrap_service,
        sources=sources,
        source_cursors=source_cursors,
        raw_events=raw_events,
        ingest=ingest,
        normalized_events=normalized_events,
        unknown_schema=unknown_schema,
        candidate_events=candidate_events,
        normalizer=normalizer,
        pipeline=pipeline,
        baseline=baseline,
        feedback=feedback,
        rules=rules,
        decision=decision,
        graph=graph_repo,
        graph_runner=graph_runner,
        llm=llm_gateway,
        alerts=alert_service,
        query=query_service,
    )


_app: AppContext | None = None


def init_app(
    *,
    settings: WatchtowerSettings | None = None,
    database_path: Path | None = None,
    run_migrations: bool = True,
) -> AppContext:
    """Initialize global app context (settings + database)."""
    global _app
    resolved_settings = settings or load_settings()
    if database_path is not None:
        resolved_settings = resolved_settings.model_copy(
            update={"database_path": database_path}
        )

    database = Database(resolved_settings.database_path)
    checkpoint_store = GraphCheckpointStore.from_settings(resolved_settings)
    _app = AppContext(
        settings=resolved_settings,
        database=database,
        checkpoint_store=checkpoint_store,
    )
    if run_migrations:
        _app.run_migrations()
    return _app


def get_app_context() -> AppContext:
    if _app is None:
        msg = "Application not initialized"
        raise RuntimeError(msg)
    return _app


def create_app(
    *,
    settings: WatchtowerSettings | None = None,
    database_path: Path | None = None,
    run_migrations: bool = True,
) -> AppContext:
    """Create an isolated app context (tests) without touching the global singleton."""
    resolved_settings = settings or load_settings()
    if database_path is not None:
        resolved_settings = resolved_settings.model_copy(
            update={"database_path": database_path}
        )
    checkpoint_store = GraphCheckpointStore.from_settings(resolved_settings)
    app = AppContext(
        settings=resolved_settings,
        database=Database(resolved_settings.database_path),
        checkpoint_store=checkpoint_store,
    )
    if run_migrations:
        app.run_migrations()
    return app
