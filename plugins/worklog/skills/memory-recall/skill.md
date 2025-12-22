---
name: memory-recall
description: Query the worklog database for context, knowledge, errors, and history
---

# Memory Recall Skill

Query the worklog database to retrieve context, knowledge, and history.

## Prerequisites

- Worklog plugin configured (run `/worklog-init` first)
- Database backend configured:
  - **SQLite (default)**: No additional setup needed
  - **PostgreSQL (optional)**: Set `DATABASE_URL` or `PGHOST` environment variables

## When to Recall

| Scenario | Query Type |
|----------|------------|
| Starting a task | Boot queries for relevant context |
| Debugging an error | Search error_patterns |
| Making a decision | Check knowledge_base for precedents |
| Continuing previous work | Query entries and memories |
| Learning about a topic | Search across all tables |

## Detect Your Backend

```bash
# Check which backend is configured
if [ -n "$DATABASE_URL" ] || [ -n "$PGHOST" ]; then
    echo "Backend: PostgreSQL"
else
    echo "Backend: SQLite"
fi
```

---

## SQLite Queries (Default)

Default database path: `~/.claude/worklog/worklog.db`

### Boot Sequence

```bash
DB="${WORKLOG_DB_PATH:-$HOME/.claude/worklog/worklog.db}"

# Protocols
sqlite3 "$DB" "SELECT title FROM knowledge_base WHERE is_protocol=1 ORDER BY updated_at DESC LIMIT 5;"

# Recent work (24h)
sqlite3 "$DB" "SELECT agent, title FROM entries WHERE timestamp > datetime('now', '-1 day') ORDER BY timestamp DESC LIMIT 5;"

# Items flagged for me
sqlite3 "$DB" "SELECT title FROM entries WHERE tags LIKE '%for:claude%' AND timestamp > datetime('now', '-7 days');"
```

### Search Knowledge Base

```bash
# By topic
sqlite3 "$DB" "SELECT id, title FROM knowledge_base WHERE title LIKE '%topic%' OR content LIKE '%topic%' ORDER BY updated_at DESC LIMIT 10;"

# By category
sqlite3 "$DB" "SELECT title, content FROM knowledge_base WHERE category = 'development' ORDER BY updated_at DESC LIMIT 10;"

# Protocols only
sqlite3 "$DB" "SELECT title, content FROM knowledge_base WHERE is_protocol = 1 ORDER BY updated_at DESC;"
```

### Search Work History

```bash
# By agent
sqlite3 "$DB" "SELECT timestamp, title, outcome FROM entries WHERE agent = 'jarvis' ORDER BY timestamp DESC LIMIT 20;"

# By task type
sqlite3 "$DB" "SELECT timestamp, agent, title FROM entries WHERE task_type = 'debugging' ORDER BY timestamp DESC LIMIT 10;"

# Recent across all agents
sqlite3 "$DB" "SELECT timestamp, agent, title FROM entries ORDER BY timestamp DESC LIMIT 20;"
```

### Search Error Patterns

```bash
# By error text
sqlite3 "$DB" "SELECT error_signature, resolution FROM error_patterns WHERE error_message LIKE '%error text%' LIMIT 5;"

# By platform
sqlite3 "$DB" "SELECT error_signature, resolution FROM error_patterns WHERE platform = 'macos' ORDER BY id DESC LIMIT 10;"
```

### Query Memories

```bash
# By key
sqlite3 "$DB" "SELECT content FROM memories WHERE key = 'ctx_agent_date_slug';"

# High importance
sqlite3 "$DB" "SELECT key, summary FROM memories WHERE importance >= 7 ORDER BY importance DESC LIMIT 10;"

# Active memories
sqlite3 "$DB" "SELECT key, summary FROM memories WHERE status != 'archived' ORDER BY importance DESC LIMIT 10;"
```

---

## PostgreSQL Queries (Optional)

For multi-system setups with shared database.

### Boot Sequence

