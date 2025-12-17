---
event: PostToolUse
priority: 50
match_tools: ["Write", "Edit", "MultiEdit"]
---

# Post Tool Use Hook - Selective Observation Capture

Automatically capture significant tool outcomes during a session. Inspired by claude-mem's observation system but with selective filtering to avoid noise.

## Design Philosophy

**Claude-mem captures everything.** We capture selectively.

| Approach | Pros | Cons |
|----------|------|------|
| Capture all | Complete history | Token bloat, noise |
| Capture none | No overhead | Lost learnings |
| **Capture significant** | Signal preserved | Requires filtering |

This hook captures **significant Write/Edit outcomes** - the moments that matter.

## Configuration

This hook is **OFF by default**. Enable via `~/.claude/worklog.local.md`:

```yaml
---
profile: full
hook_mode: aggressive
db_path: ~/.claude/worklog/worklog.db
system_name: my-system
# PostToolUse capture settings
capture_observations: true          # Enable this hook (default: false)
capture_filter: significant         # all | significant | decisions-only
capture_files: ["*.md", "*.ts", "*.py", "*.json"]  # File patterns to capture
capture_exclude: ["node_modules/*", "*.lock", ".git/*"]  # Exclude patterns
---
```

### Capture Modes

| Mode | What Gets Captured | Recommended For |
|------|-------------------|-----------------|
| `off` (default) | Nothing | Most users |
| `significant` | Major file changes, configs, decisions | Power users |
| `decisions-only` | Only explicit decision markers | Minimal overhead |
| `all` | Every Write/Edit | Debug/audit only |

## What Makes an Observation "Significant"

### Capture If:

| Signal | Example | Why Significant |
|--------|---------|-----------------|
| Config file modified | `.env`, `config.json`, `docker-compose.yml` | Deployment-affecting |
| Schema/migration | `schema.sql`, `*.migration.ts` | Data structure change |
| Core logic file | `auth.ts`, `api/*.ts` | Business logic |
| Documentation | `README.md`, `CLAUDE.md` | Knowledge capture |
| Test file with fix | `*.test.ts` after bug discussion | Bug resolution |
| Multiple related edits | 3+ files in same directory | Feature implementation |

### Skip If:

| Signal | Example | Why Skip |
|--------|---------|----------|
| Generated file | `package-lock.json`, `*.min.js` | No learning value |
| Trivial change | Typo fix, whitespace | Noise |
| Temporary file | `/tmp/*`, `*.log` | Ephemeral |
| Build artifact | `dist/*`, `build/*` | Derived |
| Single small edit | One-line comment | Too granular |

## Hook Execution

### Step 1: Check if enabled

```bash
CAPTURE=$(grep -A1 "^capture_observations:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')

if [ "$CAPTURE" != "true" ]; then
  # Hook disabled, exit silently
  exit 0
fi
```

### Step 2: Check tool and file

```bash
TOOL_NAME="{from hook context}"
FILE_PATH="{from hook context}"
CHANGE_SUMMARY="{from hook context}"

# Only process Write, Edit, MultiEdit
if [[ ! "$TOOL_NAME" =~ ^(Write|Edit|MultiEdit)$ ]]; then
  exit 0
fi

# Check exclude patterns
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == $pattern ]]; then
    exit 0
  fi
done

# Check include patterns (if specified)
if [ -n "$CAPTURE_FILES" ]; then
  MATCH=false
  for pattern in "${CAPTURE_FILES[@]}"; do
    if [[ "$FILE_PATH" == $pattern ]]; then
      MATCH=true
      break
    fi
  done
  if [ "$MATCH" = false ]; then
    exit 0
  fi
fi
```

### Step 3: Assess significance

```bash
FILTER=$(grep -A1 "^capture_filter:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
FILTER="${FILTER:-significant}"

case "$FILTER" in
  all)
    # Capture everything that passed file filters
    CAPTURE=true
    ;;
  significant)
    # Apply significance heuristics
    CAPTURE=false

    # Config files are always significant
    if [[ "$FILE_PATH" =~ \.(env|json|yaml|yml|toml|ini)$ ]]; then
      CAPTURE=true
    fi

    # Schema/migration files
    if [[ "$FILE_PATH" =~ (schema|migration|seed) ]]; then
      CAPTURE=true
    fi

    # Core code directories
    if [[ "$FILE_PATH" =~ (src/|lib/|app/) ]]; then
      # Only if change is substantial (>10 lines or >3 hunks)
      if [ "$LINES_CHANGED" -gt 10 ] || [ "$HUNKS" -gt 3 ]; then
        CAPTURE=true
      fi
    fi

    # Documentation always captured
    if [[ "$FILE_PATH" =~ \.(md|rst|txt)$ ]]; then
      CAPTURE=true
    fi
    ;;
  decisions-only)
    # Only capture if change contains decision markers
    if [[ "$CHANGE_SUMMARY" =~ (DECISION|DECIDED|CHOSE|RATIONALE) ]]; then
      CAPTURE=true
    fi
    ;;
esac

if [ "$CAPTURE" = false ]; then
  exit 0
fi
```

### Step 4: Generate observation

