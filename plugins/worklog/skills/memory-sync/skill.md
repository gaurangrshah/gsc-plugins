---
name: memory-sync
description: Reconcile worklog database with local knowledge base and documentation
---

# Memory Sync Skill

Synchronize worklog database entries with local documentation. Promotes important learnings to permanent docs and cleans up stale entries.

## When to Use

| Trigger | Action |
|---------|--------|
| Weekly maintenance | Full sync review |
| After major project | Sync project learnings |
| Before context loss | Ensure learnings captured |
| Monthly cleanup | Archive old entries |

## Workflow

### Step 1: Query Recent Entries

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

### Step 2: Identify Promotion Candidates

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

### Step 3: Check for Duplicates

Before adding to local knowledge base:

```bash
# Search local insights
grep -i "{keyword}" ~/.claude/knowledge/insights.md

# Check decisions folder
ls ~/.claude/knowledge/decisions/ | grep -i "{topic}"
```

If duplicate found:
- Bump score in insights.md instead of adding new entry
- Update existing decision doc if new information

### Step 4: Promote to Local Docs

**For insights.md:**

```markdown
**[Score: 1] | YYYY-MM-DD | {agent} | {topic}**
{insight_text}. Source: worklog knowledge_base #{id}
```

**For decisions/:**

Create `YYYY-MM-DD-{slug}.md` with ADR template:

```markdown
# {Decision Title}

**Date:** YYYY-MM-DD
**Status:** Accepted
**Source:** worklog knowledge_base #{id}

## Context
{from knowledge_base.content}

## Decision
{extracted decision}

## Consequences
{extracted consequences}
```

### Step 5: Update Memory Status

Promote valuable memories:

```sql
UPDATE memories
SET status = 'promoted',
    promoted_at = CURRENT_TIMESTAMP
WHERE id = {id};
```

Archive stale memories:

```sql
UPDATE memories
SET status = 'archived'
WHERE status = 'staging'
  AND last_accessed < datetime('now', '-30 days')
  AND importance < 5;
```

### Step 6: Mark Entries as Synced

Add sync tag to processed entries:

```sql
UPDATE knowledge_base
SET tags = tags || ',synced:{system_name}'
WHERE id = {id};
```

### Step 7: Cleanup Old Data

**Archive old entries (optional):**

```sql
-- Move old entries to archive (if you have archive tables)
-- Or just leave them - SQLite handles large tables fine

-- Delete test/junk entries
DELETE FROM entries
WHERE agent LIKE '_test%'
   OR title LIKE '%_test%';

-- Clean up orphaned memories
DELETE FROM memories
WHERE status = 'archived'
  AND last_accessed < datetime('now', '-90 days');
```

## Sync Report Template

After sync, generate report:

```markdown
## Worklog Sync Report - {date}

### Reviewed
- Knowledge entries: {count}
- Work entries: {count}
- Memories: {count}

### Promoted to Local Docs
- insights.md: {count} new entries
- decisions/: {count} new ADRs
- guides/: {count} new guides

### Memory Status Updates
- Promoted: {count}
- Archived: {count}

### Cleanup
- Deleted test entries: {count}
- Archived stale memories: {count}

### Pending Review
{list entries that need human decision}
```

## Promotion Decision Matrix

| Criteria | Action |
|----------|--------|
| Seen 3+ times | Promote to insights.md, score = occurrences |
| Architectural decision | Promote to decisions/ |
| Step-by-step procedure | Promote to guides/ |
| Single occurrence, high value | Promote to insights.md, score = 1 |
| Single occurrence, low value | Leave in worklog |
| Stale (>30 days, low importance) | Archive |

## Cross-System Sync

For shared databases, check for entries from other systems:

```sql
SELECT DISTINCT source_agent, system
FROM knowledge_base
WHERE created_at > datetime('now', '-7 days')
  AND system != '{this_system}';
```

Review entries from other systems for local relevance.

## Example Sync Session

```bash
# 1. Query recent knowledge
sqlite3 {db_path} "SELECT id, title, tags FROM knowledge_base
WHERE created_at > datetime('now', '-7 days');"

# Found: ID 47 - "Docker compose override pattern"
# Action: New pattern, add to insights.md with score 1

# 2. Query active memories
sqlite3 {db_path} "SELECT key, importance FROM memories
WHERE status = 'staging' ORDER BY importance DESC;"

# Found: ctx_jarvis_20251213_webgen high importance
# Action: Still active, leave as staging

# 3. Update insights.md
echo "**[Score: 1] | 2025-12-13 | jarvis | Docker Compose**
Use override files for environment-specific config. Source: worklog #47" >> ~/.claude/knowledge/insights.md

# 4. Mark as synced
sqlite3 {db_path} "UPDATE knowledge_base
SET tags = tags || ',synced:ubuntu-mini' WHERE id = 47;"
```
