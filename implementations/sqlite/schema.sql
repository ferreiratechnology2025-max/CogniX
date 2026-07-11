-- AEP SQLite Schema v1.0.0

-- Resources table
CREATE TABLE IF NOT EXISTS resources (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    CHECK (type IN ('project', 'status', 'skill', 'adr', 'incident', 'rule', 'template')),
    CHECK (status IN ('draft', 'review', 'active', 'deprecated', 'archived'))
);

-- Dependencies table (many-to-many)
CREATE TABLE IF NOT EXISTS resource_dependencies (
    resource_id TEXT NOT NULL,
    depends_on TEXT NOT NULL,
    FOREIGN KEY (resource_id) REFERENCES resources(id),
    FOREIGN KEY (depends_on) REFERENCES resources(id),
    PRIMARY KEY (resource_id, depends_on)
);

-- State table (singleton)
CREATE TABLE IF NOT EXISTS kernel_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    active_project TEXT,
    active_status TEXT,
    session TEXT,
    last_run TEXT,
    last_result TEXT,
    program TEXT DEFAULT 'padrao',
    r0_session TEXT,
    internal_last_action TEXT,  -- not R1: SQLite does not implement WATCHDOG (see README)
    r2_next_act TEXT,
    r3_modified TEXT,
    r4_blockers TEXT,
    r5_active_sk TEXT,
    r6_health TEXT DEFAULT 'OK',
    r7_timestamp TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(type);
CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status);