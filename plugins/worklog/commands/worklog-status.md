---
description: Check worklog database connectivity and display statistics
arguments: []
---

# Worklog Status

Check worklog database connectivity and display usage statistics.

## Workflow

### Step 1: Load Configuration

Read `.claude/worklog.local.md` for settings:
- `backend`: sqlite or postgresql
- `profile`
- `db_path` or `database_url`

If config not found:
```
Worklog not configured.
Run /worklog-init to set up.
```

### Step 2: Detect Backend

```bash
# Auto-detect backend from environment
if [ -n "$DATABASE_URL" ] || [ -n "$PGHOST" ]; then
    BACKEND="postgresql"
else
    BACKEND="sqlite"
fi
echo "Backend: $BACKEND"
```

### Step 3: Test Connectivity

**SQLite:**
```bash
DB="${WORKLOG_DB_PATH:-$HOME/.claude/worklog/worklog.db}"
sqlite3 "$DB" "SELECT 1;" 2>&1
```

**PostgreSQL:**
```bash
psql -c "SELECT 1;" 2>&1
```

### Step 4: Gather Statistics

**SQLite:**
```bash
DB="${WORKLOG_DB_PATH:-$HOME/.claude/worklog/worklog.db}"

# Table counts
sqlite3 "$DB" "
SELECT
  (SELECT COUNT(*) FROM entries) as entries,
  (SELECT COUNT(*) FROM knowledge_base) as knowledge,
  (SELECT COUNT(*) FROM memories) as memories;
"

# Recent activity
sqlite3 "$DB" "
SELECT agent, COUNT(*) as count
FROM entries
WHERE timestamp > datetime('now', '-7 days')
GROUP BY agent;
"

# Database size
ls -lh "$DB" | awk '{print $5}'
```

**PostgreSQL:**
```bash
# Table counts
psql -t -c "
SELECT
  (SELECT COUNT(*) FROM entries) as entries,
  (SELECT COUNT(*) FROM knowledge_base) as knowledge,
  (SELECT COUNT(*) FROM memories) as memories;
"

# Recent activity
psql -t -c "
SELECT agent, COUNT(*) as count
FROM entries
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY agent;
"

# Database size
psql -t -c "SELECT pg_size_pretty(pg_database_size(current_database()));"
```

### Step 5: Display Status

```
Worklog Status
==============

Backend:     {sqlite|postgresql}
Connection:  ✅ Connected
Profile:     {profile}

{For SQLite:}
Database:    {db_path}
Size:        {size}

{For PostgreSQL:}
Host:        {host}:{port}
Database:    {database}
Size:        {size}

Content:
--------
Entries:         {count}
Knowledge Base:  {count}
Memories:        {count}
Open Issues:     {count}
Error Patterns:  {count}

Recent Activity (7 days):
-------------------------
{agent}: {count} entries
{agent}: {count} entries

Last Entry:
-----------
{timestamp} | {agent} | {title}
```

### Step 6: Test Write Access

**SQLite:**
```bash
sqlite3 "$DB" "INSERT INTO entries (agent, task_type, title) VALUES ('_test', '_test', '_test'); DELETE FROM entries WHERE agent='_test';"
echo "Write: ✅"
```

**PostgreSQL:**
```bash
psql -c "INSERT INTO entries (agent, task_type, title) VALUES ('_test', '_test', '_test'); DELETE FROM entries WHERE agent='_test';"
echo "Write: ✅"
```

### Troubleshooting Output

If connectivity fails:

**SQLite:**
```
Worklog Status
==============

Backend:     SQLite
Connection:  ❌ Failed
Database:    {db_path}
Error:       {error_message}

Troubleshooting:
----------------
1. Check if file exists: ls -la {db_path}
2. Check permissions: test -w {db_path} && echo "Writable"
3. Check directory exists: ls -la ~/.claude/worklog/

Run /worklog-init to create database.
```

**PostgreSQL:**
```
Worklog Status
==============

Backend:     PostgreSQL
Connection:  ❌ Failed
Error:       {error_message}

Troubleshooting:
----------------
{If "connection refused":}
1. Check server is running
2. Verify host and port
3. Check network connectivity

{If "authentication failed":}
1. Verify credentials
2. Check DATABASE_URL or PG* variables

{If "could not translate host name":}
1. Check PGHOST is set
2. Verify environment variables

Run /worklog-configure to update settings.
```

## Quick Check Commands

**SQLite:**
```bash
sqlite3 ~/.claude/worklog/worklog.db "SELECT 'OK', COUNT(*) FROM entries;"
```

**PostgreSQL:**
```bash
psql -c "SELECT 'OK', COUNT(*) FROM entries;"
```