```yaml
observation:
  timestamp: "{ISO-8601}"
  tool: "{Write|Edit|MultiEdit}"
  file: "{file_path}"
  type: "{config|schema|code|docs|test}"
  summary: "One-line description of change"
  context: "Why this change was made (from conversation)"
  significance: "low|medium|high"
  tags: ["auto-generated", "tags"]
```

### Step 5: Store to memories table

```bash
# Generate unique key
OBS_KEY="obs_${SYSTEM_NAME}_$(date +%Y%m%d%H%M%S)_$(basename $FILE_PATH | tr '.' '_')"

# Determine importance based on file type
case "$TYPE" in
  config|schema) IMPORTANCE=7 ;;
  code) IMPORTANCE=6 ;;
  docs) IMPORTANCE=5 ;;
  test) IMPORTANCE=5 ;;
  *) IMPORTANCE=4 ;;
esac

sqlite3 "$DB_PATH" "INSERT INTO memories
(key, content, summary, memory_type, importance, source_agent, tags, status) VALUES
('$OBS_KEY',
'{\"tool\": \"$TOOL_NAME\", \"file\": \"$FILE_PATH\", \"type\": \"$TYPE\", \"context\": \"$CONTEXT\"}',
'$SUMMARY',
'observation', $IMPORTANCE, '$SYSTEM_NAME',
'observation,auto:post-tool,file:$(basename $FILE_PATH),type:$TYPE', 'staging');" 2>/dev/null
```

### Step 6: Silent confirmation (no output to user)

This hook runs silently. Observations are stored but don't interrupt the workflow.

To review captured observations:
```sql
SELECT key, summary, created_at FROM memories
WHERE memory_type = 'observation'
ORDER BY created_at DESC LIMIT 10;
```

## Observation Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVATION LIFECYCLE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PostToolUse Hook                                                │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────────────┐                                           │
│  │ Filter: Enabled? │──No──► Exit silently                      │
│  └────────┬─────────┘                                           │
│           │ Yes                                                  │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │ Filter: File OK? │──No──► Exit silently                      │
│  └────────┬─────────┘                                           │
│           │ Yes                                                  │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │ Significant?     │──No──► Exit silently                      │
│  └────────┬─────────┘                                           │
│           │ Yes                                                  │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │ Store to         │                                           │
│  │ memories table   │                                           │
│  │ (status=staging) │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  SessionEnd Hook                                                 │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────────────┐                                           │
│  │ Review staged    │                                           │
│  │ observations     │                                           │
│  │ Promote or       │                                           │
│  │ archive          │                                           │
│  └──────────────────┘                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Integration with Other Hooks

### SessionStart

```bash
# Show count of recent observations
OBS_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM memories
WHERE memory_type = 'observation'
AND created_at > datetime('now', '-1 day');" 2>/dev/null)

# Include in index if >0
```

### SessionEnd

```bash
# Review staged observations
STAGED=$(sqlite3 "$DB_PATH" "SELECT key, summary FROM memories
WHERE memory_type = 'observation' AND status = 'staging';" 2>/dev/null)

# Option to promote significant ones to knowledge_base
# Option to archive trivial ones
```

## Performance Considerations

| Concern | Mitigation |
|---------|------------|
| Hook overhead | Only triggers on Write/Edit/MultiEdit |
| Database writes | Single INSERT, <10ms |
| Filter complexity | Exit early if disabled |
| Storage bloat | Staging → promote/archive cycle |

**Target:** <50ms per hook execution, invisible to user.

## Example Observations

### Config Change
```json
{
  "key": "obs_ubuntu-mini_20241216143022_docker_compose_yml",
  "summary": "Added Redis service to docker-compose.yml",
  "memory_type": "observation",
  "importance": 7,
  "tags": "observation,auto:post-tool,file:docker-compose.yml,type:config"
}
```

### Code Change
```json
{
  "key": "obs_ubuntu-mini_20241216143156_auth_ts",
  "summary": "Implemented JWT refresh token rotation",
  "memory_type": "observation",
  "importance": 6,
  "tags": "observation,auto:post-tool,file:auth.ts,type:code"
}
```

### Documentation
```json
{
  "key": "obs_ubuntu-mini_20241216143312_README_md",
  "summary": "Added deployment instructions for Coolify",
  "memory_type": "observation",
  "importance": 5,
  "tags": "observation,auto:post-tool,file:README.md,type:docs"
}
```

## Troubleshooting

### Hook not capturing

1. Check `capture_observations: true` in config
2. Verify file matches include patterns
3. Check file doesn't match exclude patterns
4. Verify database is writable

### Too many observations

1. Switch to `capture_filter: significant` or `decisions-only`
2. Narrow `capture_files` patterns
3. Expand `capture_exclude` patterns

### Review captured observations

```sql
-- Recent observations
SELECT key, summary, importance, created_at
FROM memories
WHERE memory_type = 'observation'
ORDER BY created_at DESC LIMIT 20;

-- Observations by file
SELECT key, summary FROM memories
WHERE memory_type = 'observation'
AND tags LIKE '%file:auth.ts%';

-- High importance only
SELECT key, summary FROM memories
WHERE memory_type = 'observation'
AND importance >= 7;
```

## Version History

### 1.0.0 (Current)
- Initial PostToolUse hook
- Selective capture with significance filtering
- Three capture modes: all, significant, decisions-only
- File pattern include/exclude
- Silent operation with staging status
- Integration with SessionStart/SessionEnd hooks
