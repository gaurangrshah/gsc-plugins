---
name: memory-recall
description: Query the worklog database for context, knowledge, errors, and history using direct SQL
---

# Memory Recall Skill

Query the worklog database for relevant context, prior knowledge, and history.

## Prerequisites

- Worklog plugin configured (run `/worklog-init` or `/worklog-connect` first)
- Database path from `.claude/worklog.local.md`

## When to Use

| Scenario | Query Type |
|----------|------------|
| Starting a task | Boot queries for relevant context |
| Debugging an error | Search error_patterns |
| Making a decision | Check knowledge_base for precedents |
| Continuing previous work | Query entries and memories |
| Learning about a topic | Search across all tables |

## Boot Sequence Queries

Run these at the start of non-trivial tasks to load relevant context.

### Light Boot (STANDARD profile)

```sql
-- Recent work entries (last 24h)
SELECT timestamp, title, outcome
FROM entries
WHERE timestamp > datetime('now', '-1 day')
ORDER BY timestamp DESC LIMIT 5;

-- Active memories
SELECT key, summary, importance
FROM memories
WHERE status != 'archived'
ORDER BY importance DESC, last_accessed DESC LIMIT 5;
```

### Full Boot (FULL profile)

```sql
-- Protocols (always relevant)
SELECT title, substr(content, 1, 300)
FROM knowledge_base
WHERE is_protocol = 1
ORDER BY updated_at DESC LIMIT 3;

-- Recent work across all agents
SELECT agent, title, outcome
FROM entries
WHERE timestamp > datetime('now', '-1 day')
ORDER BY timestamp DESC LIMIT 10;

-- Open issues
SELECT project, title, status
FROM issues
WHERE status = 'open'
ORDER BY created_at DESC LIMIT 5;

-- Recent errors (might be relevant)
SELECT error_signature, resolution
FROM error_patterns
WHERE last_seen > datetime('now', '-7 days')
ORDER BY occurrence_count DESC LIMIT 3;

-- Important memories
SELECT key, content, importance
FROM memories
WHERE status = 'promoted' OR importance >= 8
ORDER BY importance DESC LIMIT 5;
```

## Query Patterns

### Search Knowledge Base

```bash
# By tag
sqlite3 {db_path} "SELECT id, title, content
FROM knowledge_base
WHERE tags LIKE '%{tag}%'
ORDER BY updated_at DESC;"

# By category
sqlite3 {db_path} "SELECT title, content
FROM knowledge_base
WHERE category = '{category}'
ORDER BY updated_at DESC LIMIT 10;"

# Full-text search
sqlite3 {db_path} "SELECT title, content
FROM knowledge_base
WHERE content LIKE '%{search_term}%' OR title LIKE '%{search_term}%'
ORDER BY updated_at DESC;"

# Protocols only
sqlite3 {db_path} "SELECT title, content
FROM knowledge_base
WHERE is_protocol = 1
ORDER BY updated_at DESC;"
```

### Search Work History

```bash
# By agent
sqlite3 {db_path} "SELECT timestamp, title, outcome
FROM entries
WHERE agent = '{agent_name}'
ORDER BY timestamp DESC LIMIT 20;"

# By task type
sqlite3 {db_path} "SELECT timestamp, agent, title, outcome
FROM entries
WHERE task_type = '{task_type}'
ORDER BY timestamp DESC LIMIT 10;"

# By date range
sqlite3 {db_path} "SELECT timestamp, title, outcome
FROM entries
WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
ORDER BY timestamp DESC;"

# Recent across all agents
sqlite3 {db_path} "SELECT timestamp, agent, title, outcome
FROM entries
ORDER BY timestamp DESC LIMIT 20;"
```

### Search Error Patterns

```bash
# By error text
sqlite3 {db_path} "SELECT error_signature, root_cause, resolution
FROM error_patterns
WHERE error_message LIKE '%{error_text}%'
   OR error_signature LIKE '%{error_text}%';"

# By platform
sqlite3 {db_path} "SELECT error_signature, resolution
FROM error_patterns
WHERE platform = '{platform}' OR platform = 'all'
ORDER BY occurrence_count DESC;"

# By language
sqlite3 {db_path} "SELECT error_signature, resolution
FROM error_patterns
WHERE language = '{language}' OR language = 'all'
ORDER BY occurrence_count DESC;"

# Most frequent errors
sqlite3 {db_path} "SELECT error_signature, occurrence_count, resolution
FROM error_patterns
ORDER BY occurrence_count DESC LIMIT 10;"
```

