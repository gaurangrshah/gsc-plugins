# Worklog - Cross-Session Knowledge Persistence

A Claude Code plugin for maintaining knowledge, context, and learnings across sessions using SQLite.

**Version:** 1.1.0

## Overview

Worklog provides persistent memory for Claude Code sessions. Store learnings, recall context, track work history, and maintain continuity across sessions and systems.

## Quick Start (5 minutes)

### 1. Install Plugin

Copy the `worklog/` folder to your Claude Code plugins directory:
```bash
cp -r worklog ~/.claude/plugins/local-plugins/
```

### 2. Initialize

Run in any Claude Code session:
```
/worklog-init
```

You'll be prompted to choose:
- **Profile:** Standard (recommended) - balanced integration
- **Location:** Local (default) - `~/.claude/worklog/worklog.db`

The command will:
1. Create a backup of your CLAUDE.md
2. Initialize the database
3. Add worklog section to CLAUDE.md
4. Show verification results
5. Ask for confirmation (rollback if declined)

### 3. Start Using

After init, you have access to:
- `memory-store` skill - Save learnings after tasks
- `memory-recall` skill - Query context at task start
- `/worklog-status` - Check connectivity

### Multi-System Setup (Optional)

**Primary system:**
```
/worklog-init
# Choose: shared location
# Provide network path (e.g., /mnt/nas/worklog.db)
```

**Secondary systems:**
```
/worklog-connect /path/to/shared/worklog.db
```

### System Path Reference

When using a shared NAS database, each system needs its own path to the same database:

| System | Shared DB Path |
|--------|----------------|
| atlas (Mac) | `/Volumes/dev-env/workspace/logs/worklog.db` |
| ubuntu-mini | `/mnt/nasdevenv/workspace/logs/worklog.db` |

> **Important:** On ubuntu-mini, `~/workspace/logs/` does NOT exist because `~/workspace` is mounted to a subdirectory. Always use `/mnt/nasdevenv/workspace/logs/` for the shared worklog.
>
> See: [WORKSPACE-ARCHITECTURE.md](/Volumes/dev-env/workspace/docs/WORKSPACE-ARCHITECTURE.md) for full path mapping.

## Profiles

| Profile | Tables | Boot Queries | Auto-Store | Best For |
|---------|--------|--------------|------------|----------|
| **Minimal** | 6 core | None | Manual | Occasional use |
| **Standard** (default) | 6 core | Light | Prompted | Daily use |
| **Full** | 10 (core + extended) | Aggressive | Auto | Multi-system teams |

### Minimal
- Core tables only
- Manual store/recall via skills
- No automatic queries
- ~20 lines added to CLAUDE.md

### Standard (Recommended)
- Core tables
- Boot queries for recent context
- Prompts to store learnings
- ~50 lines added to CLAUDE.md

### Full
- All 10 tables (core + extended: projects, components, reference_library)
- Aggressive boot queries (protocols, recent work, errors, issues)
- Auto-store task outcomes
- Network failure handling with retry + handoffs
- ~100 lines added to CLAUDE.md
- Optional: Add domain-agency.sql for clients/competitors tables

## Commands

| Command | Purpose |
|---------|---------|
| `/worklog-init` | Initialize database (primary system) |
| `/worklog-connect <path>` | Connect to shared database (secondary) |
| `/worklog-configure` | Change profile or settings |
| `/worklog-status` | Check connectivity and stats |

## Skills

| Skill | Purpose |
|-------|---------|
| `memory-store` | Store knowledge, entries, errors |
| `memory-recall` | Query context and history |
| `memory-sync` | Reconcile with local docs |

## Database Schema

### Core Tables (6)

| Table | Purpose |
|-------|---------|
| `entries` | Work history and activity logs |
| `knowledge_base` | Reusable learnings and protocols |
| `memories` | Working context and session state |
| `issues` | Issue tracking |
| `error_patterns` | Error signatures and resolutions |
| `research` | External research items |

### Extended Tables (4) - Full Profile Only

| Table | Purpose |
|-------|---------|
| `projects` | Project registry |
| `component_registry` | Agents, skills, commands |
| `component_deployments` | Per-system deployments |
| `reference_library` | Research assets |

### Domain Extension: Agency (2) - Optional Add-on

| Table | Purpose |
|-------|---------|
| `clients` | Client entities (PII-safe) |
| `competitors` | Competitor profiles |

