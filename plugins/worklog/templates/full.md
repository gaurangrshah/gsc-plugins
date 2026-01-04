<!-- WORKLOG_START -->
## Worklog Database (Full Profile)

**Database:** ${WORKLOG_DB_PATH}
**Profile:** full
**Mode:** ${WORKLOG_MODE}
**Hook Mode:** ${WORKLOG_HOOK_MODE}

### Automatic Behavior

Based on your hook mode setting:
- **full** (default): Auto-loads all context (protocols, work, issues, errors, memories); auto-logs session summaries
- **aggressive**: Everything in full + auto-extracts learnings to knowledge_base, logs session starts
- **light/remind**: Reduced automation (consider upgrading for full profile benefits)

**The hooks handle most context loading and logging automatically.** Manual queries below are for specialized lookups.

### Boot Sequence (Manual Override)

For additional context beyond automatic hooks, or if hooks are disabled:

```bash
# Protocols (always check first)
sqlite3 ${WORKLOG_DB_PATH} "SELECT title, substr(content, 1, 300)
FROM knowledge_base WHERE is_protocol = 1
ORDER BY updated_at DESC LIMIT 3;"

# Recent work across all agents
sqlite3 ${WORKLOG_DB_PATH} "SELECT agent, title, outcome
FROM entries WHERE timestamp > datetime('now', '-1 day')
ORDER BY timestamp DESC LIMIT 10;"

# Recent error patterns
sqlite3 ${WORKLOG_DB_PATH} "SELECT error_signature, resolution
FROM error_patterns WHERE last_seen > datetime('now', '-7 days')
ORDER BY occurrence_count DESC LIMIT 3;"

# Important memories
sqlite3 ${WORKLOG_DB_PATH} "SELECT key, summary
FROM memories WHERE status = 'promoted' OR importance >= 8
ORDER BY importance DESC LIMIT 5;"
```

### Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `memory-store` | Save learnings | After tasks with reusable insights |
| `memory-recall` | Query context | Starting tasks, debugging, decisions |
| `memory-sync` | Promote to docs | Weekly, after major milestones |

### Store Operations

**Knowledge (reusable learnings):**
```bash
sqlite3 ${WORKLOG_DB_PATH} "INSERT INTO knowledge_base
(category, title, content, tags, source_agent, is_protocol) VALUES
('{category}', '{title}', '{content}', '{tags}', '{agent}', {0|1});"
```

**Work entry (task completion):**
```bash
sqlite3 ${WORKLOG_DB_PATH} "INSERT INTO entries
(agent, task_type, title, details, decision_rationale, outcome, tags) VALUES
('{agent}', '{type}', '{title}', '{details}', '{rationale}', '{outcome}', '{tags}');"
```

**Error pattern (debugging win):**
```bash
sqlite3 ${WORKLOG_DB_PATH} "INSERT INTO error_patterns
(error_signature, error_message, platform, language, root_cause, resolution, tags) VALUES
('{signature}', '{message}', '{platform}', '{language}', '{cause}', '{fix}', '{tags}');"
```

**Memory (working context):**
```bash
sqlite3 ${WORKLOG_DB_PATH} "INSERT INTO memories
(key, content, summary, memory_type, importance, source_agent, tags) VALUES
('{key}', '{content}', '{summary}', '{type}', {importance}, '{agent}', '{tags}');"
```

### Network Write Protocol

For shared databases, use retry logic:

```bash
for i in 1 2 3; do
  sqlite3 ${WORKLOG_DB_PATH} "YOUR SQL" && break
  echo "Attempt $i failed, waiting..."
  sleep $((5 + RANDOM % 6))
done
```

**If all retries fail:** Create handoff file for another system to process:
```bash
cat > ${WORKLOG_HANDOFF_DIR}/$(hostname)-$(date +%Y%m%d%H%M%S).md << 'EOF'
# Handoff: {title}
{SQL to execute}
EOF
```

### Tables (Core)

| Table | Purpose |
|-------|---------|
| `entries` | Work history |
| `knowledge_base` | Reusable learnings, protocols |
| `memories` | Working context |
| `error_patterns` | Error resolutions |
| `research` | External research |

### Tables (Extended)

| Table | Purpose |
|-------|---------|
| `projects` | Project registry |
| `component_registry` | Agents, skills, commands |
| `component_deployments` | Per-system deployments |
| `reference_library` | Research assets |

### Tables (Domain: Agency) - Optional

| Table | Purpose |
|-------|---------|
| `clients` | Client entities |
| `competitors` | Competitor profiles |

Install: `sqlite3 ${WORKLOG_DB_PATH} < schema/domain-agency.sql`

### Tagging Convention

Always include structured tags:
```
system:{system},agent:{agent},topic:{topic1},topic:{topic2}
```

### Cross-System Coordination

Query for work from other systems:
```bash
sqlite3 ${WORKLOG_DB_PATH} "SELECT agent, title, outcome
FROM entries WHERE agent != '${SYSTEM_NAME}'
AND timestamp > datetime('now', '-1 day');"
```

Check for entries flagged for this system:
```bash
sqlite3 ${WORKLOG_DB_PATH} "SELECT title, details
FROM entries WHERE tags LIKE '%for:${SYSTEM_NAME}%';"
```

### Commands

- `/worklog-status` - Check connectivity and stats
- `/worklog-configure` - Change profile or settings
- `/worklog-connect` - Connect additional systems

<!-- WORKLOG_END -->
