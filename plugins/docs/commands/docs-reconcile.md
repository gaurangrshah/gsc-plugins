---
name: docs-reconcile
description: Reconcile a journal file into permanent documentation following decision tree routing
---

# /docs-reconcile

Reconcile a journal file into permanent documentation.

## Usage

```
/docs-reconcile <journal-path>
```

## What It Does

1. **Reads and analyzes the journal**
   - Parses entry types (Discovery, Decision, Blocker, Checkpoint, Completed)
   - Identifies what changed (code, config, architecture, services)
   - Extracts key decisions and rationale
   - Notes lessons learned or gotchas

2. **Determines documentation actions** using decision tree:
   ```
   System config change     → Update $MAIN_GUIDE inline
   Service deployment       → Update services/ or $MAIN_GUIDE
   Security change          → Update security/ AND $MAIN_GUIDE
   Architecture decision    → $KNOWLEDGE_BASE/decisions/
   Lesson learned           → Main guide "Key Lessons"
   Cross-project pattern    → $KNOWLEDGE_BASE/guides/
   Bug fix (non-trivial)    → Troubleshooting section
   Code change only         → Project CHANGELOG
   Trivial change           → No documentation needed
   ```

3. **Executes documentation updates**
   - Makes inline updates (never separate incident files)
   - Updates "Current State" tables if applicable
   - Adds to "Change History" sections
   - Validates frontmatter on new files

4. **Stores to worklog.db** (if configured)
   - Reusable learnings → `knowledge_base` table
   - Work completion → `entries` table

5. **Reports reconciliation results**
   - What was updated
   - What was skipped (and why)
   - Confirms journal can be deleted

## Journal Format Expected

```markdown
# Journal: Task Name

## Task Started - HH:MM
**Context:** What you're working on

## Discovery - HH:MM
**Context:** What you found
**Content:** Details

## Decision - HH:MM
**Context:** What decision was needed
**Content:** What was decided and why
**Next:** What to do next

## Blocker - HH:MM
**Context:** What's blocking
**Content:** Details
**Resolution:** How resolved (if resolved)

## Checkpoint - HH:MM
**Context:** Progress update
**Content:** What's done so far

## Completed - HH:MM
**Context:** Task completion
**Content:** Summary of what was accomplished
```

## Examples

**Basic reconciliation:**
```
/docs-reconcile /tmp/journal-fix-auth-2025-01-15.md
```

## Output

```
📝 Journal Reconciliation Report

Journal: /tmp/journal-fix-auth-2025-01-15.md
Entries found: 6 (2 decisions, 1 discovery, 1 completed)

✅ Documentation Updated:
- $MAIN_GUIDE: Added firewall rule to Current State
- $MAIN_GUIDE: Added entry to Change History
- $KNOWLEDGE_BASE/decisions/jwt-auth-strategy.md: Created

⏭️  Skipped:
- 2 checkpoint entries (context only)
- 1 trivial discovery (no lasting value)

📦 Stored to worklog.db:
- knowledge_base: 1 new entry (JWT auth decision)
- entries: 1 work log entry

✅ Journal can be safely deleted
```

## Post-Reconciliation

After successful reconciliation:
1. Review the documentation updates
2. Commit changes to git
3. Delete the journal file
4. Run `/docs-validate --quick` to verify

## Integration

- Works with docs-manager skill for documentation updates
- Logs to worklog.db if configured
- Respects frontmatter standards
- Never creates separate incident files
