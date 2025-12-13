---
title: TaskFlow - Task Management System Design
type: design-document
created: 2025-11-29
updated: 2025-11-29
status: approved
version: "1.1"
---

# TaskFlow - Task Management System Design

A hybrid task management system inspired by [claude-task-master](https://github.com/eyaltoledano/claude-task-master), adapted to work within our Claude Code workflow across multiple environments.

## Overview

TaskFlow transforms Product Requirements Documents (PRDs) into structured, dependency-aware tasks with human-in-the-loop checkpoints. It integrates with existing protocols (journals, git branches, TodoWrite) without duplicating functionality.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage | Per-project with central index | Portable + discoverable |
| Task format | JSON only | Simplicity for MVP |
| TodoWrite | Sync (one-way push) | Task system is source of truth |
| Journals | Separate | Agents use journals independently |
| Checkpoints | Human-in-the-loop | parse, execute, complete |
| Tags | Per-project isolated contexts | Parallel work streams |
| Complexity analysis | Deferred | MVP scope control |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Task Orchestrator                  │
│  (/task skill - environment aware)                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ PRD      │  │ Task     │  │ Environment      │   │
│  │ Parser   │  │ Selector │  │ Adapter          │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │              Tag Manager                      │   │
│  │  (isolated contexts per feature/branch)       │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
├─────────────────────────────────────────────────────┤
│                   Storage Layer                      │
│  (JSON tasks, dependency graph, status tracking)     │
├─────────────────────────────────────────────────────┤
│              Integration Hooks                       │
│  (TodoWrite sync, git branches)                      │
└─────────────────────────────────────────────────────┘
```

---

## Storage Schema

### Directory Structure

```
~/.claude/
├── task-config.json              # Global config (environments, defaults)
│
~/workspace/
├── .task-index.json              # Central index for discoverability
└── projects/
    └── {project}/
        └── .tasks/
            ├── config.json       # Project settings (optional overrides)
            ├── state.json        # Current tag tracking
            └── tags/
                ├── master/
                │   └── tasks.json    # Default tag
                ├── feat-auth/
                │   └── tasks.json    # Feature tag
                └── phase-2/
                    └── tasks.json    # Phase tag
```

### Global Config (`~/.claude/task-config.json`)

```json
{
  "version": "1.1",
  "environments": {
    "atlas": {
      "hostname": "atlas",
      "workspacePath": "/home/gs/workspace",
      "indexPath": "/home/gs/workspace/.task-index.json"
    },
    "dev-vm": {
      "hostname": "dev-vm",
      "workspacePath": "/home/gs/projects",
      "indexPath": "/home/gs/projects/.task-index.json"
    }
  },
  "defaults": {
    "checkpoints": ["parse", "execute", "complete"],
    "syncTodoWrite": true,
    "defaultPriority": "medium",
    "defaultNumTasks": 10,
    "defaultTag": "master",
    "autoTagFromBranch": false
  }
}
```

### Central Index (`~/workspace/.task-index.json`)

```json
{
  "version": "1.0",
  "projects": {
    "project-slug": {
      "name": "My Project",
      "path": "/home/gs/workspace/projects/my-project",
      "created": "2025-11-29T10:00:00Z",
      "lastAccessed": "2025-11-29T12:00:00Z",
      "currentTag": "master",
      "stats": {
        "total": 8,
        "pending": 5,
        "in_progress": 1,
        "done": 2
      }
    }
  }
}
```

### State File (`.tasks/state.json`)

```json
{
  "currentTag": "master",
  "lastSwitched": "2025-11-29T14:30:00Z",
  "tags": {
    "master": {
      "created": "2025-11-29T10:00:00Z",
      "description": "Main task list"
    },
    "feat-auth": {
      "created": "2025-11-29T12:00:00Z",
      "description": "Authentication feature",
      "branch": "feat/user-authentication"
    }
  }
}
```

### Project Tasks (`.tasks/tags/{tag}/tasks.json`)

```json
{
  "version": "1.0",
  "project": "my-project",
  "tag": "master",
  "prdSource": "docs/PRD/feature.md",
  "created": "2025-11-29T10:00:00Z",
  "updated": "2025-11-29T12:00:00Z",
  "tasks": [
    {
      "id": 1,
      "title": "Set up project structure",
      "description": "Initialize the base project with required directories and config files",
      "status": "done",
      "priority": "high",
      "dependencies": [],
      "subtasks": [],
      "acceptanceCriteria": [
        "Directory structure matches spec",
        "Config files created with defaults"
      ],
      "created": "2025-11-29T10:00:00Z",
      "updated": "2025-11-29T11:00:00Z",
      "completedAt": "2025-11-29T11:00:00Z"
    },
    {
      "id": 2,
      "title": "Implement core API endpoints",
      "description": "Create REST endpoints for CRUD operations",
      "status": "in_progress",
      "priority": "high",
      "dependencies": [1],
      "subtasks": [
        {
          "id": "2.1",
          "title": "Create GET endpoint",
          "status": "done"
        },
        {
          "id": "2.2",
          "title": "Create POST endpoint",
          "status": "in_progress"
        },
        {
          "id": "2.3",
          "title": "Create PUT/DELETE endpoints",
          "status": "pending"
        }
      ],
      "acceptanceCriteria": [
        "All CRUD operations functional",
        "Proper error handling",
        "Input validation"
      ],
      "created": "2025-11-29T10:00:00Z",
      "updated": "2025-11-29T12:00:00Z",
      "startedAt": "2025-11-29T11:30:00Z"
    }
  ]
}
```

**Status values**: `pending` | `in_progress` | `done` | `blocked` | `deferred`

**Status metadata fields**:
- `startedAt` - When task moved to in_progress
- `completedAt` - When task marked done
- `blockedAt` - When task was blocked
- `blockedReason` - Why task is blocked
- `deferredAt` - When task was deferred
- `deferredReason` - Why task was deferred

---

## Tag System

### Purpose

Tags provide isolated task contexts for:
- Parallel feature development
- Phase-based project organization
- Experimental branches
- Multiple work streams without conflicts

### Tag Operations

| Command | Description |
|---------|-------------|
| `/task-tag` | Show current tag and list all |
| `/task-tag list` | List all tags with stats |
| `/task-tag use <name>` | Switch to a tag |
| `/task-tag create <name>` | Create new tag |
| `/task-tag delete <name>` | Delete a tag (protected: master) |
| `/task-tag copy <from> <to>` | Copy tasks between tags |

### Tag Integration

All task commands operate on the **current tag**:
- Tasks are stored in `.tasks/tags/{tag}/tasks.json`
- Current tag tracked in `.tasks/state.json`
- Output shows `[Tag: name]` when not on master

### Git Branch Integration

Optional: Link tags to git branches:
```bash
/task-tag create --from-branch  # Creates tag from current branch name
```

---

## PRD Parser

### Purpose
Transform natural language PRD into structured, dependency-aware tasks.

### PRD Location Convention
```
<project-root>/docs/PRD/<feature-name>.md
```

### Parser Prompt Template

```markdown
Analyze this Product Requirements Document and generate a structured task breakdown.

## Instructions
1. Identify discrete, implementable units of work
2. Establish dependencies (what must complete before what)
3. Order by logical implementation sequence
4. Each task should be completable in a focused session (1-4 hours)
5. Include clear acceptance criteria for each task

## Output Format
Return ONLY valid JSON matching this schema (no markdown, no code fences):

{
  "tasks": [
    {
      "id": <sequential integer starting at 1>,
      "title": "<concise action-oriented title - start with verb>",
      "description": "<what needs to be done and why>",
      "status": "pending",
      "priority": "high|medium|low",
      "dependencies": [<array of task IDs that must complete first>],
      "subtasks": [],
      "acceptanceCriteria": ["<measurable success criterion>", ...]
    }
  ]
}

## Rules
- No circular dependencies
- Task 1 should have no dependencies (entry point)
- Higher priority for foundational/blocking work
- Keep tasks focused (if too broad, it will be expanded later)

## PRD Content
<PRD_CONTENT>
```

### Validation
1. Verify JSON is valid (strip code fences if present)
2. Check no circular dependencies
3. Verify all dependency IDs exist
4. Ensure at least one task has no dependencies
5. Validate all required fields present
6. IDs are sequential with no gaps

---

## Task Selector (Next Task Logic)

### Algorithm

```python
def get_next_task(tasks, skip_ids=None):
    skip_ids = skip_ids or set()
    task_map = {t["id"]: t for t in tasks}

    # Filter to actionable tasks
    candidates = [t for t in tasks
                  if t["status"] in ("pending", "blocked")
                  and t["id"] not in skip_ids]

    # Check dependency satisfaction
    actionable = []
    for task in candidates:
        deps_satisfied = all(
            task_map.get(dep_id, {}).get("status") == "done"
            for dep_id in task.get("dependencies", [])
        )
        if deps_satisfied:
            actionable.append(task)

    if not actionable:
        return None

    # Calculate blocking factor
    def count_dependents(task_id):
        return sum(1 for t in tasks if task_id in t.get("dependencies", []))

    # Priority weights
    priority_weight = {"high": 3, "medium": 2, "low": 1}

    # Sort by: priority DESC, blocking_count DESC, id ASC
    actionable.sort(key=lambda t: (
        -priority_weight.get(t.get("priority", "medium"), 2),
        -count_dependents(t["id"]),
        t["id"]
    ))

    return actionable[0]
```

### Subtask Handling

When a task has subtasks:
- Parent task status derived from subtasks
- `next` returns first pending subtask, not parent
- Parent marked `done` only when all subtasks `done`

---

## TodoWrite Sync

### Strategy
- Task system = source of truth
- TodoWrite is ephemeral (session-scoped)
- One-way sync: task system → TodoWrite

### Sync Events

| Event | Action |
|-------|--------|
| `/task-next` | Load current task + subtasks to TodoWrite |
| `/task-status <id> done` | Mark completed in TodoWrite, load next |
| `/task-status <id> in_progress` | Update TodoWrite status |
| Session start | Hydrate from `in_progress` tasks |

### Mapping

```
Task System                          TodoWrite
─────────────────────────────────    ─────────────────────────────
Task 2: Implement API (in_progress)
  ├── 2.1: GET (done)                ✓ Create GET endpoint (completed)
  ├── 2.2: POST (in_progress)   →    ● Create POST endpoint (in_progress)
  └── 2.3: DELETE (pending)          ○ Create DELETE endpoint (pending)
```

---

## Environment Adapter

### Detection Flow

1. Read hostname (`$(hostname)`)
2. Load global config (`~/.claude/task-config.json`)
3. Match environment (`config.environments[hostname]`)
4. If no match, use defaults with warning
5. Override with project config if present (`.tasks/config.json`)

### Configuration Hierarchy

```
Lowest Priority                          Highest Priority
      │                                        │
      ▼                                        ▼
┌──────────┐    ┌──────────────┐    ┌─────────────────┐
│ Built-in │ →  │ Global Config │ →  │ Project Config  │
│ Defaults │    │ (per-env)     │    │ (.tasks/config) │
└──────────┘    └──────────────┘    └─────────────────┘
```

---

## Human Checkpoints

### Checkpoint Types

| Checkpoint | Trigger | Purpose |
|------------|---------|---------|
| `parse` | After PRD parsing | Review generated task breakdown |
| `execute` | Before starting task | Confirm approach/readiness |
| `complete` | When marking done | Verify completion criteria met |

### Configurable

Per-environment or per-project:
```json
{
  "checkpoints": ["parse", "complete"]  // Skip execute checkpoint
}
```

Or disable all:
```json
{
  "checkpoints": []
}
```

---

## Slash Commands

### Command Structure

```
~/.claude/commands/
├── task-init.md          # Initialize tasks in project
├── task-parse.md         # Parse PRD into tasks
├── task-list.md          # List all tasks
├── task-next.md          # Get next recommended task
├── task-show.md          # Show task details
├── task-status.md        # Update task status
├── task-expand.md        # Break task into subtasks
├── task-tag.md           # Manage tags
└── task.md               # Main skill (orchestrator)
```

### Commands Overview

| Command | Purpose | Checkpoint |
|---------|---------|------------|
| `/task-init` | Initialize `.tasks/` directory | None |
| `/task-parse <prd>` | Parse PRD → tasks | **parse** |
| `/task-list` | List tasks with status | None |
| `/task-next` | Get next task | **execute** |
| `/task-show <id>` | Display task details | None |
| `/task-status <id> <status>` | Update status | **complete** (when done) |
| `/task-expand <id>` | Break into subtasks | Review subtasks |
| `/task-tag [subcommand]` | Manage tags | None |
| `/task` | Conversational orchestrator | Routes to above |

---

## Usage Examples

### Initialize and Parse
```bash
/task-init
/task-parse docs/PRD/user-authentication.md
```

### Daily Workflow
```bash
/task-next              # What should I work on?
/task-show 3            # Show me the details
/task-status 3 done     # Mark it complete
```

### Tag Management
```bash
/task-tag                         # Show current tag
/task-tag create feat-auth        # Create feature tag
/task-tag use feat-auth           # Switch to tag
/task-parse docs/PRD/auth.md      # Parse into current tag
/task-tag use master              # Switch back
```

### Conversational (via /task skill)
```
"What tasks are available?"
"Show me task 3"
"I finished the authentication task"
"Break down task 5 into smaller pieces"
"Switch to the auth feature tag"
```

---

## Edge Cases Handled

| Scenario | Resolution |
|----------|------------|
| Initialize in root/home | Block with clear message |
| PRD file not found | List available PRDs, suggest path |
| PRD too large (>50KB) | Warn and offer options |
| Circular dependencies | Detect and auto-fix or regenerate |
| All tasks blocked | Show blocking chain |
| Delete protected tag (master) | Block with explanation |
| Status transition invalid | Show valid transitions |
| Reopen completed task | Require --force flag |
| Multiple tasks in progress | Warn and ask to choose |
| Nested project detection | Warn before proceeding |

---

## Version History

### v1.1 (2025-11-29)
- Added tag system for parallel work streams
- Added state.json for tag tracking
- Updated directory structure for tags
- Added status metadata fields (startedAt, completedAt, etc.)
- Enhanced edge case handling

### v1.0 (2025-11-29)
- Initial design
- Core commands implemented
- Environment adapter
- TodoWrite sync
- Human checkpoints
