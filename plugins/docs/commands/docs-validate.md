---
name: docs-validate
description: Run documentation validation checks for frontmatter, links, and structure compliance
---

# /docs-validate

Run documentation validation checks.

## Usage

```
/docs-validate [options]
```

## Options

- `--quick` - Fast validation (frontmatter + obvious issues only)
- `--path <dir>` - Validate specific directory (default: `$DOCS_ROOT`)
- `--fix` - Attempt to auto-fix simple issues
- `--report` - Generate detailed report to `/tmp/docs-validation-YYYY-MM-DD.md`

## What It Checks

### Quick Mode (`--quick`)
- Frontmatter exists on all .md files
- Required fields present (title, type, created)
- No obvious broken links
- ~1-2 minutes

### Full Mode (default)
- All quick mode checks
- Internal link validation
- README completeness
- CHANGELOG compliance
- Structure compliance
- ~5-10 minutes

## Validation Categories

| Category | Severity | Example |
|----------|----------|---------|
| Missing frontmatter | Critical | File has no `---` block |
| Broken link | Critical | Link to non-existent file |
| Missing required field | Warning | No `created` date |
| Orphaned file | Warning | Not referenced in README |
| Missing README | Warning | Subdirectory without README.md |
| Stale content | Info | Not updated in 90+ days |

## Examples

**Quick validation before commit:**
```
/docs-validate --quick
```

**Full validation with report:**
```
/docs-validate --report
```

**Validate specific directory:**
```
/docs-validate --path ~/docs/security
```

**Auto-fix simple issues:**
```
/docs-validate --fix
```

## Output

**Console output:**
```
📋 Documentation Validation Report

Checked: 42 files
Issues: 3 critical, 5 warnings, 2 info

❌ Critical Issues:
- security/new-policy.md: Missing frontmatter
- guides/README.md: Broken link to old-guide.md

⚠️  Warnings:
- 5 files not referenced in READMEs

ℹ️  Info:
- Consider adding tags to 2 files

Full report: /tmp/docs-validation-2025-01-15.md
```

## Auto-Fix Capabilities

When `--fix` is used:

| Issue | Auto-Fix Action |
|-------|-----------------|
| Missing frontmatter | Add minimal frontmatter template |
| Missing created date | Add today's date |
| Malformed date | Convert to YYYY-MM-DD |

**Note:** Auto-fix creates backups before modifying files.

## Integration with Worklog

If worklog plugin is configured, validation results are logged:

```sql
INSERT INTO entries (agent, task_type, title, details, outcome, tags)
VALUES ('hostname', 'validation', 'Docs validation', 'details', 'outcome', 'docs,validation');
```

## Recommended Schedule

| Frequency | Mode | When |
|-----------|------|------|
| Per commit | `--quick` | Before git commit |
| Weekly | Full | During review |
| Monthly | Full + `--report` | First of month |
