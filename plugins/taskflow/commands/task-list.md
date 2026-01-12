---
name: task-list
description: List all tasks with status and filtering
args: [--status=...] [--priority=...] [--type=...] [--search="..."]
version: "2.0"
---

# /task-list

List tasks from the configured backend with optional filtering.

## Usage

```bash
/task-list [--status=pending,in_progress] [--priority=high] [--type=epic] [--search="auth"]
```

## Filters

| Flag | Values | Description |
|------|--------|-------------|
| `--status` | pending, in_progress, done, blocked, deferred, cancelled | Filter by status |
| `--priority` | high, medium, low | Filter by priority |
| `--type` | epic, task, subtask | Filter by type |
| `--search` | string | Full-text search |
| `--limit` | number | Max results (default: 20) |

---

## Workflow

### Step 1: Load Backend

```python
backend = loadBackend()
if not backend:
    triggerSetup()
    return
```

### Step 2: Build Filters & Fetch

```python
filters = {}
if args.status:
    filters["status"] = args.status.split(",")
if args.priority:
    filters["priority"] = args.priority.split(",")
if args.type:
    filters["type"] = args.type.split(",")
if args.search:
    filters["search"] = args.search
filters["limit"] = args.limit or 20

tasks = backend.listTasks(filters)
```

### Step 3: Display

```python
info = backend.getBackendInfo()

# Header
print(f"TaskFlow Tasks ({info['type']})")
if info.get("externalUrl"):
    print(f"→ {info['externalUrl']}")
print()

# Group by status
for status in ["in_progress", "pending", "blocked", "done"]:
    group = [t for t in tasks if t["status"] == status]
    if group:
        print(f"{STATUS_LABELS[status]} ({len(group)})")
        for task in group:
            print(formatTask(task))
        print()

# Summary
print(f"Total: {len(tasks)} tasks")
```

---

## Output Format

```
TaskFlow Tasks (plane)
→ https://plane.internal.muhaha.dev/gsdev/work

In Progress (2)
● [HIGH] task-001: Implement user authentication
● [MED]  task-002: Add input validation

Pending (3)
○ [HIGH] task-003: Create API endpoints
○ [MED]  task-004: Write unit tests
○ [LOW]  task-005: Update documentation

Done (1)
✓ task-006: Set up project structure

Total: 6 tasks
```

---

## Examples

```bash
/task-list                              # All tasks
/task-list --status=pending             # Pending only
/task-list --priority=high              # High priority
/task-list --search="auth"              # Search
/task-list --type=epic                  # Epics only
```

---

**Command Version:** 2.0
