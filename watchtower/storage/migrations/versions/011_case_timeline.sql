-- Faz 15: operator case timeline

CREATE TABLE IF NOT EXISTS case_timeline (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    alert_id TEXT NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    case_id TEXT REFERENCES alert_cases(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN (
        'created',
        'acknowledged',
        'assigned',
        'comment_added',
        'ticket_linked',
        'feedback_submitted',
        'closed'
    )),
    actor TEXT,
    comment TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_case_timeline_alert
    ON case_timeline (alert_id, created_at);

CREATE INDEX IF NOT EXISTS idx_case_timeline_case
    ON case_timeline (case_id, created_at);
