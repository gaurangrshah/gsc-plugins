# Worklog - Cross-Session Knowledge Persistence

A Claude Code plugin for maintaining knowledge, context, and learnings across sessions using SQLite.

**Version:** 1.5.0

## Overview

Worklog provides persistent memory for Claude Code sessions. Store learnings, recall context, track work history, and maintain continuity across sessions and systems.

## Standalone & Integration

### Works 100% Standalone

Worklog is fully self-contained. **No other plugins required.**

```bash
# This works perfectly with ONLY worklog installed:
/worklog-init
# Use memory-store skill to save learnings
# Use memory-recall skill to query context
```

All skills work. All hooks work. All commands work. No errors or warnings about missing plugins.

### How Worklog Interacts with Other Plugins

Worklog provides **background context** for all sessions via hooks—it doesn't need to know about other plugins specifically.

#### Hooks Fire for All Sessions

When you use WebGen, AppGen, TaskFlow, or any Claude Code session:

| Hook | When | What Happens |
|------|------|--------------|
| SessionStart | Conversation begins | Loads recent context from worklog DB |
| SessionStop | Conversation ends | Captures learnings, logs work |

**The hooks don't care which plugin is active**—they provide general-purpose context and learning capture.

#### Example: WebGen + Worklog

```
User: /webgen fintech landing page

[SessionStart hook fires]
→ Loads recent work context from worklog DB
→ Agent sees: "Recent work: Implemented auth system yesterday"

[WebGen runs its workflow]
→ Generates landing page across 5 checkpoints

[SessionStop hook fires]
→ Prompts: "Session had significant activity. Store learnings?"
→ If aggressive mode: Auto-extracts design patterns to knowledge_base
```

#### Docs Plugin Integration (Bidirectional)

When both worklog and docs plugins are installed, they form a **bidirectional knowledge flow**:

```
docs-manager                    memory-sync
     ↓                              ↑
Stores learnings TO worklog    Promotes FROM worklog to docs
     ↓                              ↑
     └──────── worklog.db ──────────┘
```

| Direction | What Happens |
|-----------|--------------|
| **Docs → Worklog** | docs-manager stores learnings, decisions, and work entries to worklog.db |
| **Worklog → Docs** | memory-sync promotes valuable entries back to docs with proper frontmatter |

**Configuration for docs integration:**

```bash
# Set in both plugins for full integration
export WORKLOG_DB="/path/to/worklog.db"
export DOCS_ROOT="~/docs"
export KNOWLEDGE_BASE="~/.claude/knowledge"
```

When `$DOCS_ROOT` is set, memory-sync:
- Detects docs plugin and enables enhanced mode
- Creates files with proper YAML frontmatter
- Validates promoted files against docs standards
- Uses consistent type mapping (decisions → `type: decision`, etc.)

#### Other Plugin Integrations

| Integration | Status | Behavior |
|-------------|--------|----------|
| WebGen → Worklog | Passive (hooks only) | SessionStart/Stop hooks fire during generation |
| AppGen → Worklog | Passive (hooks only) | SessionStart/Stop hooks fire during generation |
| TaskFlow → Worklog | Passive (hooks only) | SessionStart/Stop hooks fire during task work |
| **Docs → Worklog** | **Active** | docs-manager stores to worklog.db |
| **Worklog → Docs** | **Active** | memory-sync promotes with frontmatter |

**The hooks provide value regardless**—any session benefits from context loading and learning capture.

## Quick Start (5 minutes)

### 1. Install Plugin

**Option A: Marketplace (Recommended)**
```bash
# Add the marketplace (if not already added)
claude plugin marketplace add https://github.com/gaurangrshah/gsc-plugins.git

# Install the plugin
claude plugin install worklog@gsc-plugins
```

