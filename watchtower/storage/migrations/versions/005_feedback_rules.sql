-- Faz 5: feedback events, pending rules, stable feedback rules, approvals

CREATE TABLE IF NOT EXISTS feedback_events (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    feature_id TEXT,
    detection_class TEXT,
    candidate_id TEXT,
    scope_json TEXT NOT NULL DEFAULT '{}',
    comment TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_events_tenant_time
    ON feedback_events (tenant_id, created_at);

CREATE TABLE IF NOT EXISTS pending_rules (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    feedback_event_id TEXT NOT NULL REFERENCES feedback_events(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'rejected')),
    scope_json TEXT NOT NULL DEFAULT '{}',
    effect_json TEXT NOT NULL DEFAULT '{}',
    proposed_by TEXT NOT NULL,
    proposed_role TEXT NOT NULL,
    requires_policy_suppression_approval INTEGER NOT NULL DEFAULT 0,
    expires_at TEXT,
    created_at TEXT NOT NULL,
    reviewed_at TEXT,
    reviewed_by TEXT,
    review_comment TEXT
);

CREATE INDEX IF NOT EXISTS idx_pending_rules_tenant_status
    ON pending_rules (tenant_id, status);

CREATE TABLE IF NOT EXISTS feedback_rules (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    pending_rule_id TEXT NOT NULL REFERENCES pending_rules(id) ON DELETE CASCADE,
    feedback_event_id TEXT NOT NULL REFERENCES feedback_events(id) ON DELETE CASCADE,
    scope_json TEXT NOT NULL DEFAULT '{}',
    effect_json TEXT NOT NULL DEFAULT '{}',
    approved_by TEXT NOT NULL,
    approved_at TEXT NOT NULL,
    expires_at TEXT,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_feedback_rules_tenant_active
    ON feedback_rules (tenant_id, active);

CREATE TABLE IF NOT EXISTS rule_approvals (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    pending_rule_id TEXT NOT NULL REFERENCES pending_rules(id) ON DELETE CASCADE,
    decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected')),
    approver_id TEXT NOT NULL,
    approver_role TEXT NOT NULL,
    allow_policy_suppression INTEGER NOT NULL DEFAULT 0,
    comment TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rule_approvals_pending
    ON rule_approvals (pending_rule_id);
