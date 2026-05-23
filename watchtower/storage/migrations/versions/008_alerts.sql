-- Faz 9: alerts store, lifecycle, suppression, operator queries

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    feature_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN (
            'open', 'investigating', 'true_positive', 'false_positive',
            'suppressed', 'ticket_linked'
        )),
    title TEXT NOT NULL,
    summary TEXT,
    user_id TEXT,
    department_id TEXT,
    resource TEXT,
    action TEXT,
    graph_run_id TEXT,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_alerts_tenant_status
    ON alerts (tenant_id, status, created_at);

CREATE TABLE IF NOT EXISTS alert_lifecycle_events (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    alert_id TEXT NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    alert_case_id TEXT,
    from_status TEXT,
    to_status TEXT NOT NULL,
    actor TEXT,
    comment TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_alert_lifecycle_alert
    ON alert_lifecycle_events (alert_id, created_at);

CREATE TABLE IF NOT EXISTS suppression_windows (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    alert_id TEXT NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    scope_json TEXT NOT NULL DEFAULT '{}',
    starts_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    reason TEXT,
    created_by TEXT,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_suppression_tenant_expires
    ON suppression_windows (tenant_id, expires_at, active);

-- Extend graph-era alert_cases with alert linkage (nullable for legacy rows)
ALTER TABLE alert_cases ADD COLUMN alert_id TEXT REFERENCES alerts(id);
ALTER TABLE alert_cases ADD COLUMN updated_at TEXT;
ALTER TABLE alert_cases ADD COLUMN ticket_id TEXT;
ALTER TABLE alert_cases ADD COLUMN assigned_to TEXT;

CREATE TABLE IF NOT EXISTS operator_queries (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    sources_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_operator_queries_tenant
    ON operator_queries (tenant_id, created_at);
