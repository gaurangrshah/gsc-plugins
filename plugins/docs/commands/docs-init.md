---
name: docs-init
description: Initialize documentation structure for a project with frontmatter standards
---

# /docs-init

Initialize documentation structure for a project.

## Usage

```
/docs-init [options]
```

## Options

- `--path <dir>` - Documentation root (default: `~/docs` or `$DOCS_ROOT`)
- `--guide <name>` - Main guide filename (default: `guide.md`)
- `--with-worklog` - Configure worklog.db integration

## What It Does

1. **Creates directory structure:**
   ```
   $DOCS_ROOT/
   ├── README.md
   ├── guide.md (or custom name)
   ├── FRONTMATTER-SCHEMA.md
   ├── security/
   │   └── README.md
   ├── guides/
   │   └── README.md
   ├── services/
   │   └── README.md
   └── baselines/
   ```

2. **Creates configuration file:**
   ```
   ~/.claude/docs.local.md
   ```
   Contains environment variables for this project.

3. **Initializes main guide** with template sections:
   - Current State table
   - Quick Reference
   - Change History

## Configuration File

After initialization, `~/.claude/docs.local.md` contains:

```markdown
# Docs Plugin Configuration

## Environment
- DOCS_ROOT: /path/to/docs
- MAIN_GUIDE: /path/to/docs/guide.md
- KNOWLEDGE_BASE: ~/.claude/knowledge

## Worklog Integration
- WORKLOG_DB: (path if --with-worklog used)
```

## Examples

**Basic initialization:**
```
/docs-init
```

**Custom path and guide name:**
```
/docs-init --path ~/project/docs --guide project-guide.md
```

**With worklog integration:**
```
/docs-init --with-worklog
```

## Post-Initialization

After running `/docs-init`:

1. Review and customize `$MAIN_GUIDE`
2. Update `~/.claude/docs.local.md` if needed
3. Start documenting with inline updates to main guide
4. Run `/docs-validate` to verify structure

## Integration

- Works standalone or with worklog plugin
- If worklog is installed, can auto-detect database path
- Configuration persists across sessions via `docs.local.md`
