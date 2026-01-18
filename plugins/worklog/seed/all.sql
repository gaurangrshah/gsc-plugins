-- Worklog Seed Data: Master File
-- Run this after schema creation to populate default data
--
-- Usage (SQLite):
--   sqlite3 ~/.claude/worklog/worklog.db < seed/all.sql
--
-- Usage (PostgreSQL):
--   psql -d worklog -f seed/all.sql

-- Tag taxonomy for consistent tagging
\i tag_taxonomy.sql

-- Core topics for knowledge organization
\i topics.sql

-- Bootstrap knowledge entries
\i knowledge.sql

-- Verification
SELECT 'Seed data loaded:' as status;
SELECT 'tag_taxonomy: ' || COUNT(*) || ' entries' FROM tag_taxonomy;
SELECT 'topic_index: ' || COUNT(*) || ' entries' FROM topic_index;
SELECT 'knowledge_base: ' || COUNT(*) || ' entries' FROM knowledge_base;
