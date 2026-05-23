-- Faz 7: LangGraph runs, audit, findings, alerts, learning events

CREATE TABLE IF NOT EXISTS graph_runs (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    candidate_id TEXT,
    mode TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    route_json TEXT,
    assessment_json TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_graph_runs_tenant_started
    ON graph_runs (tenant_id, started_at);

CREATE TABLE IF NOT EXISTS graph_run_audit (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES graph_runs(id) ON DELETE CASCADE,
    node_name TEXT NOT NULL,
    output_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_graph_run_audit_run
    ON graph_run_audit (run_id, created_at);

CREATE TABLE IF NOT EXISTS silent_candidate_findings (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    run_id TEXT NOT NULL REFERENCES graph_runs(id) ON DELETE CASCADE,
    candidate_id TEXT,
    feature_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_silent_findings_tenant
    ON silent_candidate_findings (tenant_id, created_at);

CREATE TABLE IF NOT EXISTS alert_cases (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    run_id TEXT NOT NULL REFERENCES graph_runs(id) ON DELETE CASCADE,
    candidate_id TEXT,
    feature_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_alert_cases_tenant
    ON alert_cases (tenant_id, status, created_at);

CREATE TABLE IF NOT EXISTS controlled_learning_events (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    run_id TEXT NOT NULL REFERENCES graph_runs(id) ON DELETE CASCADE,
    candidate_id TEXT,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_learning_events_tenant
    ON controlled_learning_events (tenant_id, created_at);
