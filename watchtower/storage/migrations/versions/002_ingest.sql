-- Faz 2: sources, cursors, raw event store

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    connector_type TEXT NOT NULL,
    name TEXT NOT NULL,
    config_json TEXT NOT NULL DEFAULT '{}',
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sources_tenant ON sources (tenant_id);

CREATE TABLE IF NOT EXISTS source_cursors (
    source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    cursor_key TEXT NOT NULL DEFAULT 'default',
    cursor_value TEXT NOT NULL DEFAULT '{}',
    last_ack_at TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (source_id, cursor_key)
);

CREATE TABLE IF NOT EXISTS raw_events (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    dedupe_key TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    source_path TEXT,
    event_timestamp TEXT,
    ingested_at TEXT NOT NULL,
    UNIQUE (tenant_id, source_id, dedupe_key)
);

CREATE INDEX IF NOT EXISTS idx_raw_events_source ON raw_events (tenant_id, source_id, ingested_at);
CREATE INDEX IF NOT EXISTS idx_raw_events_ts ON raw_events (tenant_id, event_timestamp);
