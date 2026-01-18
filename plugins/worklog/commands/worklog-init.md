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

### Step 1: Check Existing Configuration

```python
# Check for existing config
config_path = os.path.expanduser("~/.gsc-plugins/worklog.local.md")

if os.path.exists(config_path):
    print("Worklog already configured.")
    print(f"Config: {config_path}")

    response = AskUserQuestion({
        "question": "What would you like to do?",
        "header": "Config exists",
        "options": [
            {"label": "Keep existing", "description": "Exit without changes"},
            {"label": "Reconfigure", "description": "Update configuration"},
            {"label": "View config", "description": "Show current settings"}
        ]
    })

    if response == "Keep existing":
        return
    elif response == "View config":
        showConfig(config_path)
        return
```

### Step 2: Choose Database Backend

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

#### Step 3a: Choose Integration Profile

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

#### Step 4a: Create Database

```bash
# Create directory
mkdir -p ~/.claude/worklog

# Database will be auto-created by the MCP server on first use
# Or create manually with schema:
sqlite3 ~/.claude/worklog/worklog.db < {plugin_root}/schema/core.sql

# Load seed data (tag taxonomy, topics, bootstrap knowledge)
{plugin_root}/seed/run-seeds.sh sqlite ~/.claude/worklog/worklog.db
```

---

### If PostgreSQL Selected:

#### Step 3b: Choose Integration Profile

Same options as SQLite (MINIMAL, STANDARD, FULL)

#### Step 4b: Configure Connection

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

#### Step 5b: Test Connection & Load Schema

```bash
# Test connection
psql -c "SELECT 1;"

# Load schema (if not already created)
psql -f {plugin_root}/schema/core.sql

# Load seed data (tag taxonomy, topics, bootstrap knowledge)
{plugin_root}/seed/run-seeds.sh postgresql
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

echo $BACKUP_DIR > ~/.claude/.worklog-backup-path
```

### Step 6: Create Plugin Configuration

Create `~/.gsc-plugins/worklog.local.md`:

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

### Step 8: Plugin Discovery

**Detect other GSC plugins and offer integration:**

```python
# Scan for other GSC plugin configs
gsc_plugins_dir = os.path.expanduser("~/.gsc-plugins")
plugin_configs = glob.glob(f"{gsc_plugins_dir}/*.local.md")

# Check for known plugins
detected_plugins = []
for config in plugin_configs:
    name = os.path.basename(config).replace(".local.md", "")
    if name != "worklog":
        detected_plugins.append(name)

# Check for plugin directories
plugin_dirs = [
    "~/.claude/plugins/local-plugins",
    "~/.claude/plugins/marketplaces/gsc-plugins"
]

for base_dir in plugin_dirs:
    expanded = os.path.expanduser(base_dir)
    if os.path.exists(expanded):
        for item in os.listdir(expanded):
            if item in ["appgen", "webgen", "taskflow", "docs"]:
                if item not in detected_plugins:
                    detected_plugins.append(item)

# Report discovered plugins
if detected_plugins:
    print(f"\nDiscovered GSC plugins: {', '.join(detected_plugins)}")
    print("\nWorklog can provide cross-session context for these plugins:")
    print("- SessionStart hooks inject recent context")
    print("- SessionStop hooks capture learnings")
    print("- Knowledge base shared across all plugins")
```

**Scan for existing knowledge to import:**

```python
# Check for markdown knowledge directories
knowledge_sources = []

# AppGen knowledge
appgen_kb = os.path.expanduser("~/.gsc-plugins/knowledge")
if os.path.exists(appgen_kb):
    md_files = glob.glob(f"{appgen_kb}/**/*.md", recursive=True)
    if md_files:
        knowledge_sources.append({
            "source": "appgen/webgen",
            "type": "markdown",
            "path": appgen_kb,
            "count": len(md_files)
        })

# Docs knowledge base
docs_config = loadLocalMdConfig("~/.gsc-plugins/docs.local.md")
if docs_config and docs_config.get("knowledge_base"):
    kb_path = os.path.expanduser(docs_config["knowledge_base"])
    if os.path.exists(kb_path):
        md_files = glob.glob(f"{kb_path}/**/*.md", recursive=True)
        if md_files:
            knowledge_sources.append({
                "source": "docs",
                "type": "markdown",
                "path": kb_path,
                "count": len(md_files)
            })

# Offer import if knowledge found
if knowledge_sources:
    total_files = sum(k["count"] for k in knowledge_sources)
    print(f"\nFound {total_files} knowledge files from other plugins:")
    for ks in knowledge_sources:
        print(f"  - {ks['source']}: {ks['count']} files at {ks['path']}")

    response = AskUserQuestion({
        "question": "Import existing knowledge into worklog?",
        "header": "Knowledge Import",
        "options": [
            {"label": "Yes (Recommended)", "description": "Import and centralize all knowledge"},
            {"label": "No", "description": "Start fresh, keep separate"}
        ]
    })

    if "Yes" in response:
        importKnowledge(knowledge_sources)
```

