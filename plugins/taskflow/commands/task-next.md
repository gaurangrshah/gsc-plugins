---
description: Get the recommended next task to work on
---

# /task-next

Determine and display the optimal next task based on dependencies, priority, and status.

## What This Command Does

1. Load tasks from current tag's `tasks.json`
2. Apply selection algorithm (dependencies satisfied, priority, blocking factor)
3. **CHECKPOINT**: Present task for approval before starting
4. On approval, mark as `in_progress` and sync to TodoWrite

## Arguments

- `--skip` - Skip the recommended task and show the next alternative
- `--no-checkpoint` - Start immediately without confirmation
- `--tag=<name>` - Get next task from specific tag (default: current tag)

## Prerequisites

- Project must be initialized (`.tasks/state.json` exists)
- Current tag must have tasks
- At least one task must be actionable (pending with satisfied dependencies)

## Workflow

### Step 1: Load Tasks

**Load current tag and tasks:**

```python
if not exists(".tasks/state.json"):
    error("TaskFlow not initialized.")
    suggest("Run /task-init first")
    exit()

state = read_json(".tasks/state.json")
current_tag = args.tag or state["currentTag"]
tasks_file = f".tasks/tags/{current_tag}/tasks.json"

if not exists(tasks_file):
    error(f"Tag '{current_tag}' has no tasks file.")
    suggest("Run /task-parse to generate tasks")
    exit()

data = read_json(tasks_file)
tasks = data["tasks"]

if not tasks:
    error("No tasks in current tag.")
    suggest("Run /task-parse docs/PRD/your-feature.md")
    exit()
```

**Show tag context in output:**
```
[Tag: feat-auth]  # Only show if not 'master'
```

### Step 2: Check for In-Progress Tasks

First, check if there's already a task in progress:

```python
# Check both top-level tasks and subtasks
in_progress = []
for task in tasks:
    if task["status"] == "in_progress":
        in_progress.append(task)
    for subtask in task.get("subtasks", []):
        if subtask["status"] == "in_progress":
            in_progress.append({"parent": task, "subtask": subtask})

if in_progress:
    display_current_task(in_progress[0])
    ask_continue_or_switch()
```

**If task already in progress:**
```
┌─────────────────────────────────────────────────────────────────┐
│ You have a task in progress                                     │
│ [Tag: master]                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ● Task 3: Implement user authentication                         │
│   Priority: HIGH                                                │
│   Started: 2025-11-29 14:30 (2 hours ago)                       │
│                                                                 │
│   Subtasks:                                                     │
│   ✓ 3.1 Create registration endpoint                            │
│   ● 3.2 Create login endpoint (in progress)                     │
│   ○ 3.3 Create token refresh endpoint                           │
│                                                                 │
│   Acceptance Criteria remaining:                                │
│   ☐ Users can log in and receive JWT token                      │
│   ☐ Refresh token flow extends session                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Continue with this task?                                        │
└─────────────────────────────────────────────────────────────────┘
```

Use AskUserQuestion:

```json
{
  "question": "Continue with current task?",
  "header": "In Progress",
  "options": [
    {"label": "Continue", "description": "Keep working on this task"},
    {"label": "Complete", "description": "Mark as done and get next"},
    {"label": "Switch", "description": "Work on different task"},
    {"label": "Block", "description": "Mark as blocked, get next"}
  ],
  "multiSelect": false
}
```

### Step 3: Select Next Task

Apply selection algorithm:

```python
def get_next_task(tasks, skip_ids=None):
    skip_ids = skip_ids or set()

    # Build task lookup for dependency checking
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
            # If task was blocked but deps now satisfied, it's actionable
            actionable.append(task)

    if not actionable:
        return None

    # Calculate blocking factor (how many tasks depend on this one)
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

**Handle subtask selection:**

If selected task has subtasks, return the first pending subtask instead:

```python
task = get_next_task(tasks)
if task and task.get("subtasks"):
    pending_subtasks = [s for s in task["subtasks"] if s["status"] == "pending"]
    if pending_subtasks:
        return {"parent": task, "subtask": pending_subtasks[0]}
