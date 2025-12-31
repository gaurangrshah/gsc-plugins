<!-- WORKLOG_START -->
## Worklog Database (Standard Profile)

**Database:** ${WORKLOG_DB_PATH}
**Profile:** standard
**Hook Mode:** ${WORKLOG_HOOK_MODE}

### Automatic Behavior

Based on your hook mode setting:
- **light** (default): Auto-loads recent work + memories at session start; prompts to log at end
- **remind**: Just reminders, no auto-queries
- **full/aggressive**: More comprehensive context loading

**The hooks handle context loading automatically.** Manual queries below are for additional lookups.

### Boot Sequence (Manual Override)

If you need additional context beyond what hooks provide:

```bash
# Recent work (last 24h)
sqlite3 ${WORKLOG_DB_PATH} "SELECT timestamp, title, outcome
FROM entries WHERE timestamp > datetime('now', '-1 day')
ORDER BY timestamp DESC LIMIT 5;"

# Active memories
sqlite3 ${WORKLOG_DB_PATH} "SELECT key, summary, importance
FROM memories WHERE status != 'archived'
ORDER BY importance DESC LIMIT 5;"
```

### Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `memory-store` | Save learnings | After tasks with reusable insights |
| `memory-recall` | Query context | Starting tasks, debugging, decisions |
| `memory-sync` | Promote to docs | Weekly, after major milestones |

### Store Learnings

After completing tasks with reusable insights:

```bash
sqlite3 ${WORKLOG_DB_PATH} "INSERT INTO knowledge_base
(category, title, content, tags, source_agent) VALUES
('{category}', '{title}', '{content}', '{tags}', '{agent}');"
```

**Categories:** `system-administration`, `development`, `infrastructure`, `decisions`, `protocols`

### Log Work Completion

After significant tasks:

```bash
sqlite3 ${WORKLOG_DB_PATH} "INSERT INTO entries
(agent, task_type, title, details, outcome, tags) VALUES
('{agent}', '{type}', '{title}', '{details}', '{outcome}', '{tags}');"
```

### Query Patterns

```bash
# Search knowledge
sqlite3 ${WORKLOG_DB_PATH} "SELECT title, content FROM knowledge_base
WHERE tags LIKE '%keyword%' OR content LIKE '%keyword%';"

# Check for error resolution
sqlite3 ${WORKLOG_DB_PATH} "SELECT resolution FROM error_patterns
WHERE error_message LIKE '%error text%';"

# Recent work
sqlite3 ${WORKLOG_DB_PATH} "SELECT timestamp, title, outcome
FROM entries ORDER BY timestamp DESC LIMIT 10;"
```

### Tables

| Table | Purpose |
|-------|---------|
| `entries` | Work history |
| `knowledge_base` | Reusable learnings |
| `memories` | Working context |
| `sot_issues` | Issue tracking |
| `error_patterns` | Error resolutions |
| `research` | External research |

### Tagging Convention

Always include structured tags:
```
system:{system},agent:{agent},topic:{topic1},topic:{topic2}
```

Run `/worklog-status` to check connectivity.
Run `/worklog-configure` to change settings.
<!-- WORKLOG_END -->
