# Network Database Protocol

Guidelines for using worklog over network shares (SMB/CIFS/NFS).

## Core Rules

1. **NEVER copy the database locally to edit** - Creates divergent data
2. **Always write directly to the network path** - Even if slower
3. **Use DELETE journal mode** - WAL doesn't work over network
4. **Expect intermittent locks** - Normal behavior, handle with retries

## Journal Mode

SQLite journal mode MUST be DELETE for network shares:

```sql
PRAGMA journal_mode=DELETE;
```

**Why:** WAL mode creates `.db-shm` and `.db-wal` files requiring shared memory locks, which don't work over network filesystems.

**Verify:**
```bash
sqlite3 /path/to/worklog.db "PRAGMA journal_mode;"
# Should return: delete
```

## Retry Logic

Network writes may fail with "database is locked". This is normal.

### Simple Retry

```bash
for i in 1 2 3; do
  sqlite3 $DB_PATH "YOUR SQL HERE" && break
  echo "Attempt $i failed, waiting..."
  sleep $((5 + RANDOM % 6))
done
```

### With Status Check

```bash
attempt=0
max_attempts=3

while [ $attempt -lt $max_attempts ]; do
  if sqlite3 $DB_PATH "YOUR SQL HERE" 2>/dev/null; then
    echo "Success"
    break
  fi
  attempt=$((attempt + 1))
  if [ $attempt -lt $max_attempts ]; then
    echo "Attempt $attempt failed, retrying in 5s..."
    sleep 5
  else
    echo "All attempts failed"
  fi
done
```

## Handoff Mechanism

When retries fail persistently, use file-based handoff for another system to process.

### Create Handoff

```bash
HANDOFF_DIR="${WORKLOG_DB_PATH%/*}/handoffs"
HANDOFF_FILE="$HANDOFF_DIR/$(hostname)-$(date +%Y%m%d%H%M%S).md"

mkdir -p "$HANDOFF_DIR"
cat > "$HANDOFF_FILE" << 'EOF'
# Handoff: [Brief Title]

**From:** {system_name}
**Date:** {timestamp}
**Priority:** {LOW|MEDIUM|HIGH}

## SQL to Execute

```sql
INSERT INTO knowledge_base (category, title, content, tags, source_agent)
VALUES ('category', 'Title', 'Content...', 'tags', 'agent');
```

## Context

{Why this entry matters, any additional context}

---

**Delete this file after processing.**
EOF
```

### Process Handoffs

Systems with better connectivity should check for handoffs:

```bash
HANDOFF_DIR="${WORKLOG_DB_PATH%/*}/handoffs"

for file in "$HANDOFF_DIR"/*.md; do
  [ -f "$file" ] || continue

  echo "Processing: $file"
  # Extract SQL between ```sql and ``` markers
  # Execute SQL
  # Delete handoff file on success
done
```

## Mount Configuration

### Linux (CIFS/SMB)

```bash
# /etc/fstab entry
//server/share /mnt/mount cifs credentials=/home/user/.smbcreds,uid=1000,gid=1000,file_mode=0664,dir_mode=0775 0 0

# Manual mount
sudo mount -t cifs //server/share /mnt/mount -o username=user,uid=1000,gid=1000
```

### macOS (SMB)

```bash
# Manual mount
mount -t smbfs //user@server/share /Volumes/mount

# Via Finder: Cmd+K, smb://server/share
```

### Permissions

Directory needs write access for journal file:

```
drwxrwsr-x (2775) user:group /path/to/db/
-rw-rw-r-- (664)  user:group worklog.db
```

## Troubleshooting

### "database is locked"

**Cause:** Another process has write lock
**Solution:** Retry with delays (handled automatically)

**If persistent:**
```bash
# Check for connections
lsof /path/to/worklog.db

# On Linux, check NFS locks
cat /proc/locks | grep worklog
```

### "unable to open database file"

**Cause:** Mount not available or permissions issue

**Check mount:**
```bash
mount | grep mount_point
df -h /path/to/db
```

**Check permissions:**
```bash
ls -la /path/to/worklog.db
ls -la /path/to/db/directory/
```

### "disk I/O error"

**Cause:** Network interruption during write

**Solution:**
1. Check network connectivity
2. Remount if needed
3. Verify database integrity: `sqlite3 db.db "PRAGMA integrity_check;"`

### "readonly database"

**Cause:** Directory not writable (journal file needs write access)

**Solution:**
```bash
chmod 775 /path/to/db/directory/
# Or check mount options include write permission
```

## Best Practices

1. **Read operations are always safe** - No locking issues
2. **Batch writes when possible** - Fewer lock operations
3. **Use transactions for multiple inserts** - Single lock
4. **Check connectivity before long operations** - `/worklog-status`
5. **Keep handoff directory monitored** - Process promptly

## Multi-System Coordination

### Identify Active Systems

```sql
SELECT DISTINCT agent, MAX(timestamp) as last_seen
FROM entries
WHERE timestamp > datetime('now', '-24 hours')
GROUP BY agent;
```

### Flag Entries for Other Systems

Use tags to direct attention:

```sql
INSERT INTO entries (agent, task_type, title, tags)
VALUES ('system-a', 'notification', 'Review needed',
        'for:system-b,priority:high');
```

Query for flagged entries:

```sql
SELECT * FROM entries
WHERE tags LIKE '%for:my-system%'
AND timestamp > datetime('now', '-7 days');
```
