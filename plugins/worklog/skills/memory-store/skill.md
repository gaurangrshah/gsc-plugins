---
name: memory-store
description: Store knowledge, entries, errors, and context in the worklog database
---

# Memory Store Skill

Store information in the worklog database for cross-session persistence.

## Prerequisites

- Worklog plugin configured (run `/worklog-init` first)
- Database backend configured:
  - **SQLite (default)**: No additional setup needed
  - **PostgreSQL (optional)**: Set `DATABASE_URL` or `PGHOST` environment variables

## What to Store

### DO Store

| Type | Table | When |
|------|-------|------|
| Reusable learnings | `knowledge_base` | Patterns, gotchas, anti-patterns |
| Work completion | `entries` | After significant tasks |
| Error resolutions | `error_patterns` | When you solve a tricky error |
| Working context | `memories` | Session state, decisions in progress |
| Issues found | `issues` | Bugs, problems to track |

### DO NOT Store

| Type | Why Not | Alternative |
|------|---------|-------------|
| In-progress tasks | Transient | Use TodoWrite |
| Obvious code behavior | Documented in code | None needed |
| Already in files | Redundant | Reference the file |
| Trivial changes | No reuse value | None needed |

## Detect Your Backend

```bash
if [ -n "$DATABASE_URL" ] || [ -n "$PGHOST" ]; then
    echo "Backend: PostgreSQL (use psql)"
else
    echo "Backend: SQLite (use sqlite3)"
fi
```

---

## SQLite Store Patterns (Default)

Default database path: `~/.claude/worklog/worklog.db`

### Knowledge Base Entry

```bash
DB="${WORKLOG_DB_PATH:-$HOME/.claude/worklog/worklog.db}"

sqlite3 "$DB" "INSERT INTO knowledge_base
(category, title, content, tags, source_agent, system) VALUES (
'development',
'Title of the knowledge',
'Content with problem, solution, examples',
'system:shared,agent:claude,topic:example',
'claude',
'$(hostname)'
);"
```

### Work Entry

```bash
sqlite3 "$DB" "INSERT INTO entries
(agent, task_type, title, details, decision_rationale, outcome, tags) VALUES (
'claude',
'debugging',
'Fixed authentication bug',
'User sessions were expiring prematurely',
'Root cause was timezone mismatch',
'Sessions now persist correctly',
'system:$(hostname),agent:claude,topic:auth'
);"
```

### Memory

```bash
sqlite3 "$DB" "INSERT INTO memories
(key, content, summary, memory_type, importance, source_agent, tags) VALUES (
'ctx_claude_20251222_project_context',
'Detailed content here',
'Brief summary',
'context',
7,
'claude',
'system:$(hostname),agent:claude'
);"
```

### Error Pattern

```bash
sqlite3 "$DB" "INSERT INTO error_patterns
(error_signature, error_message, platform, language, root_cause, resolution, tags) VALUES (
'ECONNREFUSED',
'connect ECONNREFUSED 127.0.0.1:5432',
'all',
'all',
'PostgreSQL not running',
'Start PostgreSQL: brew services start postgresql',
'topic:postgresql,topic:connection'
);"
```

### Issue

```bash
sqlite3 "$DB" "INSERT INTO issues
(project, title, description, status, tags, source_agent) VALUES (
'my-project',
'API rate limiting needed',
'Users can make unlimited requests',
'open',
'topic:api,topic:security',
'claude'
);"
```

---

## PostgreSQL Store Patterns (Optional)

For multi-system setups with shared database.

### Knowledge Base Entry

```bash
psql -c "INSERT INTO knowledge_base
(category, title, content, tags, source_agent, system) VALUES (
'development',
'Title of the knowledge',
'Content with problem, solution, examples',
'system:shared,agent:claude,topic:example',
'claude',
'$(hostname)'
);"
```

### Work Entry

```bash
psql -c "INSERT INTO entries
(agent, task_type, title, details, decision_rationale, outcome, tags) VALUES (
'claude',
'debugging',
'Fixed authentication bug',
'User sessions were expiring prematurely',
'Root cause was timezone mismatch',
'Sessions now persist correctly',
'system:$(hostname),agent:claude,topic:auth'
);"
```

### Memory

