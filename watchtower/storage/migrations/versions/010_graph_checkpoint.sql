-- Faz 13: durable graph checkpoint metadata on graph_runs

ALTER TABLE graph_runs ADD COLUMN thread_id TEXT;
ALTER TABLE graph_runs ADD COLUMN last_checkpoint_id TEXT;
ALTER TABLE graph_runs ADD COLUMN interrupted INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_graph_runs_thread
    ON graph_runs (thread_id);

CREATE INDEX IF NOT EXISTS idx_graph_runs_interrupted
    ON graph_runs (tenant_id, interrupted, started_at);
