-- Worklog Extended Schema
-- Version: 1.0.1
-- Tables: 4 (projects, component_registry, component_deployments, reference_library)
-- Requires: core.sql to be applied first
-- Optional: domain-agency.sql for clients/competitors tables

-- Project registry and tracking
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,              -- project identifier/slug
    display_name TEXT,                      -- human-friendly name
    description TEXT,
    repo_url TEXT,                          -- git repo URL if applicable
    local_path TEXT,                        -- primary local path
    project_type TEXT,                      -- app|library|service|docs|research|config
    language TEXT,                          -- primary language: python|typescript|go|rust|mixed
    framework TEXT,                         -- react|next|fastapi|django|none
    status TEXT DEFAULT 'active',           -- active|paused|archived|completed
    priority INTEGER DEFAULT 5,             -- 1-10 (10 = highest)
    owner_system TEXT,                      -- which system owns this project
    last_worked TIMESTAMP,
    notes TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_type ON projects(project_type);

-- Platform component registry (agents, skills, commands)
CREATE TABLE IF NOT EXISTS component_registry (
    id INTEGER PRIMARY KEY,
    component_type TEXT NOT NULL,           -- agent|skill|command|plugin|protocol|script
    name TEXT NOT NULL,
    description TEXT,
    canonical_path TEXT,                    -- relative path from .claude/
    canonical_system TEXT DEFAULT 'local',
    content_hash TEXT,                      -- SHA256 for drift detection
    status TEXT DEFAULT 'active',           -- active|deprecated|draft|experimental
    capabilities TEXT,                      -- JSON: what it provides
    dependencies TEXT,                      -- JSON: what it requires
    metadata TEXT,                          -- JSON: type-specific data
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(component_type, name)
);

CREATE INDEX IF NOT EXISTS idx_component_type ON component_registry(component_type);
CREATE INDEX IF NOT EXISTS idx_component_status ON component_registry(status);
CREATE INDEX IF NOT EXISTS idx_component_tags ON component_registry(tags);

-- Per-system deployment tracking
CREATE TABLE IF NOT EXISTS component_deployments (
    id INTEGER PRIMARY KEY,
    component_id INTEGER REFERENCES component_registry(id) ON DELETE CASCADE,
    system TEXT NOT NULL,                   -- system identifier
    file_path TEXT,
    content_hash TEXT,
    last_verified TIMESTAMP,
    in_sync BOOLEAN DEFAULT 1,
    UNIQUE(component_id, system)
);

CREATE INDEX IF NOT EXISTS idx_deployment_system ON component_deployments(system);
CREATE INDEX IF NOT EXISTS idx_deployment_sync ON component_deployments(in_sync);

-- Reference library (assets, URLs, resources)
-- Note: client_id and competitor_id FKs work with domain-agency.sql tables if installed
CREATE TABLE IF NOT EXISTS reference_library (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,                      -- optional: requires domain-agency.sql
    competitor_id INTEGER,                  -- optional: requires domain-agency.sql
    resource_type TEXT NOT NULL,            -- image|website|article|video|tool|template
    url TEXT,
    title TEXT,
    description TEXT,
    use_cases TEXT,                         -- JSON array
    descriptors TEXT,                       -- JSON array
    quality_rating INTEGER,                 -- 1-5
    source TEXT,
    captured_by TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reference_type ON reference_library(resource_type);
CREATE INDEX IF NOT EXISTS idx_reference_client ON reference_library(client_id);
CREATE INDEX IF NOT EXISTS idx_reference_competitor ON reference_library(competitor_id);
CREATE INDEX IF NOT EXISTS idx_reference_tags ON reference_library(tags);
