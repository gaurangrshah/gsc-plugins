---
description: Connect to an existing shared worklog database (secondary system setup)
arguments:
  - name: db_path
    description: Path to the shared worklog database
    required: false
---

# Worklog Connect

Connect this system to an existing shared worklog database. Use this on **secondary systems** after the primary system has run `/worklog-init`.

## Workflow

### Step 1: Get Database Path

If `db_path` argument provided, use it. Otherwise, ask user:

```
Enter the path to the shared worklog database:

**System-specific paths for shared NAS:**
| System | Path |
|--------|------|
| atlas (Mac) | `/Volumes/dev-env/workspace/logs/worklog.db` |
| ubuntu-mini | `/mnt/nasdevenv/workspace/logs/worklog.db` |

> Note: On ubuntu-mini, `~/workspace/logs/` does NOT exist. Use `/mnt/nasdevenv/` path.
```

### Step 2: Verify Database Exists

```bash
# Check file exists
test -f {db_path} && echo "Found" || echo "Not found"

# Verify it's a valid SQLite database
sqlite3 {db_path} "SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;"
```

**If not found:**
- Check if mount point exists
- Suggest mount commands if network path
- Ask user to verify primary system ran `/worklog-init`

### Step 3: Test Connectivity

```bash
# Test read
sqlite3 {db_path} "SELECT COUNT(*) FROM entries;"

# Test write (insert then delete test row)
sqlite3 {db_path} "INSERT INTO entries (agent, task_type, title) VALUES ('_test', '_test', '_connectivity_test');"
sqlite3 {db_path} "DELETE FROM entries WHERE agent='_test' AND task_type='_test';"
```

**If write fails:**
- Check journal mode: `PRAGMA journal_mode;`
- Verify should be DELETE mode for network shares
- Check directory permissions

### Step 4: Detect Existing Profile

Query the database to see what tables exist:

```bash
sqlite3 {db_path} "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
```

Determine available profiles:
- 6 core tables only → MINIMAL or STANDARD available
- 10+ tables (includes projects, components) → FULL available

### Step 5: Choose Integration Profile

Present options based on what's available:

**[1] MINIMAL** - Lightweight persistence
**[2] STANDARD** - Balanced integration (Recommended)
**[3] FULL** - Maximum context awareness (if extended tables exist)

If user selects FULL but extended tables don't exist, offer to create them:
```
Extended tables not found. Create them now? (y/n)
```

### Step 6: Create Backups (Safety Protocol)

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

### Step 7: Create Plugin Configuration

Create `.claude/worklog.local.md`:

```markdown
---
profile: {selected_profile}
db_path: {db_path}
mode: shared
system_name: {hostname}
connected: {timestamp}
primary_system: false
backup_path: {backup_dir}
---

# Worklog Configuration

Connected to shared worklog database.

## Current Settings
- **Profile:** {profile}
- **Database:** {db_path}
- **Mode:** shared
- **System:** {system_name}

To change settings, run `/worklog-configure`.
```

### Step 8: Inject CLAUDE.md Section

Read appropriate template from `{plugin_root}/templates/` and process:

**Check for existing worklog section:**
```bash
grep -q "<!-- WORKLOG_START -->" ~/.claude/CLAUDE.md
```

- If exists: Ask user "Existing worklog section found. Replace it? (y/n)"
  - If yes: Remove content between `<!-- WORKLOG_START -->` and `<!-- WORKLOG_END -->`, then insert new
  - If no: Abort and restore backup
- If not exists: Append template content to CLAUDE.md

Include network-specific additions for shared mode:
- Retry logic for writes
- Handoff mechanism for persistent failures

### Step 9: Run Verification

**Automated checks:**

```bash
# 1. Database accessible
sqlite3 {db_path} "SELECT 1;" > /dev/null 2>&1
DB_OK=$?

# 2. CLAUDE.md has marker
grep -q "<!-- WORKLOG_START -->" ~/.claude/CLAUDE.md
MARKER_OK=$?

# 3. Config file exists with correct path
grep -q "db_path: {db_path}" ~/.claude/worklog.local.md
CONFIG_OK=$?

# 4. Write test (with retry for network)
for i in 1 2 3; do
  sqlite3 {db_path} "INSERT INTO entries (agent, task_type, title) VALUES ('_verify','_verify','_verify'); DELETE FROM entries WHERE agent='_verify';" && WRITE_OK=0 && break
  WRITE_OK=1
  sleep 2
done
```

**Display verification results:**

```
Verification Results
====================
Database accessible: {✅|❌}
CLAUDE.md updated:   {✅|❌}
Config created:      {✅|❌}
Write test:          {✅|❌}
```

### Step 10: User Confirmation

If all checks pass:
```
Connection complete!

Changes made:
- Updated: ~/.claude/CLAUDE.md
- Created: ~/.claude/worklog.local.md

Database: {db_path}
Profile: {profile}

Keep these changes? (y/n)
```

**If user says YES:**
```bash
# Register system in database
sqlite3 {db_path} "INSERT INTO entries (agent, task_type, title, details, outcome, tags)
VALUES ('{system_name}', 'connection', 'System connected to shared worklog',
'Profile: {profile}, System: {system_name}',
'Successfully connected and configured',
'system:{system_name},type:connect,profile:{profile}');"

# Remove backup path marker (keep backup for 7 days)
rm ~/.claude/.worklog-backup-path

echo "Connection finalized. Backup retained at $BACKUP_DIR for 7 days."
```

**If user says NO:**
```bash
# Restore from backup
BACKUP_DIR=$(cat ~/.claude/.worklog-backup-path)

if [ -f $BACKUP_DIR/CLAUDE.md ]; then
  cp $BACKUP_DIR/CLAUDE.md ~/.claude/CLAUDE.md
fi

rm -f ~/.claude/worklog.local.md

rm ~/.claude/.worklog-backup-path
rm -rf $BACKUP_DIR

echo "Rolled back. All changes reverted."
```

### Step 11: Provide Confirmation (on success)

```
Connected to shared worklog!

Database: {db_path}
Profile: {profile}
System: {system_name}

The following systems are using this database:
{list recent entries grouped by agent}

Skills available:
- `memory-store` - Save learnings
- `memory-recall` - Query context
- `memory-sync` - Reconcile with local docs

Run `/worklog-status` to verify connectivity.
```

## Error Handling

**Verification fails:**
- Show which checks failed
- Offer to rollback or retry
- Provide troubleshooting guidance

**Database not found:**
- Check mount point
- Provide mount commands
- Suggest running `/worklog-init` on primary first

## Network Troubleshooting

**"database is locked"**
- Normal for SQLite over network
- Retry logic handles this automatically
- If persistent, check for stale connections on other systems

**"unable to open database file"**
- Verify mount: `mount | grep {mount_point}`
- Check permissions: `ls -la {db_path}`
- Verify journal mode is DELETE (not WAL)

**Mount commands by OS:**

macOS:
```bash
# SMB
mount -t smbfs //server/share /Volumes/mount_point
```

Linux:
```bash
# CIFS/SMB
sudo mount -t cifs //server/share /mnt/mount_point -o username=user,uid=1000
```

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

$ARGUMENTS
