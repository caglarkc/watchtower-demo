-- Faz 8: LLM call audit

CREATE TABLE IF NOT EXISTS llm_call_audit (
    id TEXT PRIMARY KEY,
    tenant_id TEXT REFERENCES tenants(id) ON DELETE CASCADE,
    task_name TEXT NOT NULL,
    provider TEXT,
    model TEXT,
    success INTEGER NOT NULL DEFAULT 0,
    attempts INTEGER NOT NULL DEFAULT 1,
    prompt_hash TEXT,
    request_json TEXT,
    response_json TEXT,
    error TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_llm_call_audit_tenant_time
    ON llm_call_audit (tenant_id, created_at);

CREATE INDEX IF NOT EXISTS idx_llm_call_audit_task
    ON llm_call_audit (task_name, created_at);
