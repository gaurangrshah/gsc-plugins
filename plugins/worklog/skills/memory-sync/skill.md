---
name: memory-sync
description: Reconcile worklog database with documentation - promotes learnings to docs with proper frontmatter and validates after sync
---

# Memory Sync Skill

Synchronize worklog database entries with local documentation. Promotes important learnings to permanent docs with proper frontmatter, and validates the results.

## Prerequisites

- Worklog plugin configured (`$WORKLOG_DB` set)
- Optional: Docs plugin for enhanced integration

## Configuration

```bash
# Required
WORKLOG_DB="${WORKLOG_DB:-}"

# Docs integration (auto-detected if docs plugin installed)
KNOWLEDGE_BASE="${KNOWLEDGE_BASE:-~/.claude/knowledge}"
DOCS_ROOT="${DOCS_ROOT:-}"  # If set, enables full docs integration

# Optional
DOCS_VALIDATOR="${DOCS_VALIDATOR:-}"  # Path to docs-validator if available
```

### Integration Modes

| Mode | When | Behavior |
|------|------|----------|
| **Standalone** | No docs plugin | Promotes to `$KNOWLEDGE_BASE` with basic formatting |
| **Docs-aware** | `$DOCS_ROOT` set | Full frontmatter, validates after sync, respects docs structure |

---

## When to Use

| Trigger | Action |
|---------|--------|
| Weekly maintenance | Full sync review |
| After major project | Sync project learnings |
| Before context loss | Ensure learnings captured |
| Monthly cleanup | Archive old entries |

---

## Workflow

### Step 1: Detect Docs Integration

```bash
# Check if docs plugin is available
if [ -n "$DOCS_ROOT" ] && [ -d "$DOCS_ROOT" ]; then
  DOCS_INTEGRATION=true
  echo "Docs integration enabled: $DOCS_ROOT"
else
  DOCS_INTEGRATION=false
  echo "Standalone mode: promoting to $KNOWLEDGE_BASE"
fi
```

### Step 2: Query Recent Entries

**SQLite:**
```sql
-- Knowledge added in last 7 days
SELECT id, category, title, content, tags, created_at
FROM knowledge_base
WHERE created_at > datetime('now', '-7 days')
ORDER BY created_at DESC;

-- Recent work entries
SELECT id, title, outcome, tags, timestamp
FROM entries
WHERE timestamp > datetime('now', '-7 days')
ORDER BY timestamp DESC;

-- Active memories
SELECT id, key, content, importance, status
FROM memories
WHERE status = 'staging'
ORDER BY importance DESC;
```

**PostgreSQL:**
```sql
-- Knowledge added in last 7 days (includes source_url if available)
SELECT id, category, title, content, tags, created_at, source_url
FROM knowledge_base
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Recent work entries
SELECT id, title, outcome, tags, timestamp
FROM entries
WHERE timestamp > NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;

-- Active memories
SELECT id, key, content, importance, status
FROM memories
WHERE status = 'staging'
ORDER BY importance DESC;
```

### Step 3: Identify Promotion Candidates

Review entries for local documentation promotion:

**Promote to insights.md:**
- Patterns seen multiple times
- Gotchas and anti-patterns
- Cross-system learnings

**Promote to decisions/:**
- Architectural decisions
- Technology choices
- Process decisions

**Promote to guides/:**
- Step-by-step procedures
- Configuration guides
- Troubleshooting flows

### Step 4: Check for Duplicates

Before adding to local knowledge base:

```bash
# Search local insights
grep -i "{keyword}" "$KNOWLEDGE_BASE/insights.md"

# Check decisions folder
ls "$KNOWLEDGE_BASE/decisions/" | grep -i "{topic}"

# If docs integration, also check DOCS_ROOT
if [ "$DOCS_INTEGRATION" = true ]; then
  grep -r -i "{keyword}" "$DOCS_ROOT/" --include="*.md"
fi
```

If duplicate found:
- Bump score in insights.md instead of adding new entry
- Update existing decision doc if new information

### Step 5: Promote to Local Docs

#### For insights.md (No Frontmatter Needed)

```markdown
**[Score: 1] | YYYY-MM-DD | {agent} | {topic}**
{insight_text}. Source: worklog knowledge_base #{id}
```

#### For decisions/ (With Frontmatter)

Create `YYYY-MM-DD-{slug}.md`:

```markdown
---
title: "{Decision Title}"
type: decision
created: YYYY-MM-DD
status: active
tags: [worklog-sync, {category}]
source: worklog-kb-{id}
---

# {Decision Title}

## Context

{from knowledge_base.content - the problem or situation}

## Decision

{extracted decision - what was decided}

## Consequences

{extracted consequences - impact of the decision}

## References

- Source: worklog knowledge_base #{id}
- Synced: YYYY-MM-DD
```

