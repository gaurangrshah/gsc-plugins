---
event: SessionStart
priority: 100
match_files: ["*"]
---

# Session Start Hook - Worklog Context Loading

Automatically load relevant context from the worklog database at session start.

## Behavior by Profile

Read configuration from `~/.claude/worklog.local.md` frontmatter to determine behavior.

### Configuration Check

```bash
# Read hook_mode from config (defaults to profile-based)
HOOK_MODE=$(grep -A1 "^hook_mode:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
PROFILE=$(grep -A1 "^profile:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
DB_PATH=$(grep -A1 "^db_path:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')

# Expand ~ in path
DB_PATH="${DB_PATH/#\~/$HOME}"
```

### Hook Modes

| Mode | Behavior | Default For |
|------|----------|-------------|
| `off` | No auto-queries | - |
| `remind` | Just remind worklog exists | minimal |
| `light` | Query recent work + active memories | standard |
| `full` | Query protocols, work, issues, errors, memories | full |
| `aggressive` | Full + inject context into conversation | full (shared) |

## Execution

### Mode: off
Do nothing.

### Mode: remind

Output (as system context):
```
<worklog-reminder>
Worklog database available at {db_path}.
- Use `memory-recall` skill to query context
- Use `memory-store` skill to save learnings
</worklog-reminder>
```

### Mode: light

Query and output:
```bash
# Recent work (24h)
RECENT=$(sqlite3 "$DB_PATH" "SELECT datetime(timestamp,'localtime'), title, outcome FROM entries WHERE timestamp > datetime('now', '-1 day') ORDER BY timestamp DESC LIMIT 5;" 2>/dev/null)

# Active memories
MEMORIES=$(sqlite3 "$DB_PATH" "SELECT key, summary FROM memories WHERE status != 'archived' AND importance >= 5 ORDER BY importance DESC, last_accessed DESC LIMIT 5;" 2>/dev/null)
```

Output (as system context):
```
<worklog-context mode="light">
## Recent Work (24h)
{RECENT or "No recent entries"}

## Active Memories
{MEMORIES or "No active memories"}

Use `memory-store` after significant tasks.
</worklog-context>
```

### Mode: full

Query all context areas:
```bash
# Protocols
PROTOCOLS=$(sqlite3 "$DB_PATH" "SELECT title FROM knowledge_base WHERE is_protocol = 1 ORDER BY updated_at DESC LIMIT 3;" 2>/dev/null)

# Recent work
RECENT=$(sqlite3 "$DB_PATH" "SELECT agent, title, outcome FROM entries WHERE timestamp > datetime('now', '-1 day') ORDER BY timestamp DESC LIMIT 10;" 2>/dev/null)

# Open issues
ISSUES=$(sqlite3 "$DB_PATH" "SELECT project, title FROM issues WHERE status = 'open' ORDER BY created_at DESC LIMIT 5;" 2>/dev/null)

# Recent errors
ERRORS=$(sqlite3 "$DB_PATH" "SELECT error_signature, resolution FROM error_patterns WHERE last_seen > datetime('now', '-7 days') ORDER BY occurrence_count DESC LIMIT 3;" 2>/dev/null)

# Important memories
MEMORIES=$(sqlite3 "$DB_PATH" "SELECT key, summary FROM memories WHERE status = 'promoted' OR importance >= 8 ORDER BY importance DESC LIMIT 5;" 2>/dev/null)
```

Output (as system context):
```
<worklog-context mode="full">
## Active Protocols
{PROTOCOLS or "None defined"}

## Recent Work (24h)
{RECENT or "No recent entries"}

## Open Issues
{ISSUES or "No open issues"}

## Known Error Patterns (7d)
{ERRORS or "None recorded"}

## Important Memories
{MEMORIES or "No promoted memories"}

---
**Worklog Active:** Store learnings with `memory-store`. Query with `memory-recall`.
</worklog-context>
```

### Mode: aggressive

Same as `full` but also:
1. Update last_accessed on queried memories
2. Log session start to entries table
3. Check for entries flagged for this system

Additional queries:
```bash
# Entries for this system
FLAGGED=$(sqlite3 "$DB_PATH" "SELECT title, details FROM entries WHERE tags LIKE '%for:$(hostname)%' AND timestamp > datetime('now', '-7 days');" 2>/dev/null)

# Log session start
sqlite3 "$DB_PATH" "INSERT INTO entries (agent, task_type, title, outcome, tags) VALUES ('$(hostname)', 'session', 'Session started', 'Auto-logged by hook', 'system:$(hostname),type:session-start');" 2>/dev/null
```

Output includes flagged items:
```
<worklog-context mode="aggressive">
{...full mode content...}

## Flagged for This System
{FLAGGED or "Nothing flagged"}

---
**Worklog Active (Aggressive):** Auto-storing enabled. Session logged.
</worklog-context>
```

## Error Handling

If database is unreachable:
```
<worklog-warning>
Worklog database not accessible at {db_path}.
Run `/worklog-status` to diagnose.
</worklog-warning>
```

If config missing:
```
<worklog-warning>
Worklog not configured. Run `/worklog-init` to set up.
</worklog-warning>
```

## Notes

- This hook runs in the background and injects context
- Output appears before the user's first message is processed
- Keep queries fast (<500ms target) to avoid slowing session start
- Network databases may timeout - gracefully degrade to remind mode
