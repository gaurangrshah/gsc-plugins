---
description: Update the status of a task or subtask
---

# /task-status

Update the status of a task or subtask, with verification checkpoint when marking complete.

## What This Command Does

1. Load task by ID from current tag's `tasks.json`
2. Validate the status transition
3. **CHECKPOINT** (when marking `done`): Verify acceptance criteria met
4. Update status and timestamps
5. Sync to TodoWrite
6. Suggest next task if applicable

## Arguments

- `<task-id>` - **Required.** Task ID (e.g., `3` or `3.2` for subtask)
- `<status>` - **Required.** New status: `pending`, `in_progress`, `done`, `blocked`, `deferred`
- `--note="..."` - Optional note (useful for blocked/deferred)
- `--tag=<name>` - Target specific tag (default: current tag)
- `--force` - Skip checkpoints and validation (use with caution)

## Status Values

| Status | Meaning | Transitions From | Transitions To |
|--------|---------|------------------|----------------|
| `pending` | Not started, ready when deps met | blocked, deferred | in_progress, deferred |
| `in_progress` | Currently working on | pending, blocked | done, blocked, deferred, pending |
| `done` | Completed | in_progress | (final - cannot undo easily) |
| `blocked` | Cannot proceed, external issue | pending, in_progress | pending, in_progress |
| `deferred` | Postponed intentionally | pending, in_progress | pending |

## Prerequisites

- Project must be initialized (`.tasks/state.json` exists)
- Task ID must exist in current tag

## Workflow

### Step 1: Load Task

**Load current tag and find task:**

```python
if not exists(".tasks/state.json"):
    error("TaskFlow not initialized.")
    suggest("Run /task-init first")
    exit()

state = read_json(".tasks/state.json")
current_tag = args.tag or state["currentTag"]
tasks_file = f".tasks/tags/{current_tag}/tasks.json"

data = read_json(tasks_file)
tasks = data["tasks"]

# Parse task ID (handles both "3" and "3.2")
task_id = args.task_id
is_subtask = "." in str(task_id)

if is_subtask:
    parent_id, subtask_num = task_id.split(".")
    parent = find_task(tasks, int(parent_id))
    task = find_subtask(parent, task_id)
else:
    task = find_task(tasks, int(task_id))
```

**If task not found:**
```
Task <id> not found in tag '<current_tag>'.

Available tasks:
  1. Set up project structure (done)
  2. Implement database schema (done)
  3. Implement user authentication (in_progress)
     3.1 Create registration endpoint (done)
     3.2 Create login endpoint (in_progress)
     3.3 Create token refresh endpoint (pending)
  4. Create API endpoints (pending)
  5. Add rate limiting (pending)

Run /task-list to see all tasks, or check the task ID.
```

### Step 2: Validate Status Value

```python
valid_statuses = ["pending", "in_progress", "done", "blocked", "deferred"]

if new_status not in valid_statuses:
    error(f"Invalid status: '{new_status}'")
    suggest(f"Valid statuses: {', '.join(valid_statuses)}")
    exit()
```

### Step 3: Validate Transition

Check if the status transition is allowed:

```python
valid_transitions = {
    "pending": ["in_progress", "deferred"],
    "in_progress": ["done", "blocked", "deferred", "pending"],
    "blocked": ["pending", "in_progress"],
    "deferred": ["pending"],
    "done": []  # Final state - special handling below
}

current_status = task["status"]

# Special case: undoing done requires --force
if current_status == "done":
    if not args.force:
        error("Cannot change status of completed task without --force")
        suggest("If you need to reopen: /task-status <id> pending --force")
        exit()
    # With --force, allow transition back to pending or in_progress
    valid_transitions["done"] = ["pending", "in_progress"]

if new_status not in valid_transitions[current_status]:
    show_invalid_transition_error(current_status, new_status, valid_transitions)
    exit()
```

**Invalid transition message:**
```
Invalid status transition: pending → done

Task 4 is currently: pending
Valid transitions: in_progress, deferred

You cannot mark a pending task as done directly.
First start the task:
  /task-status 4 in_progress

Then complete it:
  /task-status 4 done

Or did you mean a different task?
```

### Step 4: CHECKPOINT - Verify Completion (when marking done)

When transitioning to `done`, verify acceptance criteria:

