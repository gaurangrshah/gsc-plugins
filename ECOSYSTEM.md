# GSC Plugins Ecosystem

A unified ecosystem of Claude Code plugins that work independently or together.

## Quick Start

```bash
# Add the marketplace
claude plugin marketplace add https://github.com/gaurangrshah/gsc-plugins.git

# Install any plugin (each works standalone)
claude plugin install appgen@gsc-plugins    # Full-stack app generation
claude plugin install webgen@gsc-plugins    # Website generation
claude plugin install taskflow@gsc-plugins  # Task management
claude plugin install docs@gsc-plugins      # Documentation management
claude plugin install worklog@gsc-plugins   # Cross-session knowledge
```

## Design Principles

### 1. Standalone First

Every plugin works 100% independently. No required dependencies.

```
# This works perfectly with ONLY appgen installed:
/appgen "task management app"
```

### 2. Enhanced Together

When multiple plugins are installed, they integrate automatically:

| Combination | Integration |
|-------------|-------------|
| appgen + worklog | Learnings stored across projects |
| appgen + taskflow | Tasks tracked during development |
| docs + worklog | Bidirectional knowledge flow |
| webgen + worklog | Design patterns shared |

### 3. Unified Configuration

All plugins use the same config pattern:

```
~/.gsc-plugins/
├── appgen.local.md     # AppGen global config
├── webgen.local.md     # WebGen global config
├── taskflow.local.md   # TaskFlow global config
├── docs.local.md       # Docs global config
├── worklog.local.md    # Worklog global config
└── knowledge/          # Shared knowledge base
```

**Config format:** `.local.md` with YAML frontmatter

```yaml
---
knowledge_storage: sqlite
default_framework: next
# ... plugin-specific settings
---

# Plugin Configuration

Human-readable notes and documentation.
```

**Hierarchy:**
1. Project-specific: `./.{plugin}.local.md` (overrides global)
2. Global: `~/.gsc-plugins/{plugin}.local.md` (user defaults)
3. Built-in defaults (fallback)

## Plugin Overview

### AppGen (v2.0)

Generate full-stack applications from natural language.

```bash
/appgen "task management app with authentication"
```

**Features:**
- 8-checkpoint workflow with quality gates
- Progressive tech stack selection
- Automatic code review
- Database, API, frontend generation

**Storage Options:**
- SQLite (default) - local, structured queries
- Markdown - simple files, git-friendly
- Worklog - cross-project sharing

---

### WebGen (v2.0)

Generate websites and components from natural language.

```bash
/webgen "fintech landing page with pricing section"
```

**Features:**
- 5-checkpoint workflow
- Reference asset extraction
- Competitive analysis
- Responsive implementation

**Storage Options:**
- SQLite (default)
- Markdown
- Worklog

---

### TaskFlow (v2.0)

Task management with PRD parsing and multi-tag contexts.

```bash
/task-init                    # Initialize in project
/task-parse docs/PRD.md       # Parse PRD to tasks
/task next                    # Get next task
```

**Features:**
- Parse PRDs into structured tasks
- Multi-tag support for parallel contexts
- Gitea kanban sync
- Cross-session task tracking

**Storage:**
- `.tasks/` directory per project
- Backend abstraction (SQLite planned)

---

### Docs (v1.1)

Documentation management and validation.

```bash
/docs-init                    # Set up docs structure
/docs-reconcile journal.md    # Reconcile journal
/docs-validate                # Run validation
```

**Features:**
- Single source of truth philosophy
- Journal reconciliation workflow
- Frontmatter validation
- Worklog integration for learnings

**Storage:**
- `$DOCS_ROOT` directory (default: ~/docs)
- Knowledge base for learnings

---

### Worklog (v1.7)

Cross-session knowledge persistence.

```bash
/worklog-init                 # Initialize database
/worklog-status              # Check connectivity
```

**Features:**
- SQLite or PostgreSQL backend
- MCP server for programmatic access
- SessionStart/Stop hooks
- Plugin discovery and knowledge import

**Storage:**
- SQLite: `~/.claude/worklog/worklog.db`
- PostgreSQL: via DATABASE_URL

## Integration Patterns

### Knowledge Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  AppGen  │───▶│ Worklog  │◀───│  WebGen  │
└──────────┘    └────┬─────┘    └──────────┘
                     │
                     ▼
              ┌──────────┐
              │   Docs   │
              └──────────┘
