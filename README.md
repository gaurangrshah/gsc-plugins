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

## Plugin Integrations

These plugins are designed to work together:

| Integration | Description |
|-------------|-------------|
| **WebGen + TaskFlow** | Track website generation progress with tasks |
| **AppGen + TaskFlow** | Track app development phases with tasks |
| **WebGen + Worklog** | Persist learnings from website projects |
| **AppGen + Worklog** | Persist learnings from app projects |

Integration is **optional** - each plugin works standalone.

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