#### For guides/ (With Frontmatter)

Create `{slug}.md`:

```markdown
---
title: "{Guide Title}"
type: guide
created: YYYY-MM-DD
status: active
tags: [worklog-sync, {category}]
source: worklog-kb-{id}
---

# {Guide Title}

{from knowledge_base.content - formatted as step-by-step guide}

## Prerequisites

{extracted prerequisites if any}

## Steps

{extracted steps}

## Troubleshooting

{extracted gotchas or common issues}

## References

- Source: worklog knowledge_base #{id}
- Synced: YYYY-MM-DD
```

### Step 6: Update Memory Status

Promote valuable memories:

```sql
UPDATE memories
SET status = 'promoted',
    promoted_at = CURRENT_TIMESTAMP
WHERE id = {id};
```

Archive stale memories:

**SQLite:**
```sql
UPDATE memories
SET status = 'archived'
WHERE status = 'staging'
  AND last_accessed < datetime('now', '-30 days')
  AND importance < 5;
```

**PostgreSQL:**
```sql
UPDATE memories
SET status = 'archived'
WHERE status = 'staging'
  AND last_accessed < NOW() - INTERVAL '30 days'
  AND importance < 5;
```

### Step 7: Mark Entries as Synced

Add sync tag to processed entries:

```sql
UPDATE knowledge_base
SET tags = tags || ',synced:{system_name}'
WHERE id = {id};
```

### Step 8: Validate Promoted Files (Docs Integration)

**If docs plugin available**, run validation on new files:

```bash
if [ "$DOCS_INTEGRATION" = true ]; then
  echo "Running docs validation on promoted files..."

  # Quick validation on new files
  for file in $PROMOTED_FILES; do
    # Check frontmatter exists
    if ! head -1 "$file" | grep -q "^---$"; then
      echo "WARNING: $file missing frontmatter"
    fi

    # Check required fields
    if ! grep -q "^title:" "$file"; then
      echo "WARNING: $file missing title field"
    fi
    if ! grep -q "^type:" "$file"; then
      echo "WARNING: $file missing type field"
    fi
    if ! grep -q "^created:" "$file"; then
      echo "WARNING: $file missing created field"
    fi
  done

  echo "Validation complete"
fi
```

### Step 9: Cleanup Old Data

**Archive old entries (optional):**

**SQLite:**
```sql
-- Delete test/junk entries
DELETE FROM entries
WHERE agent LIKE '_test%'
   OR title LIKE '%_test%';

-- Clean up orphaned memories
DELETE FROM memories
WHERE status = 'archived'
  AND last_accessed < datetime('now', '-90 days');
```

**PostgreSQL:**
```sql
-- Delete test/junk entries
DELETE FROM entries
WHERE agent LIKE '_test%'
   OR title LIKE '%_test%';

-- Clean up orphaned memories
DELETE FROM memories
WHERE status = 'archived'
  AND last_accessed < NOW() - INTERVAL '90 days';
```

---

## Frontmatter Reference

All promoted files use docs-compatible frontmatter:

### Required Fields

| Field | Format | Description |
|-------|--------|-------------|
| `title` | String | Brief descriptive title |
| `type` | Enum | `decision`, `learning`, `guide`, `reference` |
| `created` | YYYY-MM-DD | Date created/synced |

### Optional Fields

| Field | Format | Description |
|-------|--------|-------------|
| `status` | Enum | `active`, `deprecated`, `superseded` |
| `tags` | Array | `[tag1, tag2]` |
| `source` | String | `worklog-kb-{id}` for traceability |
| `updated` | YYYY-MM-DD | Last update date |

### Type Mapping

| Worklog Category | Docs Type |
|------------------|-----------|
| `decisions`, `architecture` | `decision` |
| `learnings`, `patterns` | `learning` |
| `guides`, `procedures` | `guide` |
| `protocols`, `references` | `reference` |

---

## Sync Report Template

After sync, generate report:

```markdown
## Worklog Sync Report - {date}

### Configuration
- Mode: {Standalone | Docs-integrated}
- KNOWLEDGE_BASE: {path}
- DOCS_ROOT: {path or "not set"}

### Reviewed
- Knowledge entries: {count}
- Work entries: {count}
- Memories: {count}

### Promoted to Local Docs
- insights.md: {count} new entries
- decisions/: {count} new ADRs (with frontmatter)
- guides/: {count} new guides (with frontmatter)

### Validation Results
- Files validated: {count}
- Frontmatter issues: {count}
- All files compliant: {yes/no}

### Memory Status Updates
- Promoted: {count}
- Archived: {count}

### Cleanup
- Deleted test entries: {count}
- Archived stale memories: {count}

### Pending Review
{list entries that need human decision}
```

