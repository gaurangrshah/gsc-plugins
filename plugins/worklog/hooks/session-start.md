---
event: SessionStart
priority: 100
match_files: ["*"]
---

# Session Start Hook - Worklog Context Loading

Automatically load relevant context from the worklog database at session start using **progressive disclosure** - inject summaries first, fetch full details on-demand.

## Progressive Disclosure Pattern

Inspired by claude-mem's token-efficient approach:

| Layer | What | When | Token Cost |
|-------|------|------|------------|
| **1. Index** | Summary of available context | Always (SessionStart) | ~100-300 tokens |
| **2. Details** | Full content for selected items | On-demand (memory-recall) | ~500-2000 tokens |
| **3. Source** | Original entries/queries | Explicit request | Variable |

**Why:** Dumping all context wastes tokens. Index-first lets the agent decide what's relevant.

## Behavior by Hook Mode

Read configuration from `~/.gsc-plugins/worklog.local.md` frontmatter.

### Configuration Check

```bash
# Read settings from config
HOOK_MODE=$(grep -A1 "^hook_mode:" ~/.gsc-plugins/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
PROFILE=$(grep -A1 "^profile:" ~/.gsc-plugins/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
DB_PATH=$(grep -A1 "^db_path:" ~/.gsc-plugins/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
SYSTEM_NAME=$(grep -A1 "^system_name:" ~/.gsc-plugins/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')

# Expand ~ in path
DB_PATH="${DB_PATH/#\~/$HOME}"

# Default system name to hostname
SYSTEM_NAME="${SYSTEM_NAME:-$(hostname)}"
```

### Hook Modes

| Mode | Index Injection | Full Content | Default For |
|------|-----------------|--------------|-------------|
| `off` | None | None | - |
| `remind` | Reminder only | None | minimal |
| `light` | Summary index | On-demand | standard |
| `full` | Detailed index | On-demand | full |
| `aggressive` | Detailed index + auto-fetch critical | Auto for high-priority | full (shared) |

## Execution

### Mode: off

Do nothing.

### Mode: remind

Output (as system context):
```
<worklog-reminder>
Worklog database available at {db_path}.
Use `memory-recall` skill to query context. Use `memory-store` skill to save learnings.
</worklog-reminder>
```

### Mode: light

**Step 1: Query counts and summaries (fast queries only)**

```bash
# Count recent work (24h)
WORK_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM entries WHERE timestamp > datetime('now', '-1 day');" 2>/dev/null)

# Count active memories
MEMORY_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM memories WHERE status != 'archived' AND importance >= 5;" 2>/dev/null)

# Get top 3 memory keys (index only, not full content)
MEMORY_INDEX=$(sqlite3 "$DB_PATH" "SELECT key || ' [' || importance || ']' FROM memories WHERE status != 'archived' AND importance >= 5 ORDER BY importance DESC, last_accessed DESC LIMIT 3;" 2>/dev/null)

# Get most recent work titles (index only)
WORK_INDEX=$(sqlite3 "$DB_PATH" "SELECT title FROM entries WHERE timestamp > datetime('now', '-1 day') ORDER BY timestamp DESC LIMIT 3;" 2>/dev/null)
```

**Step 2: Output summary index**

```
<worklog-context mode="light" disclosure="index">
## Available Context

| Category | Count | Est. Tokens | Top Items |
|----------|-------|-------------|-----------|
| Recent Work (24h) | {WORK_COUNT} | ~{WORK_COUNT * 150} | {WORK_INDEX or "None"} |
| Active Memories | {MEMORY_COUNT} | ~{MEMORY_COUNT * 200} | {MEMORY_INDEX or "None"} |

**To fetch full details:** Use `memory-recall` skill with category filter.
**To store learnings:** Use `memory-store` skill after significant work.
</worklog-context>
```

### Mode: full

**Step 1: Query counts across all categories**

```bash
# Protocols
PROTOCOL_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM knowledge_base WHERE category = 'protocols' OR tags LIKE '%protocol%';" 2>/dev/null)
PROTOCOL_INDEX=$(sqlite3 "$DB_PATH" "SELECT title FROM knowledge_base WHERE category = 'protocols' OR tags LIKE '%protocol%' ORDER BY updated_at DESC LIMIT 3;" 2>/dev/null)

# Recent work
WORK_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM entries WHERE timestamp > datetime('now', '-1 day');" 2>/dev/null)
WORK_INDEX=$(sqlite3 "$DB_PATH" "SELECT title FROM entries WHERE timestamp > datetime('now', '-1 day') ORDER BY timestamp DESC LIMIT 3;" 2>/dev/null)

# Recent errors (7d)
ERROR_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM error_patterns WHERE last_seen > datetime('now', '-7 days');" 2>/dev/null)
ERROR_INDEX=$(sqlite3 "$DB_PATH" "SELECT error_signature FROM error_patterns WHERE last_seen > datetime('now', '-7 days') ORDER BY occurrence_count DESC LIMIT 3;" 2>/dev/null)

# Important memories
MEMORY_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM memories WHERE status = 'promoted' OR importance >= 7;" 2>/dev/null)
MEMORY_INDEX=$(sqlite3 "$DB_PATH" "SELECT key || ' [' || importance || ']' FROM memories WHERE status = 'promoted' OR importance >= 7 ORDER BY importance DESC LIMIT 3;" 2>/dev/null)

# Knowledge base (recent/relevant)
KB_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM knowledge_base WHERE updated_at > datetime('now', '-7 days');" 2>/dev/null)
KB_INDEX=$(sqlite3 "$DB_PATH" "SELECT title FROM knowledge_base WHERE updated_at > datetime('now', '-7 days') ORDER BY updated_at DESC LIMIT 3;" 2>/dev/null)
```