**Option B: Manual Installation**
```bash
# Clone the repo
git clone https://github.com/gaurangrshah/gsc-plugins.git

# Copy to local-plugins
cp -r gsc-plugins/plugins/worklog ~/.claude/plugins/local-plugins/

# Restart Claude Code to activate
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

### Multi-System Path Reference (Advanced)

When using a shared database across multiple systems, each system needs its own mount path to the same database file. Example configurations:

| Platform | Example Shared DB Path |
|----------|------------------------|
| macOS | `/Volumes/share-name/path/to/worklog.db` |
| Linux | `/mnt/share-name/path/to/worklog.db` |
| Windows | `\\server\share\path\to\worklog.db` |

> **Note:** Network mount paths vary by system. Ensure each system can access the shared location before configuring.

## Profiles

| Profile | Tables | Default Hook Mode | Best For |
|---------|--------|-------------------|----------|
| **Minimal** | 6 core | remind | Occasional use |
| **Standard** (default) | 6 core | light | Daily use |
| **Full** | 10 (core + extended) | full | Multi-system teams |

## Hook Modes (Automation Levels)

Hooks automatically load context at session start and capture learnings at session end.

| Mode | Session Start | Session End | Best For |
|------|---------------|-------------|----------|
| **off** | Nothing | Nothing | Full manual control |
| **remind** | Reminder only | Suggest storing | Minimal overhead |
| **light** | Summary index (~150-300 tokens) | Prompt to log | Balanced automation |
| **full** | Detailed index (~300-500 tokens) | Auto-log compressed summary | Comprehensive tracking |
| **aggressive** | Index + critical auto-fetch | Auto-extract all learnings | Power users, shared DBs |

**Hook mode is independent of profile** - you can mix any profile with any hook mode.

### Hook Benefits

- **No more forgetting to log**: Hooks capture work automatically
- **Context always available**: Start each session with relevant history
- **Learning compounds**: Knowledge extracted and stored without manual effort
- **Background operation**: Hooks run without blocking your work
- **Token efficient**: Progressive disclosure reduces context bloat by 60-70%

### Progressive Disclosure (SessionStart)

Instead of dumping all context at once, hooks now inject a **summary index** first:

| Layer | What | When | Token Cost |
|-------|------|------|------------|
| **1. Index** | Summary of available context | Always (SessionStart) | ~100-300 tokens |
| **2. Details** | Full content for selected items | On-demand (memory-recall) | ~500-2000 tokens |
| **3. Source** | Original entries/queries | Explicit request | Variable |

**Example output (light mode):**
```
<worklog-context mode="light" disclosure="index">
## Available Context

| Category | Count | Est. Tokens | Top Items |
|----------|-------|-------------|-----------|
| Recent Work (24h) | 3 | ~450 | Auth system, API refactor |
| Active Memories | 5 | ~1000 | ctx_ubuntu_session, ... |

**To fetch full details:** Use `memory-recall` skill with category filter.
</worklog-context>
```

### AI Compression (SessionStop)

Sessions are compressed into semantic learnings, not raw transcripts:

| Raw Data | Compressed Output | Storage |
|----------|-------------------|---------|
| Full conversation (10,000+ tokens) | 1-2 sentence summary (~100 tokens) | entries.outcome |
| Debugging steps | Root cause + resolution | error_patterns |
| Decisions discussed | Decision + rationale | knowledge_base |
| Patterns observed | Pattern + when to apply | knowledge_base |

**Aggressive mode extracts:**
- Decisions (choice, rationale, alternatives)
- Patterns (description, when to use, examples)
- Errors (signature, root cause, resolution, prevention)
- Gotchas (wrong approach, right approach, context)

### PostToolUse Hook (Optional)

Automatically capture significant file changes during sessions. **OFF by default.**

Enable in `~/.claude/worklog.local.md`:
```yaml
---
capture_observations: true          # Enable PostToolUse hook
capture_filter: significant         # all | significant | decisions-only
capture_files: ["*.md", "*.ts", "*.py", "*.json"]
capture_exclude: ["node_modules/*", "*.lock"]
---
```

| Capture Mode | What Gets Captured | Recommended For |
|--------------|-------------------|-----------------|
| `off` (default) | Nothing | Most users |
| `significant` | Config files, schemas, docs, major code changes | Power users |
| `decisions-only` | Only explicit decision markers in changes | Minimal overhead |
| `all` | Every Write/Edit to matching files | Debug/audit only |

Observations are stored to `memories` table with `status='staging'` for review at session end.

### Minimal
- Core tables only (6 tables)
- ~20 lines added to CLAUDE.md
- Default hook mode: `remind`

### Standard (Recommended)
- Core tables (6 tables)
- ~50 lines added to CLAUDE.md
- Default hook mode: `light`

### Full
- All 10 tables (core + extended: projects, components, reference_library)
- Network failure handling with retry + handoffs
- ~100 lines added to CLAUDE.md
- Default hook mode: `full`
- Optional: Add domain-agency.sql for clients/competitors tables

## Commands

| Command | Purpose |
|---------|---------|
| `/worklog-init` | Initialize database (primary system) |
| `/worklog-connect <path>` | Connect to shared database (secondary) |
| `/worklog-configure` | Change profile or settings |
| `/worklog-setup-mcp` | Set up Python environment for MCP server |
| `/worklog-status` | Check connectivity and stats |

## Skills

| Skill | Purpose |
|-------|---------|
| `memory-store` | Store knowledge, entries, errors |
| `memory-recall` | Query context and history |
| `memory-sync` | Reconcile with local docs |

## MCP Server (Programmatic Access)

**New in v1.4.0:** The worklog plugin includes an MCP server for direct tool access.

### MCP Server Setup

The MCP server requires Python 3.10+ and includes cross-platform setup scripts.

**Option A: Use the Setup Command (Recommended)**

Run in Claude Code:
```
/worklog-setup-mcp
```

This command:
1. Detects Python using intelligent priority (pyenv → mise → Homebrew → system)
2. Creates an isolated virtual environment
3. Installs MCP dependencies
4. Configures `.mcp.json` automatically

**Option B: Run Setup Script Directly**

```bash
# Navigate to plugin directory
cd /path/to/gsc-plugins/plugins/worklog