---

## Promotion Decision Matrix

| Criteria | Action | Frontmatter |
|----------|--------|-------------|
| Seen 3+ times | Promote to insights.md | No (inline format) |
| Architectural decision | Promote to decisions/ | Yes (type: decision) |
| Step-by-step procedure | Promote to guides/ | Yes (type: guide) |
| Single occurrence, high value | Promote to insights.md | No (inline format) |
| Single occurrence, low value | Leave in worklog | N/A |
| Stale (>30 days, low importance) | Archive | N/A |

---

## Cross-System Sync

For shared databases, check for entries from other systems:

**SQLite:**
```sql
SELECT DISTINCT source_agent, system
FROM knowledge_base
WHERE created_at > datetime('now', '-7 days')
  AND system != '{this_system}';
```

**PostgreSQL:**
```sql
SELECT DISTINCT source_agent, system
FROM knowledge_base
WHERE created_at > NOW() - INTERVAL '7 days'
  AND system != '{this_system}';
```

Review entries from other systems for local relevance.

---

## Example Sync Session

```bash
# 1. Check docs integration
if [ -n "$DOCS_ROOT" ]; then
  echo "Docs integration: enabled"
  KNOWLEDGE_BASE="${KNOWLEDGE_BASE:-$DOCS_ROOT/../.claude/knowledge}"
fi

# 2. Query recent knowledge (detect backend)
if [ -n "$DATABASE_URL" ] || [ -n "$PGHOST" ]; then
  # PostgreSQL
  psql -t -c "SELECT id, title, category, tags FROM knowledge_base
    WHERE created_at > NOW() - INTERVAL '7 days';"
else
  # SQLite
  sqlite3 "$WORKLOG_DB" "SELECT id, title, category, tags FROM knowledge_base
    WHERE created_at > datetime('now', '-7 days');"
fi

# Found: ID 47 - "Docker compose override pattern" (category: patterns)
# Action: New pattern, add to insights.md with score 1

# Found: ID 48 - "JWT auth architecture decision" (category: decisions)
# Action: Create decisions/2025-12-14-jwt-auth-strategy.md with frontmatter

# 3. Update insights.md
echo "**[Score: 1] | 2025-12-14 | claude | Docker Compose**
Use override files for environment-specific config. Source: worklog #47" >> "$KNOWLEDGE_BASE/insights.md"

# 4. Create decision doc with frontmatter
cat > "$KNOWLEDGE_BASE/decisions/2025-12-14-jwt-auth-strategy.md" << 'EOF'
---
title: "JWT Authentication Strategy"
type: decision
created: 2025-12-14
status: active
tags: [worklog-sync, auth, security]
source: worklog-kb-48
---

# JWT Authentication Strategy

## Context

Need to implement authentication for the API...

## Decision

Use JWT with refresh tokens...

## Consequences

- Stateless authentication
- Need secure token storage on client
- Refresh token rotation required

## References

- Source: worklog knowledge_base #48
- Synced: 2025-12-14
EOF

# 5. Validate new file
head -1 "$KNOWLEDGE_BASE/decisions/2025-12-14-jwt-auth-strategy.md" | grep -q "^---$" && echo "✓ Frontmatter valid"

# 6. Mark as synced (use your system name)
sqlite3 "$WORKLOG_DB" "UPDATE knowledge_base
SET tags = tags || ',synced:$(hostname)' WHERE id IN (47, 48);"

# 7. Generate report
echo "Sync complete: 1 insight, 1 decision promoted"
```

---

## Integration with Docs Plugin

When docs plugin is installed:

1. **Auto-detection**: memory-sync detects `$DOCS_ROOT` and enables full integration
2. **Frontmatter compliance**: All promoted files follow docs frontmatter schema
3. **Post-sync validation**: Validates promoted files match docs standards
4. **Consistent paths**: Uses `$KNOWLEDGE_BASE` which docs plugin also uses

**Complementary workflow:**
- **docs-manager**: Creates docs, stores learnings TO worklog
- **memory-sync**: Promotes worklog entries BACK to docs

This creates a bidirectional flow where knowledge moves between worklog and documentation.

---

**Skill Version:** 2.0.0
**Philosophy:** Promote valuable learnings. Maintain frontmatter compliance. Validate after sync.
