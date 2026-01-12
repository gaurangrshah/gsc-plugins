---
description: Path to the shared worklog database
arguments:
  - name: db_path
    description: Path to SQLite database or PostgreSQL connection string
    required: false
---

# Worklog Connect

Connect to an existing worklog database. Supports both SQLite (default) and PostgreSQL backends.

**Note:** This is a quick-connect alias for `/worklog-init`. For full configuration including profile selection, run `/worklog-init` instead.

## Workflow

### Step 1: Detect Backend

If `db_path` argument provided:
- If ends with `.db` → SQLite
- If starts with `postgresql://` → PostgreSQL
- If empty → Interactive selection

```
Choose database backend:

[A] SQLite (Recommended for most users)
    Connect to local or shared SQLite database file
    - No external dependencies
    - Works offline

[B] PostgreSQL (For multi-system setups)
    Connect to PostgreSQL server
    - Shared database across systems
    - Requires network connectivity
```

---

### If SQLite Selected:

#### Step 2a: Get Database Path

```
Enter path to SQLite database:
- Local: ~/.claude/worklog/worklog.db (default)
- Shared: /mnt/nas/worklog.db

Path: _
```

#### Step 3a: Test Connection

```bash
DB="$PROVIDED_PATH"
[ -f "$DB" ] && echo "Database: ✅ Found" || echo "Database: ❌ Not found"
sqlite3 "$DB" "SELECT COUNT(*) as count FROM entries;"
```

If database exists and is readable:
```
SQLite Connection Test:
=======================
Database:  ✅ Found
Entries:   127
Tables:    6 core tables detected

Connection successful!
```

If not found:
```
Database not found at: /path/to/db

Options:
[1] Run /worklog-init to create new database
[2] Provide different path
[3] Cancel
```

---

### If PostgreSQL Selected:

#### Step 2b: Configure Connection

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

# Reload:
source ~/.zshrc
```

**Option B - Individual Variables:**

```bash
# Add to ~/.zshrc or ~/.bashrc:
export PGHOST=your-host
export PGPORT=5432
export PGDATABASE=worklog
export PGUSER=worklog
export PGPASSWORD="your-password"

# Reload:
source ~/.zshrc
```

#### Step 3b: Test Connection

```bash
psql -c "SELECT 'Connected!' as status, COUNT(*) as entries FROM entries;"
```

If successful:
```
PostgreSQL Connection Test:
===========================
Host:      your-host:5432
Database:  worklog
Status:    ✅ Connected
Entries:   127

Connection successful!
```

If fails:
```
PostgreSQL Connection Test:
===========================
Status:    ❌ Failed
Error:     {error_message}

Troubleshooting:
----------------
{If "connection refused":}
1. Check server is running
2. Verify host and port

{If "authentication failed":}
1. Verify credentials
2. Check DATABASE_URL or PG* variables

{If "could not translate host name":}
1. Check PGHOST is set correctly
2. Verify DNS/network connectivity
```

---

### Step 4: Create Configuration

Create `~/.gsc-plugins/worklog.local.md`:

```markdown
---
profile: standard
backend: {sqlite|postgresql}
db_path: {path}                    # for SQLite
# database_url: {url}             # for PostgreSQL (if using DATABASE_URL)
system_name: {hostname}
initialized: {timestamp}
---

# Worklog Configuration

Connected to existing database via /worklog-connect.
Run /worklog-configure to change settings.
```

### Step 5: Confirmation

```
Worklog connected!

Backend:  {sqlite|postgresql}
Status:   ✅ Connected
Entries:  {count}

For full configuration (profile, hooks), run:
/worklog-init

Commands available:
- /worklog-status - Check connectivity
- /worklog-configure - Change settings
```

## Quick Connect Examples

**SQLite (local):**
```
/worklog-connect ~/.claude/worklog/worklog.db
```

**SQLite (network share):**
```
/worklog-connect /Volumes/nas/shared/worklog.db
```

**PostgreSQL (via DATABASE_URL):**
```
/worklog-connect postgresql://user:pass@host:5432/worklog
```

## Troubleshooting

### SQLite Issues

**Database not found:**
```
1. Verify the file exists: ls -la /path/to/db
2. Check you have read permissions
3. If new setup, run /worklog-init instead
```

**Permission denied:**
```
1. Check file permissions: ls -la /path/to/db
2. For network shares, verify mount is writable
3. Check directory permissions for journal file
```

### PostgreSQL Issues

**Connection refused:**
```
1. Check if PostgreSQL server is running
2. Verify host and port are correct
3. Check network/firewall settings
```

**Authentication failed:**
```
1. Verify credentials in DATABASE_URL or PG* vars
2. Check username and password
3. Verify database name exists
```

**Environment not set:**
```bash
# Check environment
echo "DATABASE_URL: ${DATABASE_URL:-not set}"
echo "PGHOST: ${PGHOST:-not set}"

# Set if needed
export DATABASE_URL="postgresql://user:pass@host:port/db"
source ~/.zshrc
```

$ARGUMENTS
