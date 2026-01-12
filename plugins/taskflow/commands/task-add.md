---
name: task-add
description: Add a new task to TaskFlow (ad-hoc, no PRD required)
args: <title> [--priority=high|medium|low] [--type=task|epic] [--description="..."]
version: "2.0"
---

# /task-add

Add a task directly to TaskFlow without needing a PRD.

## Usage

```bash
# Simple task
/task-add "Fix login button styling"

# With priority
/task-add "Implement user auth" --priority=high

# Create an epic
/task-add "User Management System" --type=epic

# With description
/task-add "Add dark mode toggle" --description="Should respect system preference"
```

---

## Workflow

### Step 1: Load Backend

```python
# Load configured backend (or trigger first-run setup)
backend = loadBackend()

if not backend:
    # First run - trigger setup flow
    # See: _core/backend-loader.md
    return runFirstTimeSetup()
```

### Step 2: Parse Arguments

```python
def parseArgs(args):
    # Extract title (required)
    title = args[0] if args else None
    if not title:
        error("Task title required. Usage: /task-add \"Your task title\"")
        return

    # Parse flags
    priority = extractFlag(args, "--priority") or "medium"
    task_type = extractFlag(args, "--type") or "task"
    description = extractFlag(args, "--description") or ""

    return {
        "title": title,
        "priority": priority,
        "type": task_type,
        "description": description
    }
```

### Step 3: Create Task

```python
def createTask(parsed):
    backend = loadBackend()

    task = backend.createTask({
        "title": parsed["title"],
        "description": parsed["description"],
        "priority": parsed["priority"],
        "type": parsed["type"],
        "createdBy": "claude"
    })

    return task
```

### Step 4: Confirm & Offer Next Steps

```markdown
## Task Created

**ID:** {task.id}
**Title:** {task.title}
**Priority:** {task.priority}
**Status:** pending

{if backend.type != "local"}
**Synced to:** {backend.externalUrl}
{/if}

---

**Next steps:**
- Start working: `/task-status {task.id} in_progress`
- Add subtasks: `/task-add "Subtask" --parent={task.id}`
- View all tasks: `/task-list`
```

---

## Examples

### Basic Task

```bash
/task-add "Update README with installation instructions"
```

Output:
```
Task Created

ID: task-001
Title: Update README with installation instructions
Priority: medium
Status: pending

Next steps:
- Start working: /task-status task-001 in_progress
- View all tasks: /task-list
```

### High Priority Task

```bash
/task-add "Fix production database connection timeout" --priority=high
```

Output:
```
Task Created

ID: task-002
Title: Fix production database connection timeout
Priority: high
Status: pending

This is marked HIGH PRIORITY.

Next steps:
- Start immediately: /task-status task-002 in_progress
```

### Create Epic

```bash
/task-add "Authentication System" --type=epic --description="Complete auth flow with JWT, refresh tokens, and OAuth"
```

Output:
```
Epic Created

ID: task-003
Title: Authentication System
Type: epic
Priority: medium
Status: pending

Description:
Complete auth flow with JWT, refresh tokens, and OAuth

Epics can have subtasks. Add them with:
  /task-add "Subtask title" --parent=task-003

Or expand from a description:
  /task-expand task-003
```

### With Plane Backend

```bash
/task-add "Implement search feature" --priority=high
```

Output:
```
Task Created

ID: abc123-def456
Title: Implement search feature
Priority: high (urgent in Plane)
Status: pending

Synced to: https://plane.internal.muhaha.dev/gsdev/work
Issue: WORK-42

Next steps:
- Start working: /task-status abc123-def456 in_progress
- View in Plane: https://plane.internal.muhaha.dev/issue/WORK-42
```

---

## Interactive Mode

If called without arguments, enter interactive mode:

```bash
/task-add
```

Prompts:
```
┌─────────────────────────────────────────────────────────────┐
│  Add New Task                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Title: _                                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Then use AskUserQuestion for priority:

```json
{
  "question": "What priority level?",
  "header": "Priority",
  "options": [
    {"label": "Medium (default)", "description": "Standard priority"},
    {"label": "High", "description": "Urgent or blocking other work"},
    {"label": "Low", "description": "Nice to have, not urgent"}
  ],
  "multiSelect": false
}
```

---

## Flags Reference

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--priority` | high, medium, low | medium | Task priority |
| `--type` | task, epic | task | Task type |
| `--description` | string | "" | Detailed description |
| `--parent` | task-id | null | Parent epic ID (creates subtask) |
| `--no-sync` | flag | false | Skip syncing to external backend |

---

## Error Handling

### No Title Provided

```
Error: Task title required.

Usage: /task-add "Your task title"

Examples:
  /task-add "Fix login bug"
  /task-add "New feature" --priority=high
```

### Backend Not Configured

```
TaskFlow not configured.

Running first-time setup...

[Triggers backend-loader first-run flow]
```

### Backend Connection Failed

```
Warning: Could not connect to Plane backend.

Task saved locally to .tasks/tasks.json
Sync will retry when backend is available.

To switch to local-only mode:
  /task config --backend=local
```

---

## Integration with TodoWrite

When a task is created, optionally add to Claude's TodoWrite:

```python
if config.defaults.get("syncTodoWrite", True):
    TodoWrite([
        {
            "content": task.title,
            "status": "pending",
            "activeForm": f"Working on {task.title[:30]}..."
        }
    ])
```

This keeps Claude's visible todo list in sync with TaskFlow.

---

**Command Version:** 2.0
**Requires:** Backend configured or first-run setup
