-- Worklog Core Schema
-- Version: 1.1.0
-- Tables: 5 (entries, knowledge_base, memories, error_patterns, research)
-- NOTE: sot_issues removed in INFA-614 - Plane/Gitea sync no longer uses worklog

-- Work history and activity logs
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    agent TEXT NOT NULL,
    task_type TEXT NOT NULL,
    title TEXT NOT NULL,
    details TEXT,
    decision_rationale TEXT,
    outcome TEXT,
    tags TEXT,
    related_files TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_timestamp ON entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_entries_agent ON entries(agent);
CREATE INDEX IF NOT EXISTS idx_entries_task_type ON entries(task_type);
CREATE INDEX IF NOT EXISTS idx_entries_tags ON entries(tags);

-- Knowledge articles, guides, protocols
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,
    source_agent TEXT,
    is_protocol INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    system TEXT DEFAULT 'shared',
    source_url TEXT                          -- Optional: external URL reference
);

CREATE INDEX IF NOT EXISTS idx_kb_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_kb_tags ON knowledge_base(tags);
CREATE INDEX IF NOT EXISTS idx_kb_protocol ON knowledge_base(is_protocol);
CREATE INDEX IF NOT EXISTS idx_kb_updated ON knowledge_base(updated_at);

-- Working memory / session context
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    memory_type TEXT DEFAULT 'fact',        -- fact|entity|preference|context
    status TEXT DEFAULT 'staging',          -- staging|promoted|archived
    importance INTEGER DEFAULT 5,           -- 1-10
    access_count INTEGER DEFAULT 1,
    source_agent TEXT,
    system TEXT,
    entities TEXT,                          -- JSON: extracted entities
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    promoted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_memories_status ON memories(status);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_memories_access ON memories(access_count);

-- Error signatures and resolutions
CREATE TABLE IF NOT EXISTS error_patterns (
    id INTEGER PRIMARY KEY,
    error_signature TEXT NOT NULL,          -- regex or key text to match
    error_message TEXT,                     -- full example message
    platform TEXT,                          -- linux|macos|docker|nas|all
    language TEXT,                          -- python|typescript|bash|go|all
    project TEXT,                           -- specific project or NULL for global
    root_cause TEXT,
    resolution TEXT NOT NULL,
    prevention_tip TEXT,
    occurrence_count INTEGER DEFAULT 1,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_error_platform ON error_patterns(platform);
CREATE INDEX IF NOT EXISTS idx_error_language ON error_patterns(language);
CREATE INDEX IF NOT EXISTS idx_error_project ON error_patterns(project);
CREATE INDEX IF NOT EXISTS idx_error_tags ON error_patterns(tags);

-- External research (articles, videos, docs)
CREATE TABLE IF NOT EXISTS research (
    id INTEGER PRIMARY KEY,
    source_type TEXT NOT NULL,              -- video|article|documentation|etc
    source_url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_id TEXT,
    author TEXT,
    raw_content TEXT,
    summary TEXT,
    key_points TEXT,
    actionable_items TEXT,
    relevance_score INTEGER DEFAULT 0,
    relevance_notes TEXT,
    applicable_to TEXT,
    duration_seconds INTEGER,
    word_count INTEGER,
    processed_by TEXT,
    tags TEXT,
    status TEXT DEFAULT 'pending'
);

CREATE INDEX IF NOT EXISTS idx_research_source_type ON research(source_type);
CREATE INDEX IF NOT EXISTS idx_research_status ON research(status);
CREATE INDEX IF NOT EXISTS idx_research_relevance ON research(relevance_score);
CREATE INDEX IF NOT EXISTS idx_research_tags ON research(tags);
CREATE INDEX IF NOT EXISTS idx_research_created ON research(created_at);

-- Set journal mode for network compatibility
PRAGMA journal_mode=DELETE;