```
┌─────────────────────────────────────────────────────────────────┐
│ Completing Task 3: Implement user authentication                │
│ [Tag: master]                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Verify acceptance criteria are met:                             │
│                                                                 │
│ ☐ Users can register with email/password                        │
│ ☐ Users can log in and receive JWT token                        │
│ ☐ Tokens expire after 24 hours                                  │
│ ☐ Refresh token flow extends session                            │
│                                                                 │
│ Time in progress: 2 hours 15 minutes                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ All criteria satisfied?                                         │
└─────────────────────────────────────────────────────────────────┘
```

Use AskUserQuestion:

```json
{
  "question": "All acceptance criteria met?",
  "header": "Verify Done",
  "options": [
    {"label": "Yes", "description": "All criteria satisfied, mark complete"},
    {"label": "No", "description": "Keep task in progress"},
    {"label": "Partial", "description": "Some criteria remain, add note"}
  ],
  "multiSelect": false
}
```

**If Yes:**
- Proceed to update status

**If No:**
- Keep status as `in_progress`
- Display: "Task remains in progress. Complete all criteria before marking done."

**If Partial:**
- Ask: "Which criteria are incomplete?"
- Record note with incomplete criteria
- Offer: "Create subtasks for remaining work?"
- Keep status as `in_progress`

### Step 5: Handle Subtasks (for parent tasks)

**When marking a parent task `done`, check subtasks:**

```python
if not is_subtask and task.get("subtasks"):
    incomplete = [s for s in task["subtasks"] if s["status"] != "done"]
    if incomplete:
        show_incomplete_subtasks_warning(task, incomplete)
```

```
┌─────────────────────────────────────────────────────────────────┐
│ Task 3 has incomplete subtasks                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ✓ 3.1 Create registration endpoint (done)                       │
│ ● 3.2 Create login endpoint (in_progress)                       │
│ ○ 3.3 Create token refresh endpoint (pending)                   │
│                                                                 │
│ 2 of 3 subtasks incomplete                                      │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ How to proceed?                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Use AskUserQuestion:

```json
{
  "question": "How to handle incomplete subtasks?",
  "header": "Subtasks",
  "options": [
    {"label": "Mark all done", "description": "Complete parent and all subtasks"},
    {"label": "Cancel", "description": "Keep working on subtasks first"},
    {"label": "Remove incomplete", "description": "Mark done, remove pending subtasks"}
  ],
  "multiSelect": false
}
```

**When marking a subtask `done`, check if parent should complete:**

```python
if is_subtask and new_status == "done":
    parent = get_parent_task(task_id)
    all_done = all(s["status"] == "done" for s in parent["subtasks"])
    if all_done:
        offer_complete_parent(parent)
```

```
All subtasks of Task 3 are now complete:
  ✓ 3.1 Create registration endpoint
  ✓ 3.2 Create login endpoint
  ✓ 3.3 Create token refresh endpoint

Mark parent Task 3 as done? [Y/n]
```

### Step 6: Handle Blocked Status

When marking as `blocked`, prompt for reason:

```
┌─────────────────────────────────────────────────────────────────┐
│ Blocking Task 4: Create API endpoints                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ What's blocking this task?                                      │
│                                                                 │
│ Common reasons:                                                 │
│   • Waiting on external team/service                            │
│   • Missing requirements/clarification                          │
│   • Technical blocker (dependency, bug)                         │
│   • Other                                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Record the note:
```python
task["blockedReason"] = args.note or input_blocking_reason()
task["blockedAt"] = now_iso8601()
```

### Step 7: Update Task

```python
# Update task status
task["status"] = new_status
task["updated"] = now_iso8601()

# Track status-specific metadata
if new_status == "in_progress" and current_status != "in_progress":
    task["startedAt"] = now_iso8601()
elif new_status == "done":
    task["completedAt"] = now_iso8601()
elif new_status == "blocked":
    task["blockedAt"] = now_iso8601()
    if args.note:
        task["blockedReason"] = args.note
elif new_status == "deferred":
    task["deferredAt"] = now_iso8601()
    if args.note:
        task["deferredReason"] = args.note

# Save to file
write_json(tasks_file, data)
```

### Step 8: Update Central Index

```python
stats = {
    "total": len(tasks),
    "pending": count_by_status(tasks, "pending"),
    "in_progress": count_by_status(tasks, "in_progress"),
    "done": count_by_status(tasks, "done"),
    "blocked": count_by_status(tasks, "blocked"),
    "deferred": count_by_status(tasks, "deferred")
}
update_index(project_slug, current_tag, stats)
```

