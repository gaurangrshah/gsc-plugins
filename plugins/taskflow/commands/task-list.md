---
description: List all tasks with status and filtering
---

# /task-list

Display all tasks in the current project with their status, priority, and dependencies.

## What This Command Does

1. Load tasks from `.tasks/tasks.json`
2. Apply any filters (status, priority)
3. Display formatted task list
4. Show summary statistics

## Arguments

- `--status=<status>` - Filter by status (pending, in_progress, done, blocked, deferred)
- `--priority=<priority>` - Filter by priority (high, medium, low)
- `--with-subtasks` - Include subtasks in output
- `--blocked` - Show only tasks with unsatisfied dependencies

## Prerequisites

- Project must be initialized with tasks (`.tasks/tasks.json` exists)

## Workflow

### Step 1: Load Tasks

Read `.tasks/tasks.json` from current project directory.

If file doesn't exist or is empty:
```
No tasks found in this project.

Run /task-init to initialize, then /task-parse to generate tasks from a PRD.
```

### Step 2: Apply Filters

Filter tasks based on arguments:

```python
tasks = all_tasks

if status_filter:
    tasks = [t for t in tasks if t.status == status_filter]

if priority_filter:
    tasks = [t for t in tasks if t.priority == priority_filter]

if blocked_filter:
    tasks = [t for t in tasks if has_unsatisfied_dependencies(t)]
```

### Step 3: Display Tasks

Format and display task list:

```
┌─────────────────────────────────────────────────────────────────┐
│ Tasks: <project-name>                                           │
│ Source: <prd-source>                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✓ 1. [HIGH] Set up project structure                           │
│                                                                 │
│  ● 2. [HIGH] Implement database schema              (needs: 1)  │
│     ├── ✓ 2.1 Create user table                                 │
│     ├── ● 2.2 Create posts table                                │
│     └── ○ 2.3 Add indexes                                       │
│                                                                 │
│  ○ 3. [HIGH] Implement authentication               (needs: 1)  │
│                                                                 │
│  ○ 4. [MED]  Create API endpoints                   (needs: 2,3)│
│                                                                 │
│  ◌ 5. [LOW]  Add caching layer                      (needs: 4)  │
│     └── BLOCKED: waiting on task 4                              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Summary: 5 tasks (1 done, 1 in progress, 2 pending, 1 blocked)  │
│ Next available: Task 3 - Implement authentication               │
└─────────────────────────────────────────────────────────────────┘
```

### Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| ✓ | done | Completed |
| ● | in_progress | Currently working |
| ○ | pending | Ready to start |
| ◌ | blocked | Dependencies not met |
| ⊘ | deferred | Postponed |

### Priority Display

| Priority | Display |
|----------|---------|
| high | `[HIGH]` |
| medium | `[MED]` |
| low | `[LOW]` |

### Step 4: Show Summary

After task list, display:

```
Summary: <total> tasks (<done> done, <in_progress> in progress, <pending> pending, <blocked> blocked)
Next available: Task <id> - <title>
```

## Output Variations

### Default (no flags)
Shows all tasks with subtasks collapsed, single line per task.

### With --with-subtasks
Expands subtasks under each parent:

```
● 2. [HIGH] Implement database schema
   ├── ✓ 2.1 Create user table
   ├── ● 2.2 Create posts table
   └── ○ 2.3 Add indexes
```

### With --status=pending
Shows only pending tasks:

```
Pending Tasks (3):

  ○ 3. [HIGH] Implement authentication               (needs: 1)
  ○ 4. [MED]  Create API endpoints                   (needs: 2,3)
  ○ 6. [LOW]  Write documentation                    (needs: 4,5)
```

### With --blocked
Shows tasks that can't start due to dependencies:

```
Blocked Tasks (2):

  ◌ 4. [MED]  Create API endpoints
     └── Waiting on: 2 (in_progress), 3 (pending)

  ◌ 5. [LOW]  Add caching layer
     └── Waiting on: 4 (blocked)
```

## Error Handling

| Error | Resolution |
|-------|------------|
| No `.tasks/tasks.json` | Prompt to run `/task-init` |
| Empty task list | Show guidance to run `/task-parse` |
| Invalid filter value | Show valid options |

## Examples

```bash
# List all tasks
/task-list

# Show only pending tasks
/task-list --status=pending

# Show high priority tasks with subtasks
/task-list --priority=high --with-subtasks

# Show blocked tasks
/task-list --blocked
```

## Related

- Command: /task-show (detailed view of single task)
- Command: /task-next (get recommended next task)
- Command: /task-status (update task status)
