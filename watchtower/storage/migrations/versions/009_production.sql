-- Faz 11: production metadata and retention audit

CREATE TABLE IF NOT EXISTS system_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS retention_runs (
    id TEXT PRIMARY KEY,
    tenant_id TEXT,
    policy TEXT NOT NULL,
    deleted_counts_json TEXT NOT NULL DEFAULT '{}',
    ran_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_retention_runs_ran_at ON retention_runs (ran_at);
