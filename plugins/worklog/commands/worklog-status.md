---
description: Check worklog database connectivity and display statistics
arguments: []
---

# Worklog Status

Check worklog database connectivity and display usage statistics.

## Workflow

### Step 1: Load Configuration

Read `.claude/worklog.local.md` for settings:
- `profile`
- `db_path`
- `mode`
- `system_name`

If config not found:
```
Worklog not configured.
Run /worklog-init to set up, or /worklog-connect to join existing.
```

### Step 2: Test Connectivity

```bash
# Test database access
sqlite3 {db_path} "SELECT 1;" 2>&1
```

**If successful:** Continue to stats
**If failed:** Show troubleshooting

### Step 3: Gather Statistics

```sql
-- Table counts
SELECT
  (SELECT COUNT(*) FROM entries) as entries,
  (SELECT COUNT(*) FROM knowledge_base) as knowledge,
  (SELECT COUNT(*) FROM memories) as memories,
  (SELECT COUNT(*) FROM issues WHERE status='open') as open_issues,
  (SELECT COUNT(*) FROM error_patterns) as error_patterns,
  (SELECT COUNT(*) FROM research) as research;

-- Recent activity
SELECT agent, COUNT(*) as count
FROM entries
WHERE timestamp > datetime('now', '-7 days')
GROUP BY agent;

-- Database size
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();
```

### Step 4: Display Status

```
Worklog Status
==============

Connection:  ✅ Connected
Database:    {db_path}
Profile:     {profile}
Mode:        {mode}
System:      {system_name}

Database Stats:
---------------
Size:            {size_mb} MB
Journal Mode:    {journal_mode}

Content:
--------
Entries:         {count}
Knowledge Base:  {count}
Memories:        {count}
Open Issues:     {count}
Error Patterns:  {count}
Research Items:  {count}

{If FULL profile and extended tables exist:}
Projects:        {count}
Components:      {count}
Clients:         {count}
Competitors:     {count}

Recent Activity (7 days):
-------------------------
{agent}: {count} entries
{agent}: {count} entries

Last Entry:
-----------
{timestamp} | {agent} | {title}
```

### Step 5: Network Health (if shared mode)

```sql
-- Check for recent write from this system
SELECT COUNT(*) FROM entries
WHERE agent = '{system_name}'
AND timestamp > datetime('now', '-1 hour');
```

Test write:
```bash
sqlite3 {db_path} "UPDATE entries SET id=id WHERE id=(SELECT MAX(id) FROM entries);" 2>&1
```

```
Network Health:
---------------
Read:   ✅ Working
Write:  ✅ Working (or ⚠️ Locked - retry in progress)

Other Systems Active (24h):
---------------------------
{system}: {last_seen}
{system}: {last_seen}
```

### Troubleshooting Output

If connectivity fails:

```
Worklog Status
==============

Connection:  ❌ Failed
Database:    {db_path}
Error:       {error_message}

Troubleshooting:
----------------

{If "unable to open database file":}
1. Check if path exists: ls -la {db_path}
2. If network path, verify mount: mount | grep {mount_point}
3. Check permissions on directory

{If "database is locked":}
1. This is normal for network databases
2. Wait 5-10 seconds and retry
3. Check for stale connections: lsof {db_path}

{If "disk I/O error":}
1. Verify network connectivity
2. Check mount health
3. Try remounting the share

Run /worklog-configure to update path if needed.
```
