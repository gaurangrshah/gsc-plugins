---
description: Initialize worklog database for cross-session persistence (primary system setup)
arguments: []
---

# Worklog Init

Initialize the worklog plugin for cross-session knowledge persistence.

## Overview

This command sets up the worklog database on your system. Choose between:

- **SQLite (Default)**: Local database, no external dependencies
- **PostgreSQL (Optional)**: Shared database for multi-system setups

## Workflow

### Step 1: Choose Database Backend

```
Which database backend would you like to use?

[A] SQLite (Recommended for most users)
    - Local database at ~/.claude/worklog/worklog.db
    - No external dependencies
    - Works offline
    - Single system use

[B] PostgreSQL (For multi-system setups)
    - Shared database across systems
    - Requires PostgreSQL server
    - Enables cross-agent collaboration
    - Requires network connectivity
```

---

### If SQLite Selected:

#### Step 2a: Choose Integration Profile

**[1] MINIMAL** - Lightweight persistence
- Manual store/recall via skills
- No automatic boot queries
- CLAUDE.md addition: ~20 lines
- Best for: Occasional use, minimal overhead

**[2] STANDARD** - Balanced integration (Recommended)
- Light boot queries for recent context
- Prompts to store learnings at task end
- CLAUDE.md addition: ~50 lines
- Best for: Daily use, cross-session continuity

**[3] FULL** - Maximum context awareness
- Aggressive boot queries (protocols, recent work, errors)
- Auto-store task outcomes
- CLAUDE.md addition: ~100 lines
- Best for: Power users wanting full automation

#### Step 3a: Create Database

```bash
# Create directory
mkdir -p ~/.claude/worklog

# Database will be auto-created by the MCP server on first use
# Or create manually with schema:
sqlite3 ~/.claude/worklog/worklog.db < {plugin_root}/schema/core.sql
```

#### Step 4a: Configure Environment

```bash
# Optional: Set custom database path
export WORKLOG_DB_PATH=~/.claude/worklog/worklog.db

# Or use default (no config needed)
```

---

### If PostgreSQL Selected:

#### Step 2b: Choose Integration Profile

Same options as SQLite (MINIMAL, STANDARD, FULL)

#### Step 3b: Configure Connection

```
How would you like to configure the PostgreSQL connection?

[A] DATABASE_URL (Recommended)
    Single environment variable with full connection string

[B] Individual PG* variables
    Separate PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
```

**Option A - DATABASE_URL:**

```bash
# Add to ~/.zshrc or ~/.bashrc:
export DATABASE_URL="postgresql://user:password@host:port/database"

# Then run: source ~/.zshrc
```

**Option B - Individual Variables:**

```bash
# Add to ~/.zshrc or ~/.bashrc:
export PGHOST=your-host
export PGPORT=5432
export PGDATABASE=worklog
export PGUSER=worklog
export PGPASSWORD="your-password"

# Then run: source ~/.zshrc
```

#### Step 4b: Test Connection

```bash
psql -c "SELECT 1;"
```

---

### Step 5: Create Backups (Safety Protocol)

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

echo $BACKUP_DIR > ~/.claude/.worklog-backup-path
```

### Step 6: Create Plugin Configuration

Create `.claude/worklog.local.md`:

```markdown
---
profile: {selected_profile}
hook_mode: {selected_hook_mode}
backend: {sqlite|postgresql}
db_path: ~/.claude/worklog/worklog.db  # for SQLite
# database_url: postgresql://...       # for PostgreSQL
system_name: {hostname}
initialized: {timestamp}
---

# Worklog Configuration

## Backend
- **Type:** {backend}
- **Path/URL:** {path_or_url}

## Settings
- **Profile:** {profile}
- **Hook Mode:** {hook_mode}

To reconfigure, run `/worklog-configure`.
```

### Step 7: Inject CLAUDE.md Section

Read appropriate template from `{plugin_root}/templates/` based on profile:
- `minimal.md` for MINIMAL profile
- `standard.md` for STANDARD profile
- `full.md` for FULL profile

Replace `{DB_PATH}` or `{DATABASE_URL}` placeholders with actual values.

For SQLite, boot queries use `sqlite3`:
```bash
sqlite3 ~/.claude/worklog/worklog.db "SELECT ..."
```

For PostgreSQL, boot queries use `psql`:
```bash
psql -c "SELECT ..."
```

### Step 8: Run Verification

**SQLite Verification:**
```bash
DB=~/.claude/worklog/worklog.db
[ -f "$DB" ] && echo "Database: ✅" || echo "Database: ❌"
sqlite3 "$DB" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" && echo "Schema: ✅"
grep -q "WORKLOG_START" ~/.claude/CLAUDE.md && echo "CLAUDE.md: ✅" || echo "CLAUDE.md: ❌"
```

**PostgreSQL Verification:**
```bash
psql -c "SELECT 1;" && echo "Connection: ✅" || echo "Connection: ❌"
psql -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" && echo "Schema: ✅"
grep -q "WORKLOG_START" ~/.claude/CLAUDE.md && echo "CLAUDE.md: ✅" || echo "CLAUDE.md: ❌"
```

### Step 9: User Confirmation

```
Installation complete!

Backend:  {sqlite|postgresql}
Profile:  {profile}
Hook:     {hook_mode}

Changes made:
- Created: ~/.claude/worklog.local.md
- Updated: ~/.claude/CLAUDE.md
{If SQLite: - Created: ~/.claude/worklog/worklog.db}

Keep these changes? (y/n)
```

**If YES:** Finalize installation
**If NO:** Rollback from backup

### Step 10: Provide Next Steps

```
Worklog initialized successfully!

Backend: {backend}
Profile: {profile}

Next steps:
- Use `memory-store` skill to save learnings
- Use `memory-recall` skill to query context
- Run `/worklog-status` to check connectivity

MCP tools available:
- store_memory, recall_context, search_knowledge
- log_entry, store_knowledge, query_table
```

## Error Handling

**SQLite creation fails:**
- Check write permissions to ~/.claude/
- Verify disk space available

**PostgreSQL connection fails:**
- Verify environment variables are set
- Check network connectivity
- Verify credentials

**CLAUDE.md not found:**
- Create minimal CLAUDE.md with worklog section

## Rollback Command

```bash
BACKUP=$(ls -td ~/.claude/.worklog-backup-* 2>/dev/null | head -1)
if [ -n "$BACKUP" ]; then
  cp $BACKUP/CLAUDE.md ~/.claude/CLAUDE.md 2>/dev/null
  rm -f ~/.claude/worklog.local.md
  echo "Restored from $BACKUP"
fi
```