# Run the setup script
./scripts/setup-mcp-venv.sh

# For custom venv location:
./scripts/setup-mcp-venv.sh --venv-path ~/.local/share/worklog-mcp-venv
```

**Option C: Manual Installation**

```bash
# Navigate to the MCP server directory
cd ~/.claude/plugins/marketplaces/gsc-plugins/worklog/mcp

# Create venv with your preferred Python 3.10+
python3 -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .

# Verify installation
python -m worklog_mcp --help
```

### Python Detection Priority

The setup scripts check for Python in this order:

| Priority | Source | Why |
|----------|--------|-----|
| 1 | pyenv | Respects explicit user choice |
| 2 | Homebrew (macOS) | Platform standard, very common |
| 3 | mise | Polyglot version manager |
| 4 | System Python | Last resort if ≥3.10 |

If no suitable Python is found, you'll get platform-specific recommendations:
- **macOS:** `brew install python@3.12`
- **Linux (apt):** `sudo apt-get install python3.12 python3.12-venv`
- **Linux (other):** `mise use python@3.12`

### Verify MCP Server

After setup, restart Claude Code and verify:
```bash
claude mcp list
# Should show: worklog (11 tools)
```

Once installed, Claude Code automatically detects the MCP server via the plugin's `.mcp.json` configuration.

### When to Use Each Approach

| Approach | Best For |
|----------|----------|
| **Skills** | Human-guided workflows with context and validation |
| **Commands** | Configuration and status checks |
| **MCP Tools** | Programmatic access, automation, agent-to-agent |

### Available MCP Tools

When the MCP server is installed and the plugin is enabled, these tools are available as `mcp__worklog__<tool>`:

| Tool | Description |
|------|-------------|
| `query_table` | Query any table with filtering, pagination |
| `search_knowledge` | Full-text search across tables |
| `recall_context` | Smart context retrieval for agent sessions |
| `get_knowledge_entry` | Get KB entry by ID |
| `get_memory` | Get memory by key |
| `store_memory` | Store new memories |
| `update_memory` | Update existing memories |
| `log_entry` | Log work entries |
| `store_knowledge` | Add to knowledge base |
| `list_tables` | List tables with counts |
| `get_recent_entries` | Recent work by agent |

### MCP Usage Examples

```python
# Load context at task start
mcp__worklog__recall_context(topic="deployment", min_importance=5)

# Store a learning
mcp__worklog__store_memory(
    key="fact_agent_20251217_learning",
    content="Important discovery...",
    memory_type="fact",
    importance=7
)

# Search across all knowledge
mcp__worklog__search_knowledge(query="SSH", limit=10)

