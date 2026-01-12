# TaskFlow - AI-Powered Task Management

A Claude Code plugin for transforming Product Requirements Documents (PRDs) into structured, dependency-aware tasks with human-in-the-loop checkpoints.

**Version:** 2.0.0

## Overview

TaskFlow bridges the gap between planning and execution. It parses PRDs, generates actionable tasks, tracks dependencies, and provides intelligent task recommendations—all integrated with Claude Code's native tools.

Inspired by [claude-task-master](https://github.com/eyaltoledano/claude-task-master), adapted for multi-environment Claude Code workflows.

## Standalone & Integration

### Works 100% Standalone

TaskFlow is fully self-contained. **No other plugins required.**

```bash
# This works perfectly with ONLY taskflow installed:
/task-init
/task-parse docs/PRD/my-feature.md
/task next
```

All commands work. PRD parsing works. Task tracking works. No errors or warnings about missing plugins.

### Optional Integrations

TaskFlow can be detected and used by other GSC plugins:

#### Used by WebGen/AppGen (Passive)

When WebGen or AppGen are installed alongside TaskFlow, they detect TaskFlow and offer to track their workflows as tasks:

```
# User runs /webgen with TaskFlow installed:
TaskFlow detected. Track this project with tasks? (y/n)
```

**TaskFlow doesn't need to do anything**—WebGen/AppGen handle the integration. TaskFlow just provides its normal task management capabilities.

**Benefits when used together:**
- WebGen/AppGen phases become trackable tasks
- Visual progress during generation
- Resume capability if interrupted
- Task history persists after generation

#### Worklog Integration (Passive)

If [Worklog](../worklog/) is installed, its hooks provide background context:

- **SessionStart hook**: Loads recent work context during task sessions
- **SessionStop hook**: Prompts to store learnings after task completion

TaskFlow doesn't actively integrate with Worklog yet, but Worklog's general-purpose hooks still fire during TaskFlow sessions.

**Future (Planned):**
- Auto-log completed tasks to worklog entries table
- Store task templates to knowledge_base
- Cross-session task context from memories table

## Quick Start

### 1. Install Plugin

**Option A: Marketplace (Recommended)**
```bash
# Add the marketplace (if not already added)
claude plugin marketplace add https://github.com/gaurangrshah/gsc-plugins.git

# Install the plugin
claude plugin install taskflow@gsc-plugins
```

**Option B: Manual Installation**
```bash
# Clone the repo
git clone https://github.com/gaurangrshah/gsc-plugins.git

# Copy to local-plugins
cp -r gsc-plugins/plugins/taskflow ~/.claude/plugins/local-plugins/

# Restart Claude Code to activate
```

### 2. Configure (Optional)

Create `~/.claude/task-config.json`:
```json
{
  "version": "1.1",
  "environments": {
    "my-machine": {
      "hostname": "my-machine",
      "workspacePath": "/home/user/projects",
      "indexPath": "/home/user/projects/.task-index.json"
    }
  },
  "defaults": {
    "syncTodoWrite": true,
    "defaultTag": "master"
  }
}
```

### 3. Initialize a Project

```
/task-init
```

### 4. Parse a PRD

```
/task-parse docs/PRD/my-feature.md
```

### 5. Start Working

```
/task next
```

## Commands

| Command | Description |
|---------|-------------|
| `/task` | Conversational interface - status overview and natural language routing |
| `/task-init` | Initialize TaskFlow in current project (with backend selection) |
| `/task-add` | Add an ad-hoc task (no PRD required) |
| `/task-parse <prd>` | Generate tasks from a PRD document |
| `/task-list` | List all tasks with filtering options |
| `/task-next` | Get AI-recommended next task |
| `/task-show <id>` | View detailed task information |
| `/task-status <id> <status>` | Update task status (with hygiene prompts) |
| `/task-tag` | Manage parallel work contexts (tags) |
| `/task-expand <id>` | Break task into subtasks |
| `/task-migrate-config` | Migrate v1.x JSON config to v2.0 format |

## Features

### PRD Parsing
Transforms markdown PRD documents into structured tasks with:
- Automatic dependency detection
- Priority assignment
- Effort estimation
- Acceptance criteria extraction

### Intelligent Task Selection
`/task-next` considers:
- Dependency satisfaction
- Priority levels
- Your recent work context
- Blocked task avoidance

### Tags for Parallel Work
Work on multiple features without conflicts:
```
/task-tag create feat-auth
/task-tag switch feat-auth
# Work in isolated context
/task-tag switch master
```

### Human-in-the-Loop Checkpoints
Three checkpoint stages ensure quality:
1. **Parse** - Review generated tasks before starting
2. **Execute** - Confirm approach before implementation
3. **Complete** - Verify acceptance criteria before closing

### TodoWrite Integration
Active tasks sync to Claude Code's TodoWrite for real-time visibility.

## Storage Structure

```
project/
└── .tasks/
    ├── state.json           # Current tag tracking
    └── tags/
        ├── master/
        │   └── tasks.json   # Default task list
        └── feat-auth/
            └── tasks.json   # Feature-specific tasks
```

## Task Schema

```json
{
  "id": 1,
  "title": "Implement user authentication",
  "description": "Add JWT-based auth with refresh tokens",
  "status": "pending",
  "priority": "high",
  "dependencies": [],
  "subtasks": [],
  "acceptanceCriteria": [
    "Users can register with email",
    "Users can login and receive tokens",
    "Tokens refresh automatically"
  ],
  "prdSection": "## Authentication",
  "estimatedEffort": "medium",
  "created": "2025-12-01T10:00:00Z",
  "updated": "2025-12-01T10:00:00Z"
}
```

## Status Values

| Status | Description |
|--------|-------------|
| `pending` | Not yet started |
| `in_progress` | Currently being worked on |
| `done` | Completed successfully |
| `blocked` | Waiting on external dependency |
| `deferred` | Postponed for later |

## Configuration

### Config File Format (v2.0)

TaskFlow v2.0 uses `.local.md` files with YAML frontmatter:

**Project-level:** `./.taskflow.local.md`
**Global:** `~/.gsc-plugins/taskflow.local.md`

```yaml
---
backend: local  # local | plane | github

local:
  path: .tasks/

# For Plane backend:
# plane:
#   workspace: gsdev
#   project: work

# For GitHub backend:
# github:
#   owner: myuser
#   repo: my-project

defaults:
  defaultPriority: medium
  defaultTag: master
  syncTodoWrite: true

hygiene:
  requireCompletionNotes: true
  requireBlockerReason: true
  promptForNotes: true
  autoSyncToWorklog: false
---

# TaskFlow Configuration
```

### Backend Options

| Backend | Description | Requirements |
|---------|-------------|--------------|
| `local` | Store tasks in `.tasks/` folder | None (default) |
| `plane` | Sync with Plane issues | Plane MCP configured |
| `github` | Sync with GitHub Issues | `gh` CLI authenticated |

### Upgrading from v1.x

If you have an existing `~/.claude/task-config.json`:

```bash
# Preview migration
/task-migrate-config --dry-run

# Run migration
/task-migrate-config
```

TaskFlow v2.0 is backwards compatible - old configs still work, but you'll see a migration notice.

### Legacy Config (v1.x - deprecated)

```json
{
  "version": "1.1",
  "environments": { ... },
  "defaults": { ... }
}
```

The `environments` section is no longer used. Use project-level `.taskflow.local.md` files instead.

## Natural Language Examples

```
/task what should I work on next?
/task I finished the authentication task
/task show me task 5
/task break down task 3
/task I'm blocked on task 2
```

## Multi-Environment Support

TaskFlow detects your hostname and applies environment-specific configuration automatically. This enables:
- Different workspace paths per machine
- Separate task indexes per environment
- Consistent behavior across systems

## Plugin Structure

```
taskflow/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── task.md
│   ├── task-init.md
│   ├── task-list.md
│   ├── task-next.md
│   ├── task-parse.md
│   ├── task-show.md
│   ├── task-status.md
│   ├── task-tag.md
│   └── task-expand.md
├── config/
│   └── default-config.json
├── docs/
│   └── design.md
└── README.md
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage | Per-project JSON | Portable, git-friendly |
| Tags | Isolated contexts | Parallel feature work |
| TodoWrite | One-way sync | Task system is source of truth |
| Checkpoints | Human-in-the-loop | Quality over speed |

## Version History

### 2.0.0
- **Backend abstraction**: Unified interface for Local, Plane, GitHub, Linear backends
- **New config format**: `.local.md` with YAML frontmatter (project + global scope)
- **Auto-detection**: Automatically detects available backends (Plane MCP, GitHub CLI)
- **Task hygiene**: Prompts for completion notes, blocker reasons, decisions, gotchas
- **Epic support**: Complex tasks become epics with subtasks
- **Ad-hoc tasks**: New `/task-add` command for tasks without PRDs
- **Migration command**: `/task-migrate-config` upgrades v1.x configs
- **Backwards compatible**: Old JSON configs still work with migration notice

### 1.1.0
- **Issue tracker auto-detection**: Auto-detects Gitea and GitHub during `/task-init`
- **Dual Gitea detection**: Checks both config files AND git remotes for Gitea availability
- **GitHub fallback**: Falls back to GitHub Issues via `gh` CLI if Gitea unavailable
- **Mandatory TodoWrite**: TodoWrite is now required for all TaskFlow projects (dual-write for redundancy)
- **Enhanced config**: New `issueTracker` and `todoWrite` config sections
- **Graceful fallbacks**: Works 100% locally if no issue trackers available

### 1.0.0
- Initial plugin release
- 9 commands for complete task lifecycle
- Tag-based parallel work contexts
- PRD parsing with dependency detection
- Intelligent task recommendation
- TodoWrite integration
- Multi-environment support

## License

MIT
