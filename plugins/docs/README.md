# Docs Plugin

**Docs** is a Claude Code plugin for documentation management and quality assurance. It enforces a single source of truth philosophy with inline updates, journal reconciliation, and proactive validation.

**Version:** 1.0.0

## Installation

### Option 1: Marketplace (Recommended)

```bash
# Add the marketplace (if not already added)
claude plugin marketplace add https://github.com/gaurangrshah/gsc-plugins.git

# Install the plugin
claude plugin install docs@gsc-plugins
```

### Option 2: Manual Installation

```bash
# Clone the repo
git clone https://github.com/gaurangrshah/gsc-plugins.git

# Copy to local-plugins
cp -r gsc-plugins/plugins/docs ~/.claude/plugins/local-plugins/

# Restart Claude Code to activate
```

## Core Capabilities

The plugin provides two complementary skills: **docs-manager** for creating and maintaining documentation, and **docs-validator** for quality assurance. Together they ensure documentation stays current, consistent, and queryable.

## Key Features

**Single Source of Truth**: All system documentation flows through one main guide file. Updates happen inline—no separate incident files, no documentation sprawl.

**Journal Reconciliation**: After completing tasks, reconcile journal notes into permanent documentation. Decisions, learnings, and config changes are extracted and routed to appropriate locations.

**Proactive Validation**: Check frontmatter compliance, internal links, README completeness, and changelog entries. Catch issues before they become problems.

**Worklog Integration**: When the worklog plugin is installed, docs automatically stores reusable learnings and logs documentation work to the shared database.

**Platform Agnostic**: Configure paths via environment variables. Works with any project structure on any system.

## Configuration

Set environment variables or create `~/.claude/docs.local.md`:

```bash
export DOCS_ROOT="~/docs"
export MAIN_GUIDE="$DOCS_ROOT/guide.md"
export KNOWLEDGE_BASE="~/.claude/knowledge"
export WORKLOG_DB=""  # Optional: path to worklog.db
```

## Commands

| Command | Purpose |
|---------|---------|
| `/docs-init` | Initialize documentation structure |
| `/docs-validate` | Run validation checks |
| `/docs-reconcile` | Reconcile journal into docs |

## Skills

| Skill | Purpose |
|-------|---------|
| `docs-manager` | Create, update, and reconcile documentation |
| `docs-validator` | Validate quality and compliance |

## Quick Start

1. Initialize documentation structure:
   ```
   /docs-init
   ```

2. Configure environment (auto-created by init):
   ```
   ~/.claude/docs.local.md
   ```

3. Start documenting with inline updates to main guide

4. After tasks, reconcile journals:
   ```
   /docs-reconcile /tmp/journal-task-2025-01-15.md
   ```

5. Run validation monthly:
   ```
   /docs-validate
   ```

## Documentation Philosophy

**DO:**
- Update main guide inline for system changes
- Use /tmp for working notes during tasks
- Add frontmatter to all markdown files
- Keep documentation concise and current

**DON'T:**
- Create separate files for each incident/change
- Leave documentation for "later"
- Add hypothetical configurations
- Over-document obvious things

## Standalone & Integration

Docs operates independently without dependencies. When the **worklog** plugin is installed:
- Reusable learnings are stored to `knowledge_base` table
- Documentation work is logged to `entries` table
- Working memory uses `memories` table during tasks

## Frontmatter Standard

All documentation requires YAML frontmatter:

```yaml
---
title: "Brief descriptive title"
type: decision|learning|guide|reference|changelog|environment
created: YYYY-MM-DD
---
```

## Validation Checks

`/docs-validate` performs:
- Frontmatter compliance (required fields, valid values)
- Internal link validation (no broken references)
- README completeness (all files referenced)
- CHANGELOG compliance (proper format)
- Structure compliance (files in correct directories)

## File Structure

```
$DOCS_ROOT/
├── README.md           # Navigation hub
├── guide.md            # THE GUIDE (single source of truth)
├── FRONTMATTER-SCHEMA.md
├── security/
├── guides/
├── services/
└── baselines/
```

## Journal Reconciliation Flow

```
Journal Entry → Decision Tree → Documentation Action
─────────────────────────────────────────────────────
System config     → Main guide inline
Architecture      → $KNOWLEDGE_BASE/decisions/
Lesson learned    → Main guide "Key Lessons"
Cross-project     → $KNOWLEDGE_BASE/guides/
Code change       → Project CHANGELOG
Trivial           → No action needed
```

---

**License:** MIT