```

- AppGen/WebGen store learnings → Worklog
- Worklog syncs with → Docs (via memory-sync)
- Docs stores knowledge → Worklog

### Task Tracking

```
┌──────────┐    ┌──────────┐
│  AppGen  │───▶│ TaskFlow │
│  WebGen  │    │          │
└──────────┘    └────┬─────┘
                     │
                     ▼
              ┌──────────┐
              │  Gitea   │
              │  Kanban  │
              └──────────┘
```

- AppGen/WebGen detect TaskFlow
- Suggest tracking project tasks
- TaskFlow syncs to Gitea boards

### Progressive Discovery

When you run `/appgen` or `/webgen`:

1. **First-run:** Prompts for knowledge storage preference
2. **Plugin detection:** Checks for TaskFlow, Worklog
3. **Suggestions:** Offers to install complementary plugins
4. **Auto-integration:** Installed plugins work together automatically

## First-Run Experience

### Single Plugin Install

```bash
claude plugin install appgen@gsc-plugins
/appgen "todo app"

# First run prompts:
# 1. Knowledge storage? (SQLite/Markdown/Worklog)
# 2. Default preferences? (Framework, DB, Auth)
# 3. TaskFlow available? (Offer install)
# 4. Worklog available? (Offer install if needed)
```

### Full Ecosystem Install

```bash
# Install all plugins
claude plugin install appgen@gsc-plugins
claude plugin install webgen@gsc-plugins
claude plugin install taskflow@gsc-plugins
claude plugin install docs@gsc-plugins
claude plugin install worklog@gsc-plugins

# Initialize worklog first (discovers other plugins)
/worklog-init
# → Detects: appgen, webgen, taskflow, docs
# → Offers knowledge import

# Use any plugin - all integrate automatically
/appgen "my app"
# → Stores learnings to worklog
# → Can track tasks with taskflow
```

## Configuration Reference

### AppGen (`~/.gsc-plugins/appgen.local.md`)

```yaml
---
knowledge_storage: sqlite|markdown|worklog
knowledge_path: ~/.gsc-plugins/knowledge
default_framework: null  # or next, remix, astro
default_database: null   # or postgresql, sqlite
default_auth: null       # or authjs, clerk
---
```

### WebGen (`~/.gsc-plugins/webgen.local.md`)

```yaml
---
knowledge_storage: sqlite|markdown|worklog
knowledge_path: ~/.gsc-plugins/knowledge
default_framework: null  # or react-vite, next, astro
default_styling: tailwind
---
```

### TaskFlow (`~/.gsc-plugins/taskflow.local.md`)

```yaml
---
version: "2.0"
backend: json  # json or sqlite
defaults:
  checkpoints: [parse, execute, complete]
  syncTodoWrite: true
gitea:
  enabled: false
  repo: null
---
```

### Docs (`~/.gsc-plugins/docs.local.md`)

```yaml
---
docs_root: ~/docs
main_guide: ~/docs/guide.md
knowledge_base: ~/.gsc-plugins/knowledge
worklog:
  enabled: true
  use_mcp: true
---
```

### Worklog (`~/.gsc-plugins/worklog.local.md`)

```yaml
---
profile: standard
backend: sqlite|postgresql
db_path: ~/.claude/worklog/worklog.db
hook_mode: light
system_name: my-system
---
```

## Version Compatibility

| Plugin | Version | Config Format | Ecosystem |
|--------|---------|---------------|-----------|
| appgen | 2.0 | .local.md | v2 |
| webgen | 2.0 | .local.md | v2 |
| taskflow | 2.0 | .local.md | v2 |
| docs | 1.1 | .local.md | v2 |
| worklog | 1.7 | .local.md | v2 |

All v2 ecosystem plugins use:
- `~/.gsc-plugins/` for configuration
- `.local.md` with YAML frontmatter
- Progressive discovery for complementary plugins
- SQLite default with worklog option

## Troubleshooting

### Plugin not detecting others

Check plugin directories:
```bash
ls ~/.claude/plugins/local-plugins/
ls ~/.claude/plugins/marketplaces/gsc-plugins/
```

### Config not loading

Check config exists:
```bash
cat ~/.gsc-plugins/{plugin}.local.md
```

### Worklog connection issues

```bash
/worklog-status
```

### Knowledge not syncing

Verify storage mode matches:
```bash
grep "knowledge_storage" ~/.gsc-plugins/*.local.md
```

## License

MIT