Install with: `sqlite3 $WORKLOG_DB_PATH < schema/domain-agency.sql`

## Configuration

Settings stored in `~/.claude/worklog.local.md`:

```yaml
---
profile: standard
db_path: ~/.claude/worklog/worklog.db
mode: local
system_name: my-system
---
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WORKLOG_DB_PATH` | `~/.claude/worklog/worklog.db` | Database location |
| `WORKLOG_PROFILE` | `standard` | Integration level |
| `WORKLOG_MODE` | `local` | `local` or `shared` |

## Network Usage

For shared databases over network mounts:

### Journal Mode

SQLite requires DELETE journal mode (not WAL) for network shares:

```sql
PRAGMA journal_mode=DELETE;
```

This is set automatically during init.

### Retry Logic

Network writes may fail with "database is locked". Use retry:

```bash
for i in 1 2 3; do
  sqlite3 $DB_PATH "YOUR SQL" && break
  sleep $((5 + RANDOM % 6))
done
```

### Mount Commands

**macOS:**
```bash
mount -t smbfs //server/share /Volumes/mount
```

**Linux:**
```bash
sudo mount -t cifs //server/share /mnt/mount -o username=user,uid=1000
```

## Usage Examples

### Store a Learning

```bash
sqlite3 ~/.claude/worklog/worklog.db "INSERT INTO knowledge_base
(category, title, content, tags, source_agent) VALUES
('development', 'React memo pattern',
'Use React.memo for expensive pure components...',
'react,performance,patterns', 'claude');"
```

### Query Knowledge

```bash
sqlite3 ~/.claude/worklog/worklog.db \
  "SELECT title, content FROM knowledge_base WHERE tags LIKE '%react%';"
```

### Log Work

```bash
sqlite3 ~/.claude/worklog/worklog.db "INSERT INTO entries
(agent, task_type, title, outcome, tags) VALUES
('claude', 'development', 'Implemented auth flow',
'JWT auth with refresh tokens', 'auth,security');"
```

### Check Error Patterns

```bash
sqlite3 ~/.claude/worklog/worklog.db \
  "SELECT resolution FROM error_patterns WHERE error_message LIKE '%ECONNREFUSED%';"
```

## Worklog Viewer (Web UI)

The plugin includes a browser-based SQLite viewer for exploring your worklog data.

**Location:** `worklog-viewer/index.html`

### Features

- Natural language search (multi-term filtering)
- Tag filtering (click tags to filter)
- Dark/Light theme with persistence
- Database caching via IndexedDB
- Custom SQL queries (Ctrl+Enter)
- CSV export
- Auto table discovery

### Usage

1. Open `worklog-viewer/index.html` in a browser
2. Click "Load Database" and select your `worklog.db` file
3. Use search, tag filters, and sort controls to explore
4. Double-click any row for full details

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Enter` | Run SQL query |
| `Escape` | Close modal |

## Plugin Structure

```
worklog/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── worklog-init.md
│   ├── worklog-connect.md
│   ├── worklog-configure.md
│   └── worklog-status.md
├── skills/
│   ├── memory-store/skill.md
│   ├── memory-recall/skill.md
│   └── memory-sync/skill.md
├── schema/
│   ├── core.sql
│   └── extended.sql
├── templates/
│   ├── minimal.md
│   ├── standard.md
│   └── full.md
├── docs/
│   └── network-protocol.md
├── worklog-viewer/
│   ├── index.html
│   └── README.md
└── README.md
```

## Troubleshooting

### "unable to open database file"

1. Check path exists: `ls -la $DB_PATH`
2. If network, verify mount: `mount | grep mount_point`
3. Check directory permissions

### "database is locked"

Normal for network databases. Retry handles this automatically.

### "readonly database"

Directory needs write permission (for journal file):
```bash
chmod 775 /path/to/db/directory
```

## Version History

### 1.1.0
- **Safety Protocol**: Backup-verify-restore flow for init/connect commands
- Automated verification checks before finalizing
- User confirmation step with rollback capability
- Timestamped backups retained for 7 days

### 1.0.1
- Schema split: extended.sql reduced to 4 tables
- New domain-agency.sql for clients/competitors (optional)

### 1.0.0
- Initial release
- 3 profile levels (minimal, standard, full)
- Core and extended schemas
- Network retry logic
- Multi-system support

## License

MIT
