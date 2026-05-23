-- Faz 3: normalized events, unknown schema queue, candidate events

CREATE TABLE IF NOT EXISTS normalized_events (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    raw_event_id TEXT UNIQUE REFERENCES raw_events(id) ON DELETE SET NULL,
    source_id TEXT REFERENCES sources(id) ON DELETE SET NULL,
    schema_format TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor TEXT,
    action TEXT NOT NULL,
    resource TEXT,
    occurred_at TEXT NOT NULL,
    feature_hint TEXT,
    scenario_id TEXT,
    source_path TEXT,
    channel TEXT,
    anomaly_flag INTEGER NOT NULL DEFAULT 0,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_normalized_tenant_time
    ON normalized_events (tenant_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_normalized_feature
    ON normalized_events (tenant_id, feature_hint);

CREATE TABLE IF NOT EXISTS unknown_schema_queue (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    raw_event_id TEXT UNIQUE REFERENCES raw_events(id) ON DELETE CASCADE,
    schema_signature TEXT NOT NULL,
    payload_sample_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'mapped', 'ignored')),
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_unknown_schema_tenant
    ON unknown_schema_queue (tenant_id, status);

CREATE TABLE IF NOT EXISTS candidate_events (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    normalized_event_id TEXT NOT NULL UNIQUE REFERENCES normalized_events(id) ON DELETE CASCADE,
    feature_hint TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    scenario_id TEXT,
    anomaly_flag INTEGER NOT NULL DEFAULT 0,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_candidate_tenant_feature
    ON candidate_events (tenant_id, feature_hint, occurred_at);
