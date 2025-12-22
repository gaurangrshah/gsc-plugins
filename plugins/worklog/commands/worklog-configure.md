---
description: "Setting to change: profile, backend, or show"
arguments:
  - name: setting
    description: "Setting to change: profile, backend, or show"
    required: false
---

# Worklog Configure

Modify worklog settings after initial setup.

## Usage

```
/worklog-configure              # Interactive menu
/worklog-configure show         # Show current settings
/worklog-configure backend      # Change database backend
/worklog-configure profile      # Change profile level
```

## Workflow

### Step 1: Read Current Configuration

Load settings from `.claude/worklog.local.md`:
- `backend`: sqlite or postgresql
- `profile`: minimal/standard/full
- `db_path`: SQLite database path
- `database_url`: PostgreSQL connection (if applicable)

If config not found:
```
Worklog not configured.
Run /worklog-init to set up.
```

### Step 2: Show Current Settings

**For SQLite:**
```bash
DB="${WORKLOG_DB_PATH:-$HOME/.claude/worklog/worklog.db}"
[ -f "$DB" ] && echo "Database: ✅ Found" || echo "Database: ❌ Not found"
sqlite3 "$DB" "SELECT COUNT(*) as count FROM entries;" 2>/dev/null
```

**For PostgreSQL:**
```bash
psql -c "SELECT 1;" > /dev/null 2>&1 && echo "Connection: ✅ OK" || echo "Connection: ❌ Failed"
psql -t -c "SELECT COUNT(*) FROM entries;"
```

```
Current Worklog Configuration:
==============================

Backend:        {sqlite|postgresql}
Profile:        {profile}
Hook Mode:      {hook_mode}

{For SQLite:}
Database Path:  {db_path}
Database Size:  {size}

{For PostgreSQL:}
Host:           {host}
Port:           {port}
Database:       {database}

Content Stats:
- Entries:      {count}
- Knowledge:    {count}
- Memories:     {count}

What would you like to change?
[1] Backend (switch between SQLite/PostgreSQL)
[2] Profile (minimal/standard/full)
[3] Test connection
[4] Exit
```

### Step 3: Change Backend

If switching from SQLite to PostgreSQL:
```
Switching to PostgreSQL requires:
1. A running PostgreSQL server
2. Connection credentials

Configure connection:
[A] DATABASE_URL
[B] Individual PG* variables

Note: Your SQLite data will NOT be migrated automatically.
```

If switching from PostgreSQL to SQLite:
```
Switching to SQLite will create a local database at:
~/.claude/worklog/worklog.db

Note: Your PostgreSQL data will NOT be migrated automatically.
Continue? (y/n)
```

### Step 4: Change Profile

```
Select new profile:

[1] MINIMAL - Manual store/recall only
[2] STANDARD - Light boot queries (Recommended)
[3] FULL - Aggressive context loading
```

Update `.claude/worklog.local.md` and replace CLAUDE.md section with new template.

### Step 5: Test Connection

**SQLite:**
```bash
DB="${WORKLOG_DB_PATH:-$HOME/.claude/worklog/worklog.db}"
sqlite3 "$DB" "SELECT 'Connection OK' as status, COUNT(*) as entries FROM entries;"
```

**PostgreSQL:**
```bash
psql -c "SELECT 'Connection OK' as status, COUNT(*) as entries FROM entries;"
```

### Step 6: Update Configuration File

Rewrite `.claude/worklog.local.md`:

```markdown
---
profile: {new_profile}
hook_mode: {new_hook_mode}
backend: {backend}
db_path: {path}                    # for SQLite
database_url: {url}                # for PostgreSQL
system_name: {hostname}
initialized: {original_timestamp}
last_modified: {now}
---

# Worklog Configuration

## Change History
- {timestamp}: {what changed}
```

### Step 7: Confirm Changes

```
Configuration updated!

Backend:  {backend}
Profile:  {profile}
Status:   ✅ Connected

Run `/worklog-status` to verify.
```

## Troubleshooting

### SQLite Issues

**Database not found:**
```
The database file doesn't exist at the expected path.
Run /worklog-init to create it.
```

**Permission denied:**
```
Cannot write to database. Check permissions:
ls -la ~/.claude/worklog/
```

### PostgreSQL Issues

**Connection refused:**
```
1. Check if PostgreSQL server is running
2. Verify host and port are correct
3. Check network connectivity
```

**Authentication failed:**
```
1. Verify credentials
2. Check username and password
3. Verify database name
```

### Environment Not Set

**For PostgreSQL:**
```bash
# Check environment
echo "DATABASE_URL: ${DATABASE_URL:-not set}"
echo "PGHOST: ${PGHOST:-not set}"

# Set if needed
export DATABASE_URL="postgresql://user:pass@host:port/db"
source ~/.zshrc
```

$ARGUMENTS
