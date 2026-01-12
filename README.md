# GSC Plugins

A collection of Claude Code plugins for enhanced development workflows.

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [appgen](plugins/appgen/) | 2.0.0 | Full-stack applications and APIs from natural language |
| [webgen](plugins/webgen/) | 2.0.0 | Production-ready websites and landing pages from natural language |
| [taskflow](plugins/taskflow/) | 2.0.0 | Task management with PRD parsing and multi-tag contexts |
| [worklog](plugins/worklog/) | 1.7.0 | Cross-session knowledge persistence (SQLite/PostgreSQL) |
| [docs](plugins/docs/) | 1.1.0 | Documentation management and quality assurance |

> **Ecosystem v2:** All plugins now use unified `.local.md` configuration at `~/.gsc-plugins/`. See [ECOSYSTEM.md](ECOSYSTEM.md) for integration details.

## Installation

> **Note:** These plugins are indexed on [claude-plugins.dev](https://claude-plugins.dev) but are NOT available in the central `npx claude-plugins` registry. Use one of the methods below to install.

### Option 1: Add as Marketplace (Recommended)

From within Claude Code, run these commands:

**Step 1: Add the marketplace**
```
claude plugin marketplace add https://github.com/gaurangrshah/gsc-plugins.git
```

**Step 2: Install the plugins you want**
```
claude plugin install webgen@gsc-plugins
claude plugin install appgen@gsc-plugins
claude plugin install worklog@gsc-plugins
claude plugin install taskflow@gsc-plugins
claude plugin install docs@gsc-plugins
```

### Option 2: Slash Commands (Inside Claude Code)

If you're already in a Claude Code session:

```
/plugin marketplace add https://github.com/gaurangrshah/gsc-plugins.git
/plugin install webgen@gsc-plugins
```

### Option 3: Manual Installation

Clone and copy to your local plugins directory:

```bash
# Clone the repo
git clone https://github.com/gaurangrshah/gsc-plugins.git

# Copy desired plugins to your local-plugins directory
cp -r gsc-plugins/plugins/webgen ~/.claude/plugins/local-plugins/
cp -r gsc-plugins/plugins/appgen ~/.claude/plugins/local-plugins/
cp -r gsc-plugins/plugins/worklog ~/.claude/plugins/local-plugins/
cp -r gsc-plugins/plugins/taskflow ~/.claude/plugins/local-plugins/
cp -r gsc-plugins/plugins/docs ~/.claude/plugins/local-plugins/

# Restart Claude Code to pick up the new plugins
```

### What Doesn't Work

```bash
# This will NOT work - we're not in the central npx registry
npx claude-plugins install @gaurangrshah/gsc-plugins/webgen  # ❌
```

## Updating Plugins

To update an already installed plugin to the latest version:

### Via Marketplace (Recommended)

```bash
# Update marketplace index first
claude plugin marketplace update gsc-plugins

# Reinstall the plugin (--force overwrites existing)
claude plugin install worklog@gsc-plugins --force
```

### Uninstall/Reinstall

```bash
claude plugin uninstall worklog@gsc-plugins
claude plugin install worklog@gsc-plugins
```

### Manual Update

If you installed manually:

```bash
# Pull latest changes
cd ~/path/to/gsc-plugins
git pull

# Re-copy to local-plugins (overwrites existing)
cp -r plugins/worklog ~/.claude/plugins/local-plugins/

# Restart Claude Code to pick up changes
```

## Uninstalling

### Via Claude CLI (Marketplace Installations)

```bash
# Uninstall individual plugins
claude plugin uninstall webgen@gsc-plugins
claude plugin uninstall appgen@gsc-plugins
claude plugin uninstall worklog@gsc-plugins
claude plugin uninstall taskflow@gsc-plugins
claude plugin uninstall docs@gsc-plugins

# Remove the marketplace entirely (optional)
claude plugin marketplace remove gsc-plugins
```

### Via Slash Commands (Inside Claude Code)

```
/plugin uninstall webgen@gsc-plugins
/plugin uninstall appgen@gsc-plugins
```

### Manual Installations

If you installed manually to local-plugins:

```bash
# Remove specific plugins
rm -rf ~/.claude/plugins/local-plugins/webgen
rm -rf ~/.claude/plugins/local-plugins/appgen
rm -rf ~/.claude/plugins/local-plugins/worklog
rm -rf ~/.claude/plugins/local-plugins/taskflow
rm -rf ~/.claude/plugins/local-plugins/docs

# Restart Claude Code to apply changes
```

### Complete Cleanup

To remove everything (marketplace + all plugins):

```bash
# 1. Uninstall all plugins
claude plugin uninstall webgen@gsc-plugins
claude plugin uninstall appgen@gsc-plugins
claude plugin uninstall worklog@gsc-plugins
claude plugin uninstall taskflow@gsc-plugins
claude plugin uninstall docs@gsc-plugins

# 2. Remove marketplace
claude plugin marketplace remove gsc-plugins

# 3. Remove any manual installations
rm -rf ~/.claude/plugins/local-plugins/{webgen,appgen,worklog,taskflow,docs}

# 4. Restart Claude Code
```

**Note:** Uninstalling worklog does NOT delete your `worklog.db` database. Your knowledge and work history are preserved.

## When to Use What

Understanding which plugin to use for different scenarios:

| Need | Plugin | Why |
|------|--------|-----|
| **Build a website** | WebGen | 5-checkpoint workflow for landing pages, marketing sites |
| **Build an application** | AppGen | 8-phase workflow for full-stack apps with DB, API, auth |
| **Track tasks during development** | TaskFlow | PRD parsing, dependencies, next task recommendations |
| **Remember learnings across sessions** | Worklog | Persistent knowledge, context loading, learning capture |
| **Maintain documentation** | Docs | Single source of truth, validation, journal reconciliation |

### Complementary Usage

These plugins work together but serve distinct purposes:

```
┌─────────────────────────────────────────────────────────────────┐
│                     TYPICAL WORKFLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. /task-parse prd.md         → TaskFlow: Define WHAT to do   │
│                                                                  │
│  2. /task next                 → TaskFlow: Pick next task       │
│                                                                  │
│  3. /webgen or /appgen ...     → Generators: Do the WORK        │
│                                                                  │
│  4. [SessionStop hook]         → Worklog: Capture LEARNINGS     │
│                                                                  │
│  5. [Next session starts]      → Worklog: Restore CONTEXT       │
│                                                                  │
│  6. /task next                 → TaskFlow: Continue where       │
│                                  you left off                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

| Plugin | Manages | Persists |
|--------|---------|----------|
| **TaskFlow** | Work items (tasks, subtasks, dependencies) | Per-project in `.tasks/` |
| **Worklog** | Knowledge (learnings, patterns, errors, context) | Cross-project in `worklog.db` |
| **WebGen/AppGen** | Generation workflows | Project output folders |

**Key insight:** TaskFlow tracks **what you're doing**, Worklog remembers **what you learned**.

## Plugin Overview

### WebGen

Transform natural language descriptions into complete, production-ready web projects (landing pages, marketing sites).

**Features:**
- 5-checkpoint orchestrated workflow
- React, Next.js, Astro support
- Asset management (screenshot/design references)
- Optional TaskFlow integration
- **Git worktree support** for parallel development
- Built-in code review agent
- Design system skill
- Git feature branch workflow

**Quick Start:**
```
/webgen a modern landing page for a fitness app
```

**Dependencies:** Node.js 18+, pnpm/npm

[Full documentation →](plugins/webgen/README.md)

---

### AppGen

Generate full-stack applications and APIs from natural language descriptions.

**Features:**
- 8-phase workflow (requirements → database → API → implementation → deployment)
- Next.js App Router, API-only, Monorepo scaffolds
- Database design (Prisma/Drizzle)
- API design (REST, tRPC)
- Auth integration (Auth.js, Clerk, Lucia)
- **Git worktree support** for parallel development
- Testing setup (Vitest, Playwright)
- Deployment config (Docker, CI/CD)

**Quick Start:**
```
/appgen inventory management system for a warehouse
/appgen REST API for a blog with auth and comments
/appgen SaaS dashboard for subscription management
```

**Dependencies:** Node.js 18+, pnpm/npm, PostgreSQL (optional)

[Full documentation →](plugins/appgen/README.md)

---

### Worklog

Cross-session knowledge persistence with dual database backend support. Maintain context, learnings, and work history across Claude Code sessions.

**Features:**
- **Dual backend support:** SQLite (default, zero dependencies) or PostgreSQL (optional, for teams)
- 3 profile levels (minimal, standard, full)
- Memory store/recall/sync skills
- **MCP server for programmatic database access** (v1.4.0+)
- Session hooks for automatic context loading and learning capture
- Multi-system support with shared databases
- Error pattern tracking
- Auto-detection of backend from environment variables

**Quick Start:**
```
/worklog-init
```

**Dependencies:** None required (SQLite built-in). Optional: PostgreSQL server, Python 3.10+ (for MCP server)

[Full documentation →](plugins/worklog/README.md)

---

### TaskFlow

AI-powered task management system. Transform PRDs into structured, dependency-aware tasks.

**Features:**
- PRD parsing with automatic dependency detection
- Intelligent task recommendation
- Tag-based parallel work contexts
- Human-in-the-loop checkpoints
- TodoWrite integration
- Optional integration with WebGen/AppGen

**Quick Start:**
```
/task-init
/task-parse docs/PRD/my-feature.md
/task next
```

[Full documentation →](plugins/taskflow/README.md)

---

### Docs

Documentation management and quality assurance. Enforces single source of truth philosophy with validation.

**Features:**
- Single source of truth philosophy
- Journal reconciliation workflow
- Proactive validation checks
- Frontmatter compliance
- Worklog integration for persistence

**Quick Start:**
```
/docs-init
/docs-validate
/docs-reconcile /tmp/journal-notes.md
```

[Full documentation →](plugins/docs/README.md)

---

## Plugin Architecture

### Standalone by Design

**Every plugin works 100% independently.** Install one, two, or all five—each functions fully without the others.

| Installation | Status | Notes |
|--------------|--------|-------|
| webgen only | ✅ Full | All 5 checkpoints work |
| appgen only | ✅ Full | All 8 phases work |
| taskflow only | ✅ Full | Complete task management |
| worklog only | ✅ Full | All hooks + skills work |
| docs only | ✅ Full | All commands + skills work |
| Any combination | ✅ Full | Optional enhancements activate |

### How Plugins Detect Each Other

When plugins are installed together, they detect and offer integrations:

```
/webgen restaurant landing page

→ WebGen checks: Is TaskFlow installed?
→ If YES: "TaskFlow detected. Track this project with tasks? (y/n)"
→ If NO: Proceeds silently without task prompts
```

**No errors. No warnings. No degraded functionality.**

### Integration Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                     GSC Plugins Integration                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐         ┌──────────┐                             │
│   │  WebGen  │◄───────►│ TaskFlow │  Track generation phases    │
│   │  v1.6.0  │ opt-in  │  v1.1.0  │  as tasks with deps         │
│   └────┬─────┘         └────┬─────┘                             │
│        │                    │                                    │
│        │ (future)           │ (future)                          │
│        │                    │                                    │
│        ▼                    ▼                                    │
│   ┌──────────┐         ┌──────────┐                             │
│   │  Worklog │         │  Worklog │  Progressive disclosure +   │
│   │  v1.6.0  │         │  v1.6.0  │  AI compression             │
│   └──────────┘         └──────────┘                             │
│                                                                  │
│   ┌──────────┐         ┌──────────┐                             │
│   │  AppGen  │◄───────►│ TaskFlow │  Track app dev phases       │
│   │  v1.1.0  │ opt-in  │  v1.1.0  │  as tasks with deps         │
│   └────┬─────┘         └────┬─────┘                             │
│        │                    │                                    │
│        │ (future)           │ (future)                          │
│        ▼                    ▼                                    │
│   ┌──────────┐         ┌──────────┐                             │
│   │  Worklog │         │  Worklog │  Progressive disclosure +   │
│   │  v1.6.0  │         │  v1.6.0  │  AI compression             │
│   └──────────┘         └──────────┘                             │
│                                                                  │
│   Legend:                                                        │
│   ◄────► = Active integration (implemented)                     │
│   ────►  = Planned integration (future)                         │
│   opt-in = User must accept prompt to enable                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Active Integrations

#### WebGen ↔ TaskFlow

When both installed, WebGen offers task tracking for its 5-checkpoint workflow:

| Checkpoint | Task Created |
|------------|--------------|
| Requirements | "Define project requirements" |
| Research | "Conduct competitive research" |
| Architecture | "Design project architecture" |
| Implementation | "Implement components" |
| Final Sign-off | "Complete documentation" |

**Benefits:**
- Visual progress tracking during generation
- Resume capability if session interrupted
- Dependency chain enforcement
- Task history for future reference

#### AppGen ↔ TaskFlow

Same integration pattern for AppGen's 8-phase workflow:

| Phase | Task Created |
|-------|--------------|
| Requirements | "Define app requirements" |
| Research | "Research tech stack" |
| Database | "Design database schema" |
| API | "Design API endpoints" |
| Architecture | "Define project structure" |
| Implementation | "Implement application" |
| Testing | "Write and run tests" |
| Deployment | "Configure deployment" |

#### Worklog Hooks (All Sessions)

Worklog hooks fire on **every session**, regardless of which plugins are active:

| Hook | When | What |
|------|------|------|
| SessionStart | Conversation begins | Loads context from worklog DB |
| SessionStop | Conversation ends | Captures learnings, logs work |

**Hook behavior is controlled by your `hook_mode` setting:**

| Mode | Session Start | Session End |
|------|---------------|-------------|
| off | Nothing | Nothing |
| remind | Reminder only | Suggest storing |
| light | Summary index (~150-300 tokens) | Prompt to log |
| full | Detailed index (~300-500 tokens) | Auto-log compressed summary |
| aggressive | Index + critical auto-fetch | Auto-extract all learnings |

**v1.3.0 Improvements:**
- **Progressive disclosure**: Index-first injection (60-70% fewer tokens)
- **AI compression**: Semantic extraction vs raw transcripts
- **PostToolUse hook**: Optional auto-capture of significant file changes

### Planned Integrations (Future)

| Integration | Description | Status |
|-------------|-------------|--------|
| WebGen → Worklog | Auto-store design patterns | Planned |
| AppGen → Worklog | Auto-store architecture decisions | Planned |
| TaskFlow → Worklog | Auto-log completed tasks | Planned |

### Isolated Storage

Each plugin uses separate storage—no conflicts possible:

| Plugin | Storage Location | Format |
|--------|------------------|--------|
| WebGen | `{WEBGEN_OUTPUT_DIR}/` | Project folders |
| AppGen | `{APPGEN_OUTPUT_DIR}/` | Project folders |
| TaskFlow | `.tasks/` (per project) | JSON files |
| Worklog | `worklog.db` or PostgreSQL (global) | SQLite/PostgreSQL |
| Docs | `$DOCS_ROOT/`, `$KNOWLEDGE_BASE/` | Markdown files |

## Requirements

| Plugin | Requirements |
|--------|--------------|
| webgen | Node.js 18+, pnpm 8+ (or npm/yarn) |
| appgen | Node.js 18+, pnpm 8+, PostgreSQL (optional) |
| worklog | None (SQLite default). Optional: PostgreSQL, Python 3.10+ (MCP server) |
| taskflow | None (pure Claude Code) |
| docs | None (pure Claude Code) |

## Configuration

Each plugin has its own configuration. See individual plugin READMEs for details:

- [webgen configuration](plugins/webgen/README.md#configuration)
- [appgen configuration](plugins/appgen/README.md#configuration)
- [worklog configuration](plugins/worklog/README.md#configuration)
- [taskflow configuration](plugins/taskflow/README.md#configuration)
- [docs configuration](plugins/docs/README.md#configuration)

## License

MIT

## Author

[gaurangrshah](https://github.com/gaurangrshah)