### Step 9: Sync to TodoWrite

```python
# Update TodoWrite to reflect new status
sync_to_todowrite(tasks, current_task_id=task["id"] if new_status == "in_progress" else None)
```

### Step 10: Confirm and Suggest Next

**When marking done:**
```
Task completed: Implement user authentication

  Status: done ✓
  Tag: master
  Completed: 2025-11-29 16:45
  Duration: 2 hours 15 minutes

This unblocked:
  → Task 4: Create API endpoints (now actionable)
  → Task 5: Add rate limiting (still blocked by Task 4)

Progress: ████████████░░░░ 75% (6/8 tasks)

Next recommended task:
  Task 4: Create API endpoints [HIGH]

Run /task-next to start, or /task-list to see all tasks.
```

**When marking in_progress:**
```
Task started: Create API endpoints

  Status: in_progress ●
  Tag: master
  Started: 2025-11-29 17:00

Acceptance Criteria:
  ☐ GET /users returns user list
  ☐ POST /users creates new user
  ☐ PUT /users/:id updates user
  ☐ DELETE /users/:id removes user
  ☐ All endpoints return proper status codes

When done, run: /task-status 4 done

TodoWrite synced ✓
```

**When marking blocked:**
```
Task blocked: Create API endpoints

  Status: blocked ◌
  Tag: master
  Blocked at: 2025-11-29 17:00
  Reason: Waiting for API credentials from external team

This may affect:
  → Task 5: Add rate limiting (depends on this task)

When unblocked, run: /task-status 4 in_progress
```

**When marking deferred:**
```
Task deferred: Add caching layer

  Status: deferred ⊘
  Tag: master
  Deferred at: 2025-11-29 17:00

This task is postponed. It won't appear in /task-next recommendations.

Tasks that depend on this (if any) may need attention:
  (none)

When ready to resume: /task-status 6 pending
```

## Edge Cases

### Marking Done Without Starting

```
/task-status 4 done

Warning: Task 4 has never been started (status: pending).

This is unusual - typically tasks go pending → in_progress → done.

Mark as done anyway? [Y/n]
```

### Reopening Completed Task

```
/task-status 3 pending

Error: Task 3 is marked as done.

Reopening completed tasks requires --force flag:
  /task-status 3 pending --force

Note: This will clear the completion timestamp.
```

### Status Change on Wrong Tag

```
/task-status 3 done

Task 3 found but you're on tag 'feat-auth'.
Task 3 exists in tag 'master'.

Did you mean:
  /task-status 3 done --tag=master

Or switch tags first:
  /task-tag use master
```

### Rapid Status Changes

If task status changed recently (< 1 minute):

```
Warning: Task 4 status was just changed 30 seconds ago.
  Previous: pending → in_progress at 17:00:30

Continue with: in_progress → done? [Y/n]
```

### Subtask ID Collision

```
/task-status 3.2 done

Found multiple interpretations:
  • Subtask 3.2 of Task 3: Create login endpoint (in_progress)
  • Task 32: (if exists)

Assuming subtask 3.2. Use /task-status 32 for Task 32.
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Task not found | Show available task IDs with status |
| Invalid status value | Show valid status options |
| Invalid transition | Show valid transitions with suggestions |
| Marking done with incomplete subtasks | Offer options to handle |
| Marking done with unmet criteria | Checkpoint to verify |
| Reopening done task | Require --force |
| Wrong tag | Suggest correct tag or switching |

## Examples

```bash
# Start working on task 3
/task-status 3 in_progress

# Mark task 3 as complete
/task-status 3 done

# Mark subtask 3.2 as complete
/task-status 3.2 done

# Block task with note
/task-status 4 blocked --note="Waiting for API credentials"

# Defer a low-priority task
/task-status 6 deferred --note="Moving to phase 2"

# Resume a deferred task
/task-status 6 pending

# Reopen a completed task (use with caution)
/task-status 3 in_progress --force

# Update status in specific tag
/task-status 3 done --tag=feat-auth
```

## Related

- Command: /task-next (get next task after completing)
- Command: /task-show (view task details)
- Command: /task-list (see all task statuses)
- Command: /task-tag (manage tags)
