---
name: task-status
description: Update the status of a task
args: <task-id> <status> [--note="..."] [--force]
version: "2.0"
---

# /task-status

Update task status with hygiene prompts and backend sync.

## Usage

```bash
/task-status <task-id> <status> [--note="..."] [--force]
```

## Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not started |
| `in_progress` | Currently working |
| `done` | Completed |
| `blocked` | Cannot proceed |
| `deferred` | Postponed |
| `cancelled` | Will not do |

---

## Workflow

### Step 1: Load Backend

→ See `_core/command-preamble.md`

```python
backend = loadBackend()
if not backend:
    triggerSetup()
    return
```

### Step 2: Get Task

```python
task = backend.getTask(task_id)
if not task:
    print(f"Task not found: {task_id}")
    print("\nUse /task-list to see available tasks.")
    return
```

### Step 3: Validate Transition

```python
VALID_TRANSITIONS = {
    "pending": ["in_progress", "deferred", "cancelled"],
    "in_progress": ["done", "blocked", "deferred", "pending", "cancelled"],
    "blocked": ["pending", "in_progress", "cancelled"],
    "deferred": ["pending", "cancelled"],
    "done": [],  # Final - requires --force
    "cancelled": [],  # Final - requires --force
    "pending_review": ["pending", "in_progress", "done", "cancelled"]
}

current = task["status"]

if new_status not in VALID_TRANSITIONS.get(current, []):
    if not args.force:
        print(f"Invalid transition: {current} → {new_status}")
        print(f"Valid: {', '.join(VALID_TRANSITIONS[current])}")
        if current in ["done", "cancelled"]:
            print("\nUse --force to reopen completed/cancelled tasks.")
        return
```

### Step 4: Hygiene - Prompt for Notes

→ See `_core/task-hygiene.md`

```python
if isAutonomous():
    # Auto-generate note based on transition
    if new_status == "done" and not args.note:
        note = "Task completed"
    elif new_status == "blocked" and not args.note:
        note = "Task blocked (no reason provided)"
    else:
        note = args.note
else:
    # Interactive - prompt based on config
    note = promptForNote(current, new_status, task, args.note)
```

#### Completion Prompt (→ done)

```python
if new_status == "done" and config.hygiene.requireCompletionNotes:
    if task["priority"] == "high" or not args.note:
        # Show acceptance criteria if present
        if task.get("acceptanceCriteria"):
            print("Verify acceptance criteria:")
            for criterion in task["acceptanceCriteria"]:
                print(f"  ☐ {criterion}")
            print()

        response = AskUserQuestion({
            "question": "Add completion notes?",
            "header": "Done",
            "options": [
                {"label": "Add notes", "description": "Capture outcome, gotchas, follow-ups"},
                {"label": "Skip", "description": "Mark done without notes"}
            ]
        })

        if response == "Add notes":
            note = input("Completion notes: ")
```

#### Blocker Prompt (→ blocked)

```python
if new_status == "blocked":
    if config.hygiene.requireBlockerReason and not args.note:
        print("What's blocking this task?")
        note = input("Reason: ")
        if not note:
            print("Blocker reason required. Use --note or provide reason.")
            return
```

### Step 5: Update Status

```python
# Update via backend (handles sync to external system)
task = backend.setStatus(task_id, new_status, note)
```

### Step 6: Check Epic Completion

```python
# If subtask completed, check if epic should complete
if task.get("parentId") and new_status == "done":
    parent = backend.getTask(task["parentId"])
    siblings = backend.listTasks({"parentId": task["parentId"]})

    all_done = all(s["status"] == "done" for s in siblings)
    if all_done:
        response = AskUserQuestion({
            "question": f"All subtasks done. Complete epic '{parent['title']}'?",
            "header": "Epic",
            "options": [
                {"label": "Yes", "description": "Mark epic as done"},
                {"label": "No", "description": "Keep epic in progress"}
            ]
        })
        if response == "Yes":
            backend.setStatus(parent["id"], "done", "All subtasks completed")
```

### Step 7: Worklog Sync

```python
if config.hygiene.autoSyncToWorklog and note:
    # Promote valuable notes to worklog
    if any(keyword in note.lower() for keyword in ["gotcha", "workaround", "decision", "learned"]):
        mcp__worklog__store_memory(
            key=f"taskflow_{task_id}_{datetime.now().strftime('%Y%m%d')}",
            content=note,
            memory_type="fact",
            importance=7,
            tags="taskflow,auto-captured"
        )
```

### Step 8: Confirm & Suggest Next

```python
# Show confirmation
print(f"\nTask updated: {task['title']}")
print(f"  Status: {current} → {new_status}")

if backend.getBackendInfo()["type"] != "local":
    print(f"  Synced: {task.get('externalUrl', 'external system')}")

# Suggest next task if completed
if new_status == "done":
    next_tasks = backend.listTasks({"status": ["pending"], "limit": 1})
    if next_tasks:
        print(f"\nNext task: {next_tasks[0]['title']}")
        print(f"  /task-status {next_tasks[0]['id']} in_progress")
```

---

## Examples

```bash
# Start working on a task
/task-status task-001 in_progress

# Complete with notes
/task-status task-001 done --note="Implemented with retry logic. Gotcha: needed exponential backoff"

# Block with reason
/task-status task-002 blocked --note="Waiting on API credentials from client"

# Defer task
/task-status task-003 deferred --note="Moving to phase 2"

# Reopen completed task
/task-status task-001 in_progress --force
```

---

## Backend Behavior

| Backend | Status Update | Note |
|---------|---------------|------|
| Local | Update tasks.json | Append to notes array |
| Plane | `update_issue(state_id)` | `add_comment()` |
| GitHub | Label change + open/close | `gh issue comment` |

---

**Command Version:** 2.0
**Uses:** Backend abstraction, Task hygiene