```bash
psql -c "INSERT INTO memories
(key, content, summary, memory_type, importance, source_agent, tags) VALUES (
'ctx_claude_20251222_project_context',
'Detailed content here',
'Brief summary',
'context',
7,
'claude',
'system:$(hostname),agent:claude'
);"
```

### Error Pattern

```bash
psql -c "INSERT INTO error_patterns
(error_signature, error_message, platform, language, root_cause, resolution, tags) VALUES (
'ECONNREFUSED',
'connect ECONNREFUSED 127.0.0.1:5432',
'all',
'all',
'PostgreSQL not running',
'Start PostgreSQL: brew services start postgresql',
'topic:postgresql,topic:connection'
);"
```

### Issue

```bash
psql -c "INSERT INTO issues
(project, title, description, status, tags, source_agent) VALUES (
'my-project',
'API rate limiting needed',
'Users can make unlimited requests',
'open',
'topic:api,topic:security',
'claude'
);"
```

---

## MCP Tools (Backend-Agnostic)

The MCP server automatically uses the correct backend:

```python
# Store a memory
store_memory(
    key="ctx_claude_20251222_project",
    content="Detailed content",
    summary="Brief summary",
    memory_type="context",
    importance=7,
    tags="system:shared,agent:claude"
)

# Log work entry
log_entry(
    title="Fixed authentication bug",
    task_type="debugging",
    details="User sessions were expiring prematurely",
    outcome="Sessions now persist correctly",
    tags="system:shared,agent:claude,topic:auth"
)

# Store knowledge
store_knowledge(
    category="development",
    title="React useEffect cleanup",
    content="Always return cleanup function...",
    tags="topic:react,topic:hooks"
)
```

---

## Categories & Types

**Knowledge Base Categories:**
`system-administration`, `development`, `infrastructure`, `decisions`, `projects`, `protocols`

**Task Types:**
`configuration`, `deployment`, `debugging`, `documentation`, `research`, `maintenance`, `handoff`

**Memory Types:**
`fact`, `entity`, `preference`, `context`

**Platforms:**
`linux`, `macos`, `docker`, `nas`, `all`

**Languages:**
`python`, `typescript`, `bash`, `go`, `rust`, `all`

---

## Tagging Convention

Always include structured tags:

```
system:{system_name},agent:{agent_name},topic:{topic1},topic:{topic2}
```

Examples:
- `system:my-laptop,agent:claude,topic:docker,topic:networking`
- `system:shared,agent:claude,type:protocol,topic:sqlite`

---

## Content Format for Knowledge

```markdown
**Problem:** What was the issue

**Solution:** How to solve it

**Commands:**
```bash
example commands
```

**Notes:** Gotchas, warnings
```

---

## SQL Syntax Reference

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Boolean | `1` / `0` | `true` / `false` |
| Auto-increment | `INTEGER PRIMARY KEY` | `SERIAL` |
| Current time | `CURRENT_TIMESTAMP` | `CURRENT_TIMESTAMP` |

---

## Complete Example

### SQLite
```bash
DB="${WORKLOG_DB_PATH:-$HOME/.claude/worklog/worklog.db}"

sqlite3 "$DB" "INSERT INTO knowledge_base
(category, title, content, tags, source_agent, system, is_protocol) VALUES (
'development',
'React useEffect cleanup pattern',
'**Problem:** Memory leaks from uncleared intervals

**Solution:** Return cleanup function from useEffect

**Code:**
\`\`\`typescript
useEffect(() => {
  const id = setInterval(tick, 1000);
  return () => clearInterval(id);
}, []);
\`\`\`

**Notes:** Also applies to event listeners, subscriptions',
'system:shared,agent:claude,topic:react,topic:hooks,type:pattern',
'claude',
'$(hostname)',
0
);"
```

### PostgreSQL
```bash
psql -c "INSERT INTO knowledge_base
(category, title, content, tags, source_agent, system, is_protocol) VALUES (
'development',
'React useEffect cleanup pattern',
'**Problem:** Memory leaks from uncleared intervals

**Solution:** Return cleanup function from useEffect

**Code:**
\`\`\`typescript
useEffect(() => {
  const id = setInterval(tick, 1000);
  return () => clearInterval(id);
}, []);
\`\`\`

**Notes:** Also applies to event listeners, subscriptions',
'system:shared,agent:claude,topic:react,topic:hooks,type:pattern',
'claude',
'$(hostname)',
false
);"
```
