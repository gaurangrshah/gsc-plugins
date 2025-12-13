---
description: Display detailed information for a specific task
---

# /task-show

Display comprehensive details for a specific task or subtask.

## What This Command Does

1. Load task by ID from `.tasks/tasks.json`
2. Display all task details including acceptance criteria
3. Show dependency status and blocking information
4. Optionally sync to TodoWrite for visibility

## Arguments

- `<task-id>` - **Required.** Task ID (e.g., `3` or `3.2` for subtask)

## Prerequisites

- Project must have tasks (`.tasks/tasks.json` exists with tasks)

## Workflow

### Step 1: Parse Task ID

Handle both task and subtask IDs:

- `3` → Top-level task with id=3
- `3.2` → Subtask 2 of task 3

### Step 2: Load Task

Read `.tasks/tasks.json` and find the specified task.

If not found:
```
Task <id> not found.

Available tasks: 1, 2, 3, 4, 5
Run /task-list to see all tasks.
```

### Step 3: Resolve Dependencies

For each dependency, check its current status:

```python
for dep_id in task.dependencies:
    dep_task = find_task(dep_id)
    dep_status = dep_task.status
    # Determine if satisfied (done) or blocking
```

### Step 4: Display Task Details

**For top-level task:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Task 3: Implement user authentication                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Status:      ○ pending                                          │
│ Priority:    HIGH                                               │
│ Created:     2025-11-29 10:00                                   │
│ Updated:     2025-11-29 12:30                                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Description                                                     │
├─────────────────────────────────────────────────────────────────┤
│ Set up JWT-based authentication flow with login, logout, and    │
│ token refresh capabilities. Should integrate with existing      │
│ user model from task 2.                                         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Dependencies                                                    │
├─────────────────────────────────────────────────────────────────┤
│ ✓ Task 1: Set up project structure (done)                       │
│ ● Task 2: Implement database schema (in_progress)               │
│                                                                 │
│ ⚠ BLOCKED: Waiting on task 2 to complete                        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Acceptance Criteria                                             │
├─────────────────────────────────────────────────────────────────┤
│ ☐ Users can register with email/password                        │
│ ☐ Users can log in and receive JWT token                        │
│ ☐ Tokens expire after 24 hours                                  │
│ ☐ Refresh token flow extends session                            │
│ ☐ Invalid credentials return 401                                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Subtasks                                                        │
├─────────────────────────────────────────────────────────────────┤
│ (none - run /task-expand 3 to break down)                       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Blocking                                                        │
├─────────────────────────────────────────────────────────────────┤
│ This task blocks:                                               │
│   → Task 4: Create API endpoints                                │
│   → Task 5: Add rate limiting                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**For subtask:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Subtask 3.2: Create login endpoint                              │
│ Parent: Task 3 - Implement user authentication                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Status:      ○ pending                                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Sibling Subtasks                                                │
├─────────────────────────────────────────────────────────────────┤
│ ✓ 3.1 Create user registration endpoint                         │
│ ○ 3.2 Create login endpoint (this task)                         │
│ ○ 3.3 Create token refresh endpoint                             │
│ ○ 3.4 Create logout endpoint                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Acceptance Criteria Display

| Status | Display | Meaning |
|--------|---------|---------|
| Unchecked | ☐ | Not verified |
| Checked | ☑ | Verified (when task done) |

When task status is `done`, all criteria show as checked.

### Dependency Status Icons

| Icon | Meaning |
|------|---------|
| ✓ | Dependency satisfied (done) |
| ● | Dependency in progress |
| ○ | Dependency pending |
| ◌ | Dependency blocked |

## Error Handling

| Error | Resolution |
|-------|------------|
| No `.tasks/tasks.json` | Prompt to run `/task-init` |
| Task ID not found | Show available task IDs |
| Invalid ID format | Show expected format (number or number.number) |

## Examples

```bash
# Show task 3 details
/task-show 3

# Show subtask 3.2 details
/task-show 3.2

# Show first task
/task-show 1
```

## Related

- Command: /task-list (overview of all tasks)
- Command: /task-next (get recommended next task)
- Command: /task-status (update this task's status)
- Command: /task-expand (break into subtasks)
