---
name: docs-validator
description: Proactive documentation quality assurance - validate frontmatter, links, READMEs, and changelogs
---

# Documentation Validator Skill

**Purpose:** Proactive documentation quality assurance and compliance checking

**Philosophy:** Catch documentation issues early, maintain quality standards, ensure queryability.

---

## Prerequisites

- Environment variables configured (see Configuration below)
- Optional: Worklog plugin for logging validation results
- Optional: Query script for queryable documentation

## Configuration

```bash
# Required
DOCS_ROOT="${DOCS_ROOT:-~/docs}"
KNOWLEDGE_BASE="${KNOWLEDGE_BASE:-~/.claude/knowledge}"

# Optional
WORKLOG_DB="${WORKLOG_DB:-}"              # Log validation results to worklog
DOCS_QUERY_SCRIPT="${DOCS_QUERY_SCRIPT:-}" # Path to query-docs.sh or equivalent
```

---

## When to Use

**Monthly Hygiene:**
- First of each month: validate all documentation
- Check for compliance drift
- Identify stale or outdated content

**Before Major Commits:**
- After documentation reorganization
- Before releasing documentation to other environments
- After bulk documentation updates

**After Major Doc Changes:**
- New documentation added
- READMEs updated
- Structure changes

**Proactive Quality Checks:**
- When you notice potential issues
- After agent updates
- Periodic spot-checks

---

## What This Skill Validates

### 1. Frontmatter Compliance

**Checks:**
- ✅ All .md files have YAML frontmatter
- ✅ Required fields present: `title`, `type`, `created`
- ✅ Valid `type` values: decision, learning, guide, reference, changelog, environment
- ✅ Dates in YYYY-MM-DD format
- ✅ `status` values if present: active, deprecated, superseded
- ✅ Tags are arrays, not strings

**Reports:**
- Files missing frontmatter
- Files with incomplete required fields
- Invalid field values
- Malformed dates

### 2. Internal Link Validation

**Checks:**
- ✅ All `[text](path)` links point to existing files
- ✅ Relative paths resolve correctly
- ✅ No broken cross-references
- ✅ README links to all files in directory