return task
```

### Step 4: Handle No Available Tasks

**If all tasks blocked:**
```
┌─────────────────────────────────────────────────────────────────┐
│ No actionable tasks available                                   │
│ [Tag: master]                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Current status:                                                 │
│   ✓ Done: 3 tasks                                               │
│   ● In Progress: 1 task (Task 4)                                │
│   ◌ Blocked: 2 tasks (waiting on Task 4)                        │
│   ○ Pending: 0 tasks                                            │
│                                                                 │
│ Blocked tasks and their blockers:                               │
│   Task 5 ← waiting on: Task 4 (in_progress)                     │
│   Task 6 ← waiting on: Task 4 (in_progress), Task 5 (blocked)   │
│                                                                 │
│ Action needed:                                                  │
│   Complete Task 4 to unblock Tasks 5, 6                         │
│                                                                 │
│ Run /task-show 4 to see details.                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**If all tasks done:**
```
┌─────────────────────────────────────────────────────────────────┐
│ All tasks complete!                                             │
│ [Tag: master]                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Project: my-project                                             │
│ Tasks completed: 8/8                                            │
│ Duration: Started 2025-11-28, completed 2025-11-29              │
│                                                                 │
│ What's next?                                                    │
│   • Parse another PRD: /task-parse docs/PRD/next-feature.md     │
│   • Create new tag: /task-tag create phase-2                    │
│   • Switch tags: /task-tag use feat-auth                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**If no tasks at all:**
```
┌─────────────────────────────────────────────────────────────────┐
│ No tasks in tag 'master'                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Get started:                                                    │
│   1. Create a PRD in docs/PRD/your-feature.md                   │
│   2. Run: /task-parse docs/PRD/your-feature.md                  │
│                                                                 │
│ Or switch to a tag with tasks:                                  │
│   /task-tag list                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 5: CHECKPOINT - Confirm Task Start

Present the selected task for approval:

```
┌─────────────────────────────────────────────────────────────────┐
│ Recommended Next Task                                           │
│ [Tag: master]                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Task 3: Implement user authentication                           │
│                                                                 │
│ Priority:     HIGH                                              │
│ Dependencies: ✓ All satisfied                                   │
│   ✓ Task 1: Set up project structure (done)                     │
│   ✓ Task 2: Implement database schema (done)                    │
│                                                                 │
│ Description:                                                    │
│ Set up JWT-based authentication flow with login, logout, and    │
│ token refresh capabilities.                                     │
│                                                                 │
│ Acceptance Criteria:                                            │
│ ☐ Users can register with email/password                        │
│ ☐ Users can log in and receive JWT token                        │
│ ☐ Tokens expire after 24 hours                                  │
│ ☐ Refresh token flow extends session                            │
│                                                                 │
│ Impact:                                                         │
│ This task blocks 2 other tasks (4, 5)                           │
│                                                                 │
│ Alternatives available: 1 other actionable task                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Ready to start this task?                                       │
└─────────────────────────────────────────────────────────────────┘
```

Use AskUserQuestion:

```json
{
  "question": "Ready to start this task?",
  "header": "Start Task",
  "options": [
    {"label": "Yes", "description": "Mark as in_progress and begin"},
    {"label": "Skip", "description": "Show next available task"},
    {"label": "Expand", "description": "Break into subtasks first"},
    {"label": "Details", "description": "Show full task details"}
  ],
  "multiSelect": false
}
```

### Step 6: Handle Response

**If Yes:**
- Update task status to `in_progress`
- Update `updated` timestamp
- Save to tasks.json
- Sync to TodoWrite
- Display "Task started" confirmation

**If Skip:**
- Add task ID to session skip list
- Re-run selection excluding skipped tasks
- If no more tasks available after skipping, inform user
- Return to Step 5 with next candidate

```
Skipped Task 3. Checking for alternatives...

[Shows next task or "No other actionable tasks available"]
```

**If Expand:**
- Trigger `/task-expand <id>` flow
- After expansion, return and show first subtask

**If Details:**
- Trigger `/task-show <id>` flow
- After viewing, return to checkpoint

### Step 7: Sync to TodoWrite

On task start, sync current state to TodoWrite:

```python
todos = []

# Current task (with subtasks if any)
if task.get("subtasks"):
    for subtask in task["subtasks"]:
        todos.append({
            "content": subtask["title"],
            "status": map_status(subtask["status"]),
            "activeForm": to_active_form(subtask["title"])
        })
else:
    todos.append({
        "content": task["title"],
        "status": "in_progress",
        "activeForm": to_active_form(task["title"])
    })

# Upcoming tasks for context (max 3)
upcoming = get_next_tasks(tasks, exclude=task["id"], limit=3)
for t in upcoming:
    todos.append({
        "content": t["title"],
        "status": "pending",
        "activeForm": to_active_form(t["title"])
    })

TodoWrite(todos=todos)

def map_status(task_status):
    return {
        "done": "completed",
        "in_progress": "in_progress",
        "pending": "pending",
        "blocked": "pending",
        "deferred": "pending"
    }.get(task_status, "pending")

def to_active_form(title):
    """Convert 'Create login endpoint' to 'Creating login endpoint'"""
    verb_mappings = {
        "Create": "Creating",
        "Implement": "Implementing",
        "Add": "Adding",
        "Configure": "Configuring",
        "Set up": "Setting up",
        "Build": "Building",
        "Write": "Writing",
        "Fix": "Fixing",
        "Update": "Updating",
        "Remove": "Removing",
        "Refactor": "Refactoring",
        "Test": "Testing",
        "Deploy": "Deploying",
    }
    for verb, active in verb_mappings.items():
        if title.startswith(verb + " "):
            return title.replace(verb + " ", active + " ", 1)
        if title.startswith(verb.lower() + " "):
            return title.replace(verb.lower() + " ", active.lower() + " ", 1)
    # Fallback: prepend "Working on"
    return f"Working on {title}"
```

### Step 8: Confirm Start

```
Task started: Implement user authentication

  Status: in_progress ●
  Tag: master
  Started: 2025-11-29 14:30

Acceptance Criteria to complete:
  ☐ Users can register with email/password
  ☐ Users can log in and receive JWT token
  ☐ Tokens expire after 24 hours
  ☐ Refresh token flow extends session

When done, run: /task-status 3 done

TodoWrite synced ✓
```

## Edge Cases

### Multiple Tasks In Progress

If somehow multiple tasks are in progress (shouldn't happen normally):

```
Warning: Multiple tasks are in progress:
  ● Task 3: Implement authentication
  ● Task 5: Add caching

This may indicate interrupted work. Please choose one to continue:
```

### All Skipped

If user skips all actionable tasks:

```
All actionable tasks have been skipped.

Skipped: Task 3, Task 5, Task 7

Options:
  • Clear skips and start over: /task-next
  • View all tasks: /task-list
  • Work on a specific task: /task-status <id> in_progress
```

### Task Has Already-Started Subtasks

If task has subtasks and some are already in progress:

```
Task 3 has a subtask in progress:
  ● 3.2 Create login endpoint

Continue with subtask 3.2?
```

### Circular Skip Detection

If skip would create circular situation:

```
Cannot skip Task 3 - it's the only actionable task.

Options:
  • Start Task 3
  • Mark a blocking task as done: /task-status <id> done
  • Defer Task 3: /task-status 3 deferred
```

## Error Handling

| Error | Resolution |
|-------|------------|
| No `.tasks/state.json` | Prompt to run `/task-init` |
| Tag doesn't exist | Suggest valid tags or create new |
| No tasks in tag | Prompt to run `/task-parse` |
| No tasks file | Tag exists but no tasks.json - suggest parse |
| All tasks blocked | Show blocking chain and how to unblock |
| All tasks done | Celebrate and suggest next steps |
| All tasks skipped | Offer to clear skips |

## Examples

```bash
# Get next recommended task
/task-next

# Skip current recommendation
/task-next --skip

# Start without confirmation
/task-next --no-checkpoint

# Get next from specific tag
/task-next --tag=feat-auth
```

## Related

- Command: /task-list (see all tasks)
- Command: /task-show (detailed task view)
- Command: /task-status (mark task done)
- Command: /task-expand (break into subtasks)
- Command: /task-tag (manage tags)