### Step 9: Import Knowledge (if requested)

```python
def importKnowledge(sources):
    """Import markdown knowledge files into worklog database."""
    imported = 0

    for source in sources:
        if source["type"] == "markdown":
            for md_file in glob.glob(f"{source['path']}/**/*.md", recursive=True):
                # Parse frontmatter
                with open(md_file, 'r') as f:
                    content = f.read()

                frontmatter, body = parseFrontmatter(content)

                # Map to knowledge_base entry
                title = frontmatter.get("title", os.path.basename(md_file))
                category = frontmatter.get("type", "general")
                tags = frontmatter.get("tags", source["source"])

                # Insert into worklog
                mcp__worklog__store_knowledge(
                    category=category,
                    title=title,
                    content=body,
                    tags=tags,
                    source_agent=f"import:{source['source']}"
                )
                imported += 1

    print(f"\nImported {imported} knowledge entries to worklog.")
    print("Original files preserved (non-destructive import).")
```

### Step 10: Run Verification

**SQLite Verification:**
```bash
DB=~/.claude/worklog/worklog.db
[ -f "$DB" ] && echo "Database: OK" || echo "Database: MISSING"
sqlite3 "$DB" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" && echo "Schema: OK"
sqlite3 "$DB" "SELECT COUNT(*) FROM tag_taxonomy;" && echo "Seed data: OK" || echo "Seed data: MISSING"
grep -q "WORKLOG_START" ~/.claude/CLAUDE.md && echo "CLAUDE.md: OK" || echo "CLAUDE.md: MISSING"
[ -f ~/.gsc-plugins/worklog.local.md ] && echo "Config: OK" || echo "Config: MISSING"
```

**PostgreSQL Verification:**
```bash
psql -c "SELECT 1;" && echo "Connection: OK" || echo "Connection: FAILED"
psql -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" && echo "Schema: OK"
psql -t -c "SELECT COUNT(*) FROM tag_taxonomy;" && echo "Seed data: OK" || echo "Seed data: MISSING"
grep -q "WORKLOG_START" ~/.claude/CLAUDE.md && echo "CLAUDE.md: OK" || echo "CLAUDE.md: MISSING"
[ -f ~/.gsc-plugins/worklog.local.md ] && echo "Config: OK" || echo "Config: MISSING"
```

### Step 11: User Confirmation

```
Installation complete!

Backend:  {sqlite|postgresql}
Profile:  {profile}
Hook:     {hook_mode}

Changes made:
- Created: ~/.gsc-plugins/worklog.local.md
- Updated: ~/.claude/CLAUDE.md
{If SQLite: - Created: ~/.claude/worklog/worklog.db}
- Loaded seed data (tag taxonomy, topics, bootstrap knowledge)
{If imported: - Imported {n} knowledge entries}

Keep these changes? (y/n)
```

**If YES:** Finalize installation
**If NO:** Rollback from backup

### Step 12: Provide Next Steps

```
Worklog initialized successfully!

Backend: {backend}
Profile: {profile}
{If plugins discovered:}
Integrates with: {detected_plugins}

Seed data loaded:
- Tag taxonomy for consistent tagging (k8s→kubernetes, pg→postgresql, etc.)
- Core topics for knowledge organization
- Quick start guide in knowledge base

Next steps:
- Run `search_knowledge("Quick Start")` to see the getting started guide
- Use `store_memory` to save learnings (tags auto-normalized)
- Use `recall_context` to query relevant context
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

**Import fails:**
- Original files are preserved
- Check file permissions
- Verify frontmatter format

**Seed data fails:**
- Schema must be created first
- Run `{plugin_root}/seed/run-seeds.sh` manually
- Check for unique constraint violations (safe to ignore - ON CONFLICT DO NOTHING)

## Rollback Command

```bash
BACKUP=$(ls -td ~/.claude/.worklog-backup-* 2>/dev/null | head -1)
if [ -n "$BACKUP" ]; then
  cp $BACKUP/CLAUDE.md ~/.claude/CLAUDE.md 2>/dev/null
  rm -f ~/.gsc-plugins/worklog.local.md
  echo "Restored from $BACKUP"
fi
```