### Query Memories

```bash
# Active memories
sqlite3 {db_path} "SELECT key, content, importance
FROM memories
WHERE status != 'archived'
ORDER BY importance DESC, last_accessed DESC;"

# By type
sqlite3 {db_path} "SELECT key, content
FROM memories
WHERE memory_type = '{type}'
ORDER BY importance DESC;"

# Search by tag
sqlite3 {db_path} "SELECT key, content, summary
FROM memories
WHERE tags LIKE '%{tag}%'
ORDER BY importance DESC;"

# Update access count when reading
sqlite3 {db_path} "UPDATE memories
SET access_count = access_count + 1,
    last_accessed = CURRENT_TIMESTAMP
WHERE key = '{key}';"
```

### Query Issues

```bash
# Open issues
sqlite3 {db_path} "SELECT id, project, title, created_at
FROM issues
WHERE status = 'open'
ORDER BY created_at DESC;"

# By project
sqlite3 {db_path} "SELECT title, status, resolution
FROM issues
WHERE project = '{project}'
ORDER BY created_at DESC;"

# Resolved with solutions
sqlite3 {db_path} "SELECT title, description, resolution
FROM issues
WHERE status = 'resolved'
ORDER BY resolved_at DESC LIMIT 10;"
```

## Cross-Table Search

Find information across all tables:

```bash
sqlite3 {db_path} "
SELECT 'knowledge' as source, title, substr(content, 1, 100) as preview
FROM knowledge_base WHERE content LIKE '%{term}%'
UNION ALL
SELECT 'entry' as source, title, outcome as preview
FROM entries WHERE details LIKE '%{term}%' OR outcome LIKE '%{term}%'
UNION ALL
SELECT 'error' as source, error_signature as title, resolution as preview
FROM error_patterns WHERE error_message LIKE '%{term}%'
UNION ALL
SELECT 'memory' as source, key as title, summary as preview
FROM memories WHERE content LIKE '%{term}%'
LIMIT 20;"
```

## Task-Specific Queries

### Before Debugging

```sql
-- Check for known error patterns
SELECT error_signature, root_cause, resolution
FROM error_patterns
WHERE error_message LIKE '%{error_snippet}%'
ORDER BY occurrence_count DESC LIMIT 5;

-- Check recent similar issues
SELECT title, resolution
FROM issues
WHERE title LIKE '%{keyword}%' OR description LIKE '%{keyword}%'
ORDER BY resolved_at DESC LIMIT 5;
```

### Before Architecture Decision

```sql
-- Check precedents
SELECT title, content
FROM knowledge_base
WHERE category = 'decisions'
  AND (title LIKE '%{topic}%' OR tags LIKE '%{topic}%')
ORDER BY updated_at DESC;

-- Check relevant protocols
SELECT title, content
FROM knowledge_base
WHERE is_protocol = 1
  AND (content LIKE '%{topic}%' OR tags LIKE '%{topic}%');
```

### Before Starting Project Work

```sql
-- Project context (if FULL profile)
SELECT name, description, status, notes
FROM projects
WHERE name = '{project}';

-- Recent work on this project
SELECT timestamp, title, outcome
FROM entries
WHERE tags LIKE '%project:{project}%'
ORDER BY timestamp DESC LIMIT 10;

-- Open issues for project
SELECT title, status
FROM issues
WHERE project = '{project}' AND status = 'open';
```

## Output Formatting

When presenting recalled information:

```
## Prior Knowledge Found

### From Knowledge Base
**{title}** (Category: {category})
{content_excerpt}

### From Work History
- {timestamp}: {title} → {outcome}
- {timestamp}: {title} → {outcome}

### Relevant Error Patterns
**{error_signature}**
Resolution: {resolution}
```
