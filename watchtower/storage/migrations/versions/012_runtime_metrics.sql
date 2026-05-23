-- Faz 16: durable runtime metrics for observability

CREATE TABLE IF NOT EXISTS runtime_metrics (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (tenant_id, metric_name)
);

CREATE INDEX IF NOT EXISTS idx_runtime_metrics_tenant
    ON runtime_metrics (tenant_id);
