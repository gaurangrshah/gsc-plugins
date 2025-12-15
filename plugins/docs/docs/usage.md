# Docs Plugin Usage Guide

## Quick Start

1. **Set environment variables:**
   ```bash
   export DOCS_ROOT="~/docs"
   export MAIN_GUIDE="$DOCS_ROOT/guide.md"
   export KNOWLEDGE_BASE="~/.claude/knowledge"
   ```

2. **Initialize documentation structure:**
   ```bash
   mkdir -p $DOCS_ROOT/{security,guides,services,baselines}
   cp templates/guide-template.md $MAIN_GUIDE
   cp templates/frontmatter-schema.md $DOCS_ROOT/FRONTMATTER-SCHEMA.md
   ```

3. **Start documenting:**
   - System changes → Update `$MAIN_GUIDE` inline
   - Decisions → `$KNOWLEDGE_BASE/decisions/`
   - Learnings → `$KNOWLEDGE_BASE/learnings/`

## Workflow

### During Tasks

1. Use `/tmp/` for working notes
2. Track progress as you go
3. Keep working files ephemeral

### After Tasks

1. Review `/tmp/` working files
2. Invoke `docs-manager` for journal reconciliation
3. Promote only valuable content
4. Delete journal after confirmation

### Monthly Maintenance

1. Run `docs-validator` for quality check
2. Fix critical issues (broken links, missing frontmatter)
3. Address warnings
4. Review and update main guide

## Commands

```bash
# Validate all documentation
/skill docs-validator

# Quick validation before commit
/skill docs-validator --quick

# Reconcile journal
/skill docs-manager reconcile /tmp/journal-task-2025-01-15.md
```

## Integration with Worklog

When worklog plugin is installed, docs-manager can:
- Store findings in memories table during tasks
- Promote high-value memories to knowledge_base
- Query recent context for reconciliation

Set `WORKLOG_DB` environment variable to enable:
```bash
export WORKLOG_DB="/path/to/worklog.db"
```