**Step 2: Output detailed index**

```
<worklog-context mode="full" disclosure="index">
## Available Context Index

| Category | Count | Est. Tokens | Recent/Top Items |
|----------|-------|-------------|------------------|
| Protocols | {PROTOCOL_COUNT} | ~{PROTOCOL_COUNT * 300} | {PROTOCOL_INDEX or "None"} |
| Recent Work (24h) | {WORK_COUNT} | ~{WORK_COUNT * 150} | {WORK_INDEX or "None"} |
| Error Patterns (7d) | {ERROR_COUNT} | ~{ERROR_COUNT * 250} | {ERROR_INDEX or "None"} |
| Important Memories | {MEMORY_COUNT} | ~{MEMORY_COUNT * 200} | {MEMORY_INDEX or "None"} |
| Knowledge Base (7d) | {KB_COUNT} | ~{KB_COUNT * 400} | {KB_INDEX or "None"} |

### Quick Actions

- **Fetch category:** `memory-recall` with `category: <name>`
- **Search all:** `memory-recall` with `query: <search term>`
- **Store learning:** `memory-store` after significant work

**Tip:** Only fetch what's relevant to the current task.
</worklog-context>
```

### Mode: aggressive

Same index as `full`, PLUS:

1. **Auto-fetch critical items** (importance >= 9 or status = 'critical')
2. **Update last_accessed** on displayed memories
3. **Log session start** to entries table
4. **Check for flagged items** for this system

**Step 1: Additional queries**

```bash
# Critical memories (auto-fetch full content)
CRITICAL=$(sqlite3 "$DB_PATH" "SELECT key, content FROM memories WHERE importance >= 9 OR status = 'critical' LIMIT 3;" 2>/dev/null)

# Flagged for this system
FLAGGED=$(sqlite3 "$DB_PATH" "SELECT title, details FROM entries WHERE tags LIKE '%for:$SYSTEM_NAME%' AND timestamp > datetime('now', '-7 days');" 2>/dev/null)

# Log session start
sqlite3 "$DB_PATH" "INSERT INTO entries (agent, task_type, title, outcome, tags) VALUES ('$SYSTEM_NAME', 'session', 'Session started', 'Auto-logged by hook', 'system:$SYSTEM_NAME,type:session-start');" 2>/dev/null

# Update last_accessed on critical memories
sqlite3 "$DB_PATH" "UPDATE memories SET last_accessed = datetime('now') WHERE importance >= 9 OR status = 'critical';" 2>/dev/null
```

**Step 2: Output with auto-fetched critical items**

```
<worklog-context mode="aggressive" disclosure="index+critical">
## Available Context Index

{...same table as full mode...}

## Critical Items (Auto-Fetched)

{CRITICAL or "No critical items"}

## Flagged for {SYSTEM_NAME}

{FLAGGED or "Nothing flagged for this system"}

---
**Worklog Active (Aggressive):** Session logged. Critical items pre-loaded.
Use `memory-recall` for additional context. Use `memory-store` to capture learnings.
</worklog-context>
```

## Error Handling

**Database unreachable:**
```
<worklog-warning>
Worklog database not accessible at {db_path}.
Run `/worklog-status` to diagnose. Continuing without context.
</worklog-warning>
```

**Config missing:**
```
<worklog-warning>
Worklog not configured. Run `/worklog-init` to set up.
</worklog-warning>
```

**Network timeout (>500ms):**
Gracefully degrade to `remind` mode:
```
<worklog-warning>
Worklog query timed out (network database). Degrading to remind mode.
Use `memory-recall` to manually fetch context when needed.
</worklog-warning>
```

## Token Efficiency

| Mode | Typical Injection | vs. Old Full Dump |
|------|-------------------|-------------------|
| remind | ~50 tokens | N/A |
| light | ~150-300 tokens | 60% reduction |
| full | ~300-500 tokens | 70% reduction |
| aggressive | ~500-1000 tokens | 50% reduction |

**Key insight:** Old approach dumped ~1500-3000 tokens. New approach injects ~300-500 token index, agent fetches only what's needed.

## Backwards Compatibility

- All existing hook_mode values work unchanged
- Output format is enhanced but structurally similar
- `memory-recall` skill works as before for fetching details
- No changes required to user configuration

## Notes

- Hook runs in background, injects context before first user message
- Keep index queries fast (<100ms each, <500ms total)
- Network databases may timeout - graceful degradation built in
- Token estimates are approximate (~150-400 tokens per full entry)
- Progressive disclosure reduces context bloat significantly

## Version History

### 1.3.0 (Current)
- **Progressive disclosure:** Index-first injection, on-demand details
- **Token estimates:** Show approximate cost per category
- **Graceful degradation:** Timeout handling for network databases
- **Critical auto-fetch:** Aggressive mode pre-loads importance >= 9 items

### 1.2.0
- Initial hook modes (off, remind, light, full, aggressive)
- Basic context injection
