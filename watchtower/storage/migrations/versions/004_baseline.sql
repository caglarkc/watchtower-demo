-- Faz 4: baseline observations, profiles, snapshots, learning windows

CREATE TABLE IF NOT EXISTS behavior_observations (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    observed_at TEXT NOT NULL,
    user_id TEXT,
    department_id TEXT,
    role_id TEXT,
    seniority TEXT NOT NULL DEFAULT 'worker',
    asset_id TEXT,
    feature_hint TEXT
);

CREATE INDEX IF NOT EXISTS idx_behavior_obs_tenant_time
    ON behavior_observations (tenant_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_behavior_obs_user_metric
    ON behavior_observations (tenant_id, user_id, metric_name);

CREATE TABLE IF NOT EXISTS user_profiles (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    department_id TEXT,
    role_id TEXT,
    seniority TEXT NOT NULL DEFAULT 'worker',
    metrics_json TEXT NOT NULL DEFAULT '{}',
    confidence REAL NOT NULL DEFAULT 0,
    window_days INTEGER NOT NULL DEFAULT 45,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (tenant_id, user_id)
);

CREATE TABLE IF NOT EXISTS department_profiles (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    department_id TEXT NOT NULL,
    metrics_json TEXT NOT NULL DEFAULT '{}',
    confidence REAL NOT NULL DEFAULT 0,
    window_days INTEGER NOT NULL DEFAULT 45,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (tenant_id, department_id)
);

CREATE TABLE IF NOT EXISTS role_profiles (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    department_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    seniority TEXT NOT NULL,
    metrics_json TEXT NOT NULL DEFAULT '{}',
    confidence REAL NOT NULL DEFAULT 0,
    window_days INTEGER NOT NULL DEFAULT 45,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (tenant_id, department_id, role_id, seniority)
);

CREATE TABLE IF NOT EXISTS asset_profiles (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    asset_id TEXT NOT NULL,
    metrics_json TEXT NOT NULL DEFAULT '{}',
    confidence REAL NOT NULL DEFAULT 0,
    window_days INTEGER NOT NULL DEFAULT 45,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (tenant_id, asset_id)
);

CREATE TABLE IF NOT EXISTS baseline_snapshots (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    period TEXT NOT NULL CHECK (period IN ('daily', 'weekly', 'monthly')),
    profile_kind TEXT NOT NULL,
    profile_key TEXT NOT NULL,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    metrics_json TEXT NOT NULL DEFAULT '{}',
    confidence REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, period, profile_kind, profile_key, window_start)
);

CREATE TABLE IF NOT EXISTS learning_windows (
    tenant_id TEXT PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,
    window_days INTEGER NOT NULL DEFAULT 45,
    started_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    observation_count INTEGER NOT NULL DEFAULT 0,
    distinct_users INTEGER NOT NULL DEFAULT 0,
    confidence REAL NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);
