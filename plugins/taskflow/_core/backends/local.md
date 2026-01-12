# TaskFlow Local Backend

Implementation of the backend interface for local `.tasks/` storage.

---

## Overview

The local backend stores tasks in JSON files within a `.tasks/` directory. This is the fallback when no external issue trackers are available.

```
.tasks/
├── config.json          # Project config (optional overrides)
├── state.json           # Current state (active task, etc.)
└── tasks.json           # All tasks
```

---

## Data Storage

### tasks.json Schema

```json
{
  "version": "2.0",
  "project": "my-project",
  "created": "2024-01-15T10:00:00Z",
  "updated": "2024-01-15T14:30:00Z",
  "tasks": [
    {
      "id": "task-001",
      "title": "Implement user authentication",
      "description": "Add JWT-based auth flow",
      "status": "in_progress",
      "priority": "high",
      "type": "epic",
      "parentId": null,
      "dependencies": [],
      "acceptanceCriteria": [
        "Login endpoint works",
        "Token refresh implemented"
      ],
      "notes": [
        {
          "id": "note-001",
          "timestamp": "2024-01-15T10:30:00Z",
          "type": "started",
          "content": "Beginning auth implementation",
          "author": "claude"
        }
      ],
      "createdAt": "2024-01-15T10:00:00Z",
      "updatedAt": "2024-01-15T14:30:00Z",
      "createdBy": "claude"
    }
  ]
}
```

### state.json Schema

```json
{
  "version": "2.0",
  "activeTaskId": "task-001",
  "lastAccessed": "2024-01-15T14:30:00Z"
}
```

---

## Operation Implementations

### createTask(input: CreateTaskInput) → Task

```python
def createTask(input):
    tasks_file = ".tasks/tasks.json"
    data = readJSON(tasks_file)

    # Generate next ID
    existing_ids = [t["id"] for t in data["tasks"]]
    next_num = max([int(id.split("-")[1]) for id in existing_ids], default=0) + 1
    new_id = f"task-{next_num:03d}"

    # Create task object
    now = datetime.now().isoformat() + "Z"
    task = {
        "id": new_id,
        "title": input.title,
        "description": input.description or "",
        "status": "pending_review" if input.requiresReview else "pending",
        "priority": input.priority or "medium",
        "type": input.type or "task",
        "parentId": input.parentId,
        "dependencies": input.dependencies or [],
        "acceptanceCriteria": input.acceptanceCriteria or [],
        "notes": [],
        "createdAt": now,
        "updatedAt": now,
        "createdBy": input.createdBy
    }

    # Add creation note if agent-created
    if input.createdBy:
        task["notes"].append({
            "id": f"note-{uuid4().hex[:8]}",
            "timestamp": now,
            "type": "started",
            "content": f"Task created by {input.createdBy}",
            "author": input.createdBy
        })

    data["tasks"].append(task)
    data["updated"] = now
    writeJSON(tasks_file, data)

    return task
```

---

### getTask(id: string) → Task | null

```python
def getTask(id):
    data = readJSON(".tasks/tasks.json")
    for task in data["tasks"]:
        if task["id"] == id:
            return task
    return None
```

---

### updateTask(id: string, updates: Partial<Task>) → Task

```python
def updateTask(id, updates):
    data = readJSON(".tasks/tasks.json")
    now = datetime.now().isoformat() + "Z"

    for i, task in enumerate(data["tasks"]):
        if task["id"] == id:
            # Apply updates (excluding id, notes, createdAt)
            for key, value in updates.items():
                if key not in ["id", "notes", "createdAt"]:
                    task[key] = value
            task["updatedAt"] = now
            data["updated"] = now
            writeJSON(".tasks/tasks.json", data)
            return task

    raise TaskNotFoundError(id)
```

---

### deleteTask(id: string) → void

```python
def deleteTask(id):
    data = readJSON(".tasks/tasks.json")

    # Find and remove task
    for i, task in enumerate(data["tasks"]):
        if task["id"] == id:
            data["tasks"].pop(i)
            data["updated"] = datetime.now().isoformat() + "Z"
            writeJSON(".tasks/tasks.json", data)
            return

    raise TaskNotFoundError(id)
```

---

### setStatus(id: string, status: TaskStatus, note?: string) → Task

```python
def setStatus(id, status, note=None):
    data = readJSON(".tasks/tasks.json")
    now = datetime.now().isoformat() + "Z"

    for task in data["tasks"]:
        if task["id"] == id:
            old_status = task["status"]
            task["status"] = status
            task["updatedAt"] = now

            # Auto-add note based on transition
            note_type = STATUS_NOTE_MAP.get((old_status, status), "progress")
            if note:
                task["notes"].append({
                    "id": f"note-{uuid4().hex[:8]}",
                    "timestamp": now,
                    "type": note_type,
                    "content": note,
                    "author": "claude"
                })

            data["updated"] = now
            writeJSON(".tasks/tasks.json", data)
            return task

    raise TaskNotFoundError(id)

# Status transition → note type mapping
STATUS_NOTE_MAP = {
    ("pending", "in_progress"): "started",
    ("in_progress", "done"): "completed",
    ("in_progress", "blocked"): "blocked",
    ("blocked", "in_progress"): "unblocked",
    ("blocked", "pending"): "unblocked",
}
```

---

### addNote(id: string, content: string, type: NoteType) → Note