# Log completed work
mcp__worklog__log_entry(
    title="Deployed API",
    task_type="deployment",
    outcome="Success"
)
```

### MCP Server Development

The MCP server source is in `mcp/`:

```bash
cd plugins/worklog/mcp
pip install -e ".[dev]"     # Install
python -m worklog_mcp       # Run directly
pytest -v                   # Run tests
```

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

### Location (varies by installation method)

| Installation Method | Viewer Location |
|---------------------|-----------------|
| **Marketplace** | `~/.claude/plugins/marketplaces/gsc-plugins/worklog/worklog-viewer/index.html` |
| **Local Plugin** | `~/.claude/plugins/local-plugins/worklog/worklog-viewer/index.html` |
| **From Source** | `<repo>/plugins/worklog/worklog-viewer/index.html` |

**Tip:** On macOS, the `~/.claude` folder is hidden. Use Finder → Go → Go to Folder (⇧⌘G) and enter the path above.

### Features

- Natural language search (multi-term filtering)
- Tag filtering (click tags to filter)
- Dark/Light theme with persistence
- Database caching via IndexedDB
- Custom SQL queries (Ctrl+Enter)
- CSV export
- Auto table discovery

### Usage

1. Navigate to the viewer location based on your installation method (see table above)
2. Open `index.html` in a browser (drag-and-drop or right-click → Open With)
3. Click "Load Database" and select your `worklog.db` file
4. Use search, tag filters, and sort controls to explore
5. Double-click any row for full details

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
│   ├── worklog-setup-mcp.md  # Cross-platform MCP setup (v1.5.0+)
│   └── worklog-status.md
├── hooks/
│   ├── session-start.md      # Auto-load context (progressive disclosure)
│   ├── session-stop.md       # Auto-capture learnings (AI compression)
│   └── post-tool-use.md      # Optional: capture significant file changes
├── skills/
│   ├── memory-store/skill.md
│   ├── memory-recall/skill.md
│   └── memory-sync/skill.md
├── scripts/                  # Setup utilities (v1.5.0+)
│   ├── detect-python-env.sh  # Cross-platform Python detection
│   └── setup-mcp-venv.sh     # Automated venv creation
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
├── mcp/                      # MCP server (v1.4.0+)
│   ├── src/worklog_mcp/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── config.py
│   │   └── server.py
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
├── .mcp.json                 # MCP server config
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

### 1.5.0
- **Cross-Platform Python Detection**: New `detect-python-env.sh` script with intelligent priority (pyenv → mise → Homebrew → system)
- **Automated MCP Setup**: New `/worklog-setup-mcp` command and `setup-mcp-venv.sh` script
- **Platform-Aware Recommendations**: Suggests appropriate Python installation method per platform
- **Lower Python Requirement**: Now requires Python 3.10+ (was 3.11+)
- **Scripts Directory**: New `scripts/` folder for setup utilities

### 1.4.0
- **MCP Server**: Added FastMCP-based MCP server for programmatic database access
- **11 MCP Tools**: query_table, search_knowledge, recall_context, store_memory, update_memory, log_entry, store_knowledge, get_knowledge_entry, get_memory, list_tables, get_recent_entries
- **Dual Access**: Skills for guided workflows, MCP for automation
- **Auto-Detection**: Database path auto-detected by hostname

### 1.3.0
- **Progressive Disclosure (SessionStart)**: Index-first injection reduces context bloat by 60-70%
- **AI Compression (SessionStop)**: Semantic extraction of learnings vs raw transcript logging
- **PostToolUse Hook**: Optional auto-capture of significant file changes (off by default)
- **Deep Extraction (Aggressive)**: Automatically extracts decisions, patterns, errors, gotchas
- **Token Efficiency**: Typical injection reduced from ~1500-3000 tokens to ~300-500 tokens

### 1.2.0
- **Hooks for Automation**: SessionStart and Stop hooks for automatic context loading and learning capture
- **Hook Modes**: off, remind, light, full, aggressive - independent of profile selection
- **Enhanced Init Flow**: Now prompts for hook mode during `/worklog-init`
- **Updated Templates**: Templates now reflect hook behavior and settings
- **Viewer Documentation**: Clarified installation-specific paths for worklog-viewer

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