**Reports:**
- Broken links (file doesn't exist)
- Incorrect relative paths
- Orphaned files (not linked from any README)

### 3. CHANGELOG Compliance

**Checks:**
- ✅ READMEs have Changelog sections
- ✅ Changelog entries have proper format
- ✅ Recent changes are documented
- ✅ Commit hashes present where applicable

**Reports:**
- READMEs missing Changelog section
- Malformed changelog entries
- Undocumented recent changes (from git log)

### 4. README Completeness

**Checks:**
- ✅ Every subdirectory has README.md
- ✅ READMEs reference all files in directory
- ✅ READMEs have frontmatter
- ✅ Navigation links work

**Reports:**
- Directories missing READMEs
- Files not referenced in README
- README frontmatter issues

### 5. Structure Compliance

**Checks:**
- ✅ Files in correct directories (security docs in security/, guides in guides/)
- ✅ No orphaned files in root
- ✅ Archive properly organized
- ✅ Naming conventions followed

**Reports:**
- Misplaced files
- Files that should be archived
- Naming convention violations

---

## Validation Workflow

### Step 1: Scan Documentation

```bash
# Scan primary documentation
cd $DOCS_ROOT
find . -type f -name "*.md" | grep -v archive/
```

### Step 2: Check Frontmatter

For each markdown file:
1. Extract YAML frontmatter (between `---` delimiters)
2. Parse required fields: title, type, created
3. Validate optional fields if present
4. Check data formats and allowed values
5. Report issues

### Step 3: Validate Links

For each markdown file:
1. Extract all `[text](path)` patterns
2. Resolve relative paths
3. Check if target exists
4. Report broken links

### Step 4: Check READMEs

For each subdirectory:
1. Verify README.md exists
2. Extract all file references
3. Compare with actual files in directory
4. Report orphaned or unreferenced files

### Step 5: Verify CHANGELOGs

For each README:
1. Check for Changelog section
2. Parse entries (Date - Title format)
3. Compare with recent git commits (if in git repo)
4. Report missing or malformed entries

### Step 6: Generate Report

Create validation report in `/tmp/docs-validation-YYYY-MM-DD.md`:
- Summary (files checked, issues found)
- Issues by category (Frontmatter, Links, READMEs, CHANGELOGs)
- Severity levels (Critical, Warning, Info)
- Recommended actions

---

## Validation Report Format

```markdown
# Documentation Validation Report
**Date:** YYYY-MM-DD HH:MM
**Scope:** $DOCS_ROOT
**Files Checked:** N
**Issues Found:** N

## Summary

- ❌ Critical: N (must fix)
- ⚠️  Warning: N (should fix)
- ℹ️  Info: N (consider fixing)

## Critical Issues

### Missing Frontmatter
- `path/to/file.md` - No frontmatter block found

### Broken Links
- `path/to/file.md:42` - Link to `missing.md` (file doesn't exist)

## Warnings

### Incomplete Frontmatter
- `path/to/file.md` - Missing required field: `created`

### Orphaned Files
- `security/old-config.md` - Not referenced in security/README.md

## Info

### Potential Improvements
- Consider adding `tags` field to improve queryability
- README could reference additional files

## Recommended Actions

1. Fix critical issues first (broken links, missing frontmatter)
2. Address warnings (incomplete frontmatter, orphaned files)
3. Consider info items for next documentation pass

## Files Validated

- $DOCS_ROOT/*.md (N files)
- $DOCS_ROOT/security/*.md (N files)
- $DOCS_ROOT/guides/*.md (N files)
- ...
```

---

## Validation Rules Reference

### Required Frontmatter Fields

```yaml
---
title: "Brief descriptive title"
type: decision|learning|guide|reference|changelog|environment
created: YYYY-MM-DD
---
```

### Optional Frontmatter Fields

```yaml
updated: YYYY-MM-DD
tags: [tag1, tag2, tag3]
status: active|deprecated|superseded
category: "Primary category"
related: [path/to/doc.md]
commit: abc1234
environment: system-name
```

### Valid Type Values

| Type | Use Case |
|------|----------|
| `decision` | Architectural or operational decisions |
| `learning` | Lessons learned from incidents or tasks |
| `guide` | How-to documentation and procedures |
| `reference` | Reference documentation and indexes |
| `changelog` | Change history and logs |
| `environment` | Environment-specific documentation |

### Date Format

- **YYYY-MM-DD** (e.g., 2025-01-15)
- ISO 8601 compliant
- Sortable chronologically

### Status Values

| Status | Meaning |
|--------|---------|
| `active` | Currently in use |
| `deprecated` | No longer recommended, but still referenced |
| `superseded` | Replaced by newer documentation |

---

## Quick Validation Mode

For fast checks before commits:

**Quick Mode Checks:**
- ✅ Frontmatter exists
- ✅ Required fields present
- ✅ No obvious broken links
- ⏩ Skip detailed analysis

**Usage:**
```bash
# Quick validation (1-2 minutes)
/skill docs-validator --quick

# Full validation (5-10 minutes)
/skill docs-validator

# Specific directory
/skill docs-validator --path $DOCS_ROOT/security
```

---

## Integration with Other Tools

### With Query Script

When `$DOCS_QUERY_SCRIPT` is set, validation ensures all documents are queryable:

```bash
# After validation, these queries should work
$DOCS_QUERY_SCRIPT --type guide
$DOCS_QUERY_SCRIPT --tag security
$DOCS_QUERY_SCRIPT --status active
```

### With docs-manager

Validation complements docs-manager:
- **docs-manager**: Creates and updates documentation
- **docs-validator**: Ensures quality and compliance

**Workflow:**
1. Use docs-manager for all documentation updates
2. Run docs-validator monthly or before major commits
3. Fix issues identified by validator
4. Log results to worklog if enabled

### With System Analyzer

Validation can be part of baseline checks:
- Run validator after baseline capture
- Include validation report in system audit
- Track documentation health over time

---

## Common Issues and Fixes

### Missing Frontmatter

**Issue:** File has no YAML frontmatter

**Fix:**
```bash
# Add frontmatter to file
cat > /tmp/frontmatter.txt <<'EOF'
---
title: "File Title"
type: guide
created: 2025-01-15
---

EOF

# Prepend to file
cat /tmp/frontmatter.txt original.md > new.md
mv new.md original.md
```

### Broken Link

**Issue:** `[text](missing.md)` points to non-existent file

**Fix:**
- Update link to correct path
- Create missing file if needed
- Remove link if no longer relevant

### Orphaned File

**Issue:** File exists but not referenced in README

**Fix:**
```markdown
# In README.md, add reference:

**[File Title](filename.md)** - Brief description

**Contents:**
- Key point 1
- Key point 2
```

### Malformed Changelog Entry

**Issue:** Changelog entry doesn't follow format

**Fix:**
```markdown
# Correct format:

### YYYY-MM-DD - Title
**Changed:** What changed
**Why:** Reason for change
**Impact:** Effect of change

**See also:** Related documentation
```

---

## Worklog Integration

When `$WORKLOG_DB` is set, log validation results:

```bash
sqlite3 "$WORKLOG_DB" "INSERT INTO entries
(agent, task_type, title, details, outcome, tags) VALUES (
'$(hostname)',
'validation',
'Documentation validation - $DOCS_ROOT',
'Checked N files, found N issues (N critical, N warning)',
'Validation complete - see /tmp/docs-validation-YYYY-MM-DD.md',
'docs,validation,quality'
);"
```

---

## Automation Opportunities

### Pre-Commit Hook

Could validate before git commits:
```bash
#!/bin/bash
# .git/hooks/pre-commit
/skill docs-validator --quick
```

### Monthly Validation Cron

Could be automated to run monthly:
```bash
# Add to crontab (if desired)
0 9 1 * * /skill docs-validator > /tmp/monthly-validation.log
```

### Integration with CI/CD

If documentation repo has CI:
- Run validator on pull requests
- Block merges with critical issues
- Generate reports as artifacts

---

## Example Validation Session

**User:** "Run docs validation"

**Skill Actions:**
1. Scan $DOCS_ROOT for all .md files
2. Check frontmatter compliance (required fields, valid values)
3. Validate internal links
4. Check README completeness
5. Verify CHANGELOG entries
6. Generate report in /tmp/docs-validation-YYYY-MM-DD.md
7. Present summary to user
8. Offer to fix critical issues

**Output:**
```
📋 Documentation Validation Report

Checked: 42 files
Issues: 3 critical, 5 warnings, 2 info

❌ Critical Issues:
- security/new-policy.md: Missing frontmatter
- guides/README.md: Broken link to old-guide.md
- services/deploy.md: Missing required field 'created'

⚠️  Warnings:
- 5 files not referenced in READMEs

ℹ️  Info:
- Consider adding tags to 2 files for better queryability

Full report: /tmp/docs-validation-YYYY-MM-DD.md

Fix critical issues? (y/n)
```

---

## Success Criteria

**Good documentation system:**
- ✅ All files have frontmatter
- ✅ All links work
- ✅ Every directory has README
- ✅ All files referenced
- ✅ CHANGELOGs current
- ✅ Structure compliant

**After validation:**
- Critical issues: 0
- Warnings: Minimal
- Info items: Tracked for next pass

---

## For Future Claude Instances

**When to run docs-validator:**
- Monthly (first of month)
- After major documentation changes
- Before important commits
- When documentation issues suspected

**How to use:**
```bash
# Full validation
/skill docs-validator

# Quick check
/skill docs-validator --quick

# Specific directory
/skill docs-validator --path $DOCS_ROOT/security
```

**Remember:** Validation is proactive. Catch issues before they become problems.

---

**Skill Version:** 2.0.0
**Philosophy:** Proactive quality assurance. Early detection. Maintainable documentation.