```python
def addNote(id, content, note_type):
    data = readJSON(".tasks/tasks.json")
    now = datetime.now().isoformat() + "Z"

    for task in data["tasks"]:
        if task["id"] == id:
            note = {
                "id": f"note-{uuid4().hex[:8]}",
                "timestamp": now,
                "type": note_type,
                "content": content,
                "author": "claude"
            }
            task["notes"].append(note)
            task["updatedAt"] = now
            data["updated"] = now
            writeJSON(".tasks/tasks.json", data)
            return note

    raise TaskNotFoundError(id)
```

---

### getNotes(id: string) → Note[]

```python
def getNotes(id):
    task = getTask(id)
    if task:
        return task.get("notes", [])
    raise TaskNotFoundError(id)
```

---

### listTasks(filters?: TaskFilters) → Task[]

```python
def listTasks(filters=None):
    data = readJSON(".tasks/tasks.json")
    tasks = data["tasks"]

    if not filters:
        return tasks

    # Apply filters
    if filters.get("status"):
        tasks = [t for t in tasks if t["status"] in filters["status"]]

    if filters.get("priority"):
        tasks = [t for t in tasks if t["priority"] in filters["priority"]]

    if filters.get("type"):
        tasks = [t for t in tasks if t["type"] in filters["type"]]

    if filters.get("parentId"):
        tasks = [t for t in tasks if t["parentId"] == filters["parentId"]]

    if filters.get("createdBy"):
        tasks = [t for t in tasks if t.get("createdBy") == filters["createdBy"]]

    if filters.get("search"):
        query = filters["search"].lower()
        tasks = [t for t in tasks
                 if query in t["title"].lower()
                 or query in t.get("description", "").lower()]

    # Pagination
    if filters.get("offset"):
        tasks = tasks[filters["offset"]:]
    if filters.get("limit"):
        tasks = tasks[:filters["limit"]]

    return tasks
```

---

### searchTasks(query: string) → Task[]

```python
def searchTasks(query):
    return listTasks({"search": query})
```

---

### createEpic(title: string, description?: string) → Task

```python
def createEpic(title, description=None):
    return createTask({
        "title": title,
        "description": description,
        "type": "epic",
        "priority": "high"
    })
```

---

### addSubtask(epicId: string, task: CreateTaskInput) → Task

```python
def addSubtask(epicId, task_input):
    # Verify parent exists and is an epic
    parent = getTask(epicId)
    if not parent:
        raise TaskNotFoundError(epicId)
    if parent["type"] != "epic":
        raise ValidationError("parentId", "Parent must be an epic")

    # Create subtask with parent reference
    task_input["parentId"] = epicId
    task_input["type"] = "subtask"
    return createTask(task_input)
```

---

### linkDependency(taskId: string, dependsOnId: string) → void

```python
def linkDependency(taskId, dependsOnId):
    data = readJSON(".tasks/tasks.json")

    # Verify both tasks exist
    task = None
    depends_on = None
    for t in data["tasks"]:
        if t["id"] == taskId:
            task = t
        if t["id"] == dependsOnId:
            depends_on = t

    if not task:
        raise TaskNotFoundError(taskId)
    if not depends_on:
        raise TaskNotFoundError(dependsOnId)

    # Add dependency if not already present
    if dependsOnId not in task.get("dependencies", []):
        task.setdefault("dependencies", []).append(dependsOnId)
        task["updatedAt"] = datetime.now().isoformat() + "Z"
        writeJSON(".tasks/tasks.json", data)
```

---

### sync() → void

```python
def sync():
    # Local backend is always in sync - no-op
    pass
```

---

### getBackendInfo() → BackendInfo

```python
def getBackendInfo():
    config = readJSON(".tasks/config.json") if exists(".tasks/config.json") else {}
    data = readJSON(".tasks/tasks.json") if exists(".tasks/tasks.json") else {"tasks": []}

    return {
        "type": "local",
        "name": "Local (.tasks/)",
        "connected": True,
        "project": config.get("projectName", os.path.basename(os.getcwd())),
        "supportsEpics": True,
        "supportsSubtasks": True,
        "taskCount": len(data.get("tasks", []))
    }
```

---

## Initialization

### init(projectName?: string) → void

Called when TaskFlow is first set up in a directory.

```python
def init(projectName=None):
    project = projectName or os.path.basename(os.getcwd())
    now = datetime.now().isoformat() + "Z"

    # Create .tasks directory
    os.makedirs(".tasks", exist_ok=True)

    # Create tasks.json
    tasks_data = {
        "version": "2.0",
        "project": project,
        "created": now,
        "updated": now,
        "tasks": []
    }
    writeJSON(".tasks/tasks.json", tasks_data)

    # Create state.json
    state_data = {
        "version": "2.0",
        "activeTaskId": None,
        "lastAccessed": now
    }
    writeJSON(".tasks/state.json", state_data)

    # Create config.json (optional overrides)
    config_data = {
        "projectName": project
    }
    writeJSON(".tasks/config.json", config_data)
```

---

## Helper Functions

```python
import json
import os
from datetime import datetime
from uuid import uuid4

def readJSON(path):
    with open(path, 'r') as f:
        return json.load(f)

def writeJSON(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def exists(path):
    return os.path.exists(path)
```

---

## Error Classes

```python
class TaskNotFoundError(Exception):
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")

class ValidationError(Exception):
    def __init__(self, field, reason):
        self.field = field
        self.reason = reason
        super().__init__(f"Validation error on {field}: {reason}")
```

---

**Backend Version:** 2.0
**Storage Format:** JSON files in `.tasks/`
