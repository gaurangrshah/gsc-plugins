# GSC Plugins

A collection of Claude Code plugins for enhanced development workflows.

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [webgen](plugins/webgen/) | 1.4.0 | Natural language to production-ready websites |
| [worklog](plugins/worklog/) | 1.1.0 | Cross-session knowledge persistence with SQLite |
| [taskflow](plugins/taskflow/) | 1.0.0 | AI-powered task management from PRDs |

## Installation

### Add Marketplace

```
/plugin marketplace add gs/gsc-plugins
```

### Install Individual Plugins

```
/plugin install webgen@gsc-plugins
/plugin install worklog@gsc-plugins
/plugin install taskflow@gsc-plugins
```

### Manual Installation

Clone and copy to your plugins directory:
```bash
git clone https://github.com/gs/gsc-plugins.git
cp -r gsc-plugins/plugins/webgen ~/.claude/plugins/local-plugins/
cp -r gsc-plugins/plugins/worklog ~/.claude/plugins/local-plugins/
cp -r gsc-plugins/plugins/taskflow ~/.claude/plugins/local-plugins/
```

## Plugin Overview

### WebGen

Transform natural language descriptions into complete, production-ready web projects.

**Features:**
- 5-checkpoint orchestrated workflow
- React, Next.js, Astro support
- Built-in code review agent
- Design system skill
- Legal/compliance templates

**Quick Start:**
```
/webgen a modern landing page for a fitness app
```

**Dependencies:** Node.js 18+, pnpm/npm

[Full documentation →](plugins/webgen/README.md)

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

**Quick Start:**
```
/task-init
/task-parse docs/PRD/my-feature.md
/task next
```

[Full documentation →](plugins/taskflow/README.md)

---

## Requirements

| Plugin | Requirements |
|--------|--------------|
| webgen | Node.js 18+, pnpm 8+ (or npm/yarn) |
| worklog | SQLite 3.0+ |
| taskflow | None (pure Claude Code) |

## Configuration

Each plugin has its own configuration. See individual plugin READMEs for details:

- [webgen configuration](plugins/webgen/README.md#configuration)
- [worklog configuration](plugins/worklog/README.md#configuration)
- [taskflow configuration](plugins/taskflow/README.md#configuration)

## License

MIT

## Author

gs