```bash
# Protocols
psql -t -c "SELECT title FROM knowledge_base WHERE is_protocol=true ORDER BY updated_at DESC LIMIT 5;"

# Recent work (24h)
psql -t -c "SELECT agent, title FROM entries WHERE timestamp > NOW() - INTERVAL '1 day' ORDER BY timestamp DESC LIMIT 5;"

# Items flagged for me
psql -t -c "SELECT title FROM entries WHERE tags LIKE '%for:claude%' AND timestamp > NOW() - INTERVAL '7 days';"
```

### Search Knowledge Base

```bash
# By topic (ILIKE for case-insensitive)
psql -t -c "SELECT id, title FROM knowledge_base WHERE title ILIKE '%topic%' OR content ILIKE '%topic%' ORDER BY updated_at DESC LIMIT 10;"

# By category
psql -t -c "SELECT title, content FROM knowledge_base WHERE category = 'development' ORDER BY updated_at DESC LIMIT 10;"

# Protocols only
psql -t -c "SELECT title, content FROM knowledge_base WHERE is_protocol = true ORDER BY updated_at DESC;"
```

### Search Work History

```bash
# By agent
psql -t -c "SELECT timestamp, title, outcome FROM entries WHERE agent = 'jarvis' ORDER BY timestamp DESC LIMIT 20;"

# By task type
psql -t -c "SELECT timestamp, agent, title FROM entries WHERE task_type = 'debugging' ORDER BY timestamp DESC LIMIT 10;"

# Recent across all agents
psql -t -c "SELECT timestamp, agent, title FROM entries ORDER BY timestamp DESC LIMIT 20;"
```

### Search Error Patterns

```bash
# By error text
psql -t -c "SELECT error_signature, resolution FROM error_patterns WHERE error_message ILIKE '%error text%' LIMIT 5;"

# By platform
psql -t -c "SELECT error_signature, resolution FROM error_patterns WHERE platform = 'macos' ORDER BY id DESC LIMIT 10;"
```

### Query Memories

```bash
# By key
psql -t -c "SELECT content FROM memories WHERE key = 'ctx_agent_date_slug';"

# High importance
psql -t -c "SELECT key, summary FROM memories WHERE importance >= 7 ORDER BY importance DESC LIMIT 10;"

# Active memories
psql -t -c "SELECT key, summary FROM memories WHERE status != 'archived' ORDER BY importance DESC LIMIT 10;"
```

---

## MCP Tools (Backend-Agnostic)

The MCP server automatically uses the correct backend:

```python
# Search across tables
search_knowledge(query="topic", tables="knowledge_base,entries")

# Get context for a task
recall_context(topic="docker deployment", min_importance=5)

# Query specific table
query_table(table="entries", where="agent='jarvis'", limit=10)

# Get recent entries
get_recent_entries(days=7, limit=20)
```

---

## SQL Syntax Reference

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Case-insensitive | `LIKE` (default) | `ILIKE` |
| Days ago | `datetime('now', '-7 days')` | `NOW() - INTERVAL '7 days'` |
| Boolean | `1` / `0` | `true` / `false` |
| Last insert ID | `last_insert_rowid()` | `RETURNING id` |

## Cross-Table Search

### SQLite
```bash
sqlite3 "$DB" "
SELECT 'knowledge' as source, title, substr(content, 1, 100) as preview
FROM knowledge_base WHERE content LIKE '%term%'
UNION ALL
SELECT 'entry' as source, title, outcome as preview
FROM entries WHERE details LIKE '%term%'
LIMIT 20;"
```

### PostgreSQL
```bash
psql -t -c "
SELECT 'knowledge' as source, title, substring(content, 1, 100) as preview
FROM knowledge_base WHERE content ILIKE '%term%'
UNION ALL
SELECT 'entry' as source, title, outcome as preview
FROM entries WHERE details ILIKE '%term%'
LIMIT 20;"
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

### Relevant Error Patterns
**{error_signature}**
Resolution: {resolution}
```
