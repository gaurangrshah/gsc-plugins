# GSC Plugins

A collection of Claude Code plugins for enhanced development workflows.

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [webgen](plugins/webgen/) | 1.5.0 | Natural language to production-ready websites and landing pages |
| [appgen](plugins/appgen/) | 1.0.0 | Full-stack applications and APIs from natural language |
| [worklog](plugins/worklog/) | 1.1.0 | Cross-session knowledge persistence with SQLite |
| [taskflow](plugins/taskflow/) | 1.0.0 | AI-powered task management from PRDs |

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

## Plugin Overview

### WebGen

Transform natural language descriptions into complete, production-ready web projects (landing pages, marketing sites).

**Features:**
- 5-checkpoint orchestrated workflow
- React, Next.js, Astro support
- Asset management (screenshot/design references)
- Optional TaskFlow integration
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

Cross-session knowledge persistence using SQLite. Maintain context, learnings, and work history across Claude Code sessions.

**Features:**
- 3 profile levels (minimal, standard, full)
- Memory store/recall/sync skills
- Multi-system support with shared databases
- Error pattern tracking
- Network retry logic for shared databases

**Quick Start:**
```
/worklog-init
```

**Dependencies:** SQLite 3.0+

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

## Plugin Architecture

### Standalone by Design

**Every plugin works 100% independently.** Install one, two, or all four—each functions fully without the others.

| Installation | Status | Notes |
|--------------|--------|-------|
| webgen only | ✅ Full | All 5 checkpoints work |
| appgen only | ✅ Full | All 8 phases work |
| taskflow only | ✅ Full | Complete task management |
| worklog only | ✅ Full | All hooks + skills work |
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
│   │  v1.5.0  │ opt-in  │  v1.0.0  │  as tasks with deps         │
│   └────┬─────┘         └────┬─────┘                             │
│        │                    │                                    │
│        │ (future)           │ (future)                          │
│        │                    │                                    │
│        ▼                    ▼                                    │
│   ┌──────────┐         ┌──────────┐                             │
│   │  Worklog │         │  Worklog │  Context loading via hooks  │
│   │  v1.2.0  │         │  v1.2.0  │  Learning capture           │
│   └──────────┘         └──────────┘                             │
│                                                                  │
│   ┌──────────┐         ┌──────────┐                             │
│   │  AppGen  │◄───────►│ TaskFlow │  Track app dev phases       │
│   │  v1.0.0  │ opt-in  │  v1.0.0  │  as tasks with deps         │
│   └────┬─────┘         └────┬─────┘                             │
│        │                    │                                    │
│        │ (future)           │ (future)                          │
│        ▼                    ▼                                    │
│   ┌──────────┐         ┌──────────┐                             │
│   │  Worklog │         │  Worklog │  Context loading via hooks  │
│   │  v1.2.0  │         │  v1.2.0  │  Learning capture           │
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
| light | Recent work + memories | Prompt to log |
| full | Comprehensive context | Auto-log summary |
| aggressive | Full + flagged items | Auto-extract learnings |

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
| Worklog | `worklog.db` (global) | SQLite database |

## Requirements

| Plugin | Requirements |
|--------|--------------|
| webgen | Node.js 18+, pnpm 8+ (or npm/yarn) |
| appgen | Node.js 18+, pnpm 8+, PostgreSQL (optional) |
| worklog | SQLite 3.0+ |
| taskflow | None (pure Claude Code) |

## Configuration

Each plugin has its own configuration. See individual plugin READMEs for details:

- [webgen configuration](plugins/webgen/README.md#configuration)
- [appgen configuration](plugins/appgen/README.md#configuration)
- [worklog configuration](plugins/worklog/README.md#configuration)
- [taskflow configuration](plugins/taskflow/README.md#configuration)

## License

MIT

## Author

[gaurangrshah](https://github.com/gaurangrshah)
