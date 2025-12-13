-- Worklog Domain Extension: Agency/Client Work
-- Version: 1.0.0
-- Tables: 2 (clients, competitors)
-- Requires: core.sql (and optionally extended.sql for reference_library FKs)
--
-- Purpose: Domain-specific tables for agency/consultancy workflows
-- tracking client entities and competitor research.
--
-- Install: sqlite3 $WORKLOG_DB_PATH < domain-agency.sql

-- Client entities (PII-safe)
-- Use client_code for identifiers, avoid storing actual PII
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    client_code TEXT UNIQUE NOT NULL,       -- sanitized identifier (no PII)
    display_name TEXT,                      -- sanitized display name
    industry TEXT,
    status TEXT DEFAULT 'active',           -- active|inactive|archived
    notes TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clients_industry ON clients(industry);
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);

-- Competitor profiles
-- For tracking competitor research per client
CREATE TABLE IF NOT EXISTS competitors (
    id INTEGER PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    competitor_name TEXT NOT NULL,
    industry TEXT,
    website TEXT,
    industry_position TEXT,                 -- leader|challenger|niche|emerging
    strengths TEXT,                         -- JSON array
    weaknesses TEXT,                        -- JSON array
    brand_voice_notes TEXT,
    visual_style_notes TEXT,
    marketing_channels TEXT,                -- JSON array
    file_path TEXT,                         -- path to full profile directory
    completeness TEXT,                      -- JSON: which elements exist
    last_researched TIMESTAMP,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_competitors_industry ON competitors(industry);
CREATE INDEX IF NOT EXISTS idx_competitors_client ON competitors(client_id);
CREATE INDEX IF NOT EXISTS idx_competitors_tags ON competitors(tags);

-- If you have reference_library from extended.sql, you can link entries:
-- UPDATE reference_library SET client_id = X WHERE ...
-- UPDATE reference_library SET competitor_id = Y WHERE ...
