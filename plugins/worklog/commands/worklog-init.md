---
description: Initialize worklog database for cross-session persistence (primary system setup)
arguments: []
---

# Worklog Init

Initialize the worklog database on this system. Use this command on your **primary system** to create the database. For secondary systems connecting to a shared database, use `/worklog-connect` instead.

## Workflow

### Step 1: Choose Integration Profile

Ask the user to select their preferred integration level:

**[1] MINIMAL** - Lightweight persistence
- Core tables only (6 tables)
- Manual store/recall via skills
- No automatic boot queries
- CLAUDE.md addition: ~20 lines
- Best for: Occasional use, minimal overhead

**[2] STANDARD** - Balanced integration (Recommended)
- Core tables (6 tables)
- Light boot queries for recent context
- Prompts to store learnings at task end
- CLAUDE.md addition: ~50 lines
- Best for: Daily use, cross-session continuity

**[3] FULL** - Maximum context awareness
- All tables (10 tables including projects, components)
- Aggressive boot queries (protocols, recent work, errors)
- Auto-store task outcomes
- Network failure handling with handoffs
- CLAUDE.md addition: ~100 lines
- Best for: Multi-system, team/agency workflows

### Step 2: Choose Database Location

Ask the user:

**[A] Local** (Default)
- Path: `~/.claude/worklog/worklog.db`
- Single system use
- No network dependencies

**[B] Shared**
- User provides path (e.g., `/mnt/shared/worklog.db`)
- Multi-system access
- Requires network mount

### Step 3: Create Backups (Safety Protocol)

**Before making ANY changes**, backup existing files:

```bash
BACKUP_TS=$(date +%Y%m%d%H%M%S)
BACKUP_DIR=~/.claude/.worklog-backup-$BACKUP_TS

mkdir -p $BACKUP_DIR

# Backup CLAUDE.md if exists
if [ -f ~/.claude/CLAUDE.md ]; then
  cp ~/.claude/CLAUDE.md $BACKUP_DIR/CLAUDE.md
  echo "Backed up: CLAUDE.md"
fi

# Backup existing config if exists
if [ -f ~/.claude/worklog.local.md ]; then
  cp ~/.claude/worklog.local.md $BACKUP_DIR/worklog.local.md
  echo "Backed up: worklog.local.md"
fi

# Record backup location
echo $BACKUP_DIR > ~/.claude/.worklog-backup-path
```

Inform the user: "Created backup at {BACKUP_DIR}. You can rollback if needed."

### Step 4: Create Database

Based on profile selection:

```bash
# Create directory if local
mkdir -p ~/.claude/worklog

# Initialize with core schema
sqlite3 {db_path} < {plugin_root}/schema/core.sql

# If FULL profile, add extended schema
sqlite3 {db_path} < {plugin_root}/schema/extended.sql

# Verify creation
sqlite3 {db_path} "SELECT name FROM sqlite_master WHERE type='table';"
```

### Step 5: Create Plugin Configuration

Create `.claude/worklog.local.md` with YAML frontmatter:

```markdown
---
profile: {selected_profile}
db_path: {selected_path}
mode: {local|shared}
system_name: {hostname or user-provided}
initialized: {timestamp}
backup_path: {backup_dir}
---

# Worklog Configuration

This file stores your worklog plugin settings.

## Current Settings
- **Profile:** {profile}
- **Database:** {db_path}
- **Mode:** {mode}

To change settings, run `/worklog-configure`.
```

### Step 6: Inject CLAUDE.md Section

Read the appropriate template from `{plugin_root}/templates/` based on profile:
- `minimal.md` for MINIMAL profile
- `standard.md` for STANDARD profile
- `full.md` for FULL profile

**Check for existing worklog section:**
```bash
grep -q "<!-- WORKLOG_START -->" ~/.claude/CLAUDE.md
```

- If exists: Ask user "Existing worklog section found. Replace it? (y/n)"
  - If yes: Remove content between `<!-- WORKLOG_START -->` and `<!-- WORKLOG_END -->`, then insert new
  - If no: Abort and restore backup
- If not exists: Append template content to CLAUDE.md

### Step 7: Run Verification

**Automated checks:**

```bash
# 1. Database exists and is valid
sqlite3 {db_path} "SELECT 1;" > /dev/null 2>&1
DB_OK=$?

# 2. Expected tables present
TABLES=$(sqlite3 {db_path} "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN ('entries','knowledge_base','memories','issues','error_patterns','research');")
TABLES_OK=$([ "$TABLES" -eq 6 ] && echo 0 || echo 1)

# 3. CLAUDE.md has marker
grep -q "<!-- WORKLOG_START -->" ~/.claude/CLAUDE.md
MARKER_OK=$?

# 4. Config file exists
[ -f ~/.claude/worklog.local.md ]
CONFIG_OK=$?

# 5. Write test
sqlite3 {db_path} "INSERT INTO entries (agent, task_type, title) VALUES ('_verify','_verify','_verify'); DELETE FROM entries WHERE agent='_verify';"
WRITE_OK=$?
```

**Display verification results:**

```
Verification Results
====================
Database valid:     {✅|❌}
Tables present:     {✅|❌} ({count}/6 core tables)
CLAUDE.md updated:  {✅|❌}
Config created:     {✅|❌}
Write test:         {✅|❌}
```

### Step 8: User Confirmation

If all checks pass:
```
Installation complete!

Changes made:
- Created database: {db_path}
- Updated: ~/.claude/CLAUDE.md
- Created: ~/.claude/worklog.local.md

Keep these changes? (y/n)
```

**If user says YES:**
```bash
# Register system in database
sqlite3 {db_path} "INSERT INTO entries (agent, task_type, title, details, outcome, tags)
VALUES ('{system_name}', 'initialization', 'Worklog plugin initialized',
'Profile: {profile}, Path: {db_path}, Mode: {mode}',
'Database created and CLAUDE.md updated',
'system:{system_name},type:init,profile:{profile}');"

# Remove backup path marker (keep backup for 7 days)
rm ~/.claude/.worklog-backup-path

echo "Installation finalized. Backup retained at $BACKUP_DIR for 7 days."
```

**If user says NO:**
```bash
# Restore from backup
BACKUP_DIR=$(cat ~/.claude/.worklog-backup-path)

if [ -f $BACKUP_DIR/CLAUDE.md ]; then
  cp $BACKUP_DIR/CLAUDE.md ~/.claude/CLAUDE.md
fi

rm -f ~/.claude/worklog.local.md
rm -f {db_path}  # Only if we created it

rm ~/.claude/.worklog-backup-path
rm -rf $BACKUP_DIR

echo "Rolled back. All changes reverted."
```

### Step 9: Provide Next Steps (on success)

```
Worklog initialized successfully!

Database: {db_path}
Profile: {profile}
Mode: {mode}

Next steps:
- Use `memory-store` skill to save learnings
- Use `memory-recall` skill to query context
- Run `/worklog-status` to check connectivity

{If shared mode:}
For other systems, run:
  /worklog-connect {db_path}
```

## Error Handling

**Directory creation fails:**
- Check permissions
- Suggest alternative path
- Rollback automatically

**Schema application fails:**
- Verify sqlite3 is installed
- Check disk space
- Rollback automatically
- Provide manual recovery steps

**CLAUDE.md not found:**
- Create minimal CLAUDE.md with worklog section
- Or ask user for correct path

**Verification fails:**
- Show which checks failed
- Offer to rollback or retry
- Provide troubleshooting guidance

## Rollback Command

If user needs to rollback later:

```bash
# Find most recent backup
BACKUP=$(ls -td ~/.claude/.worklog-backup-* 2>/dev/null | head -1)

if [ -n "$BACKUP" ]; then
  cp $BACKUP/CLAUDE.md ~/.claude/CLAUDE.md
  rm -f ~/.claude/worklog.local.md
  echo "Restored from $BACKUP"
else
  echo "No backup found"
fi
```
