# TaskFlow Plane Backend

Implementation of the backend interface for Plane issue tracking.

---

## Overview

The Plane backend syncs tasks with Plane issues using MCP tools. Tasks in TaskFlow map directly to Plane issues.

```
TaskFlow Task  ←→  Plane Issue
TaskFlow Epic  ←→  Plane Issue + Module (or parent link)
TaskFlow Note  ←→  Plane Comment
```

---

## Configuration

```yaml
# In .taskflow.local.md or ~/.gsc-plugins/taskflow.local.md
backend: plane

plane:
  workspace: gsdev
  project: work
  module: my-feature    # Optional: default module for new issues
  defaultState: Backlog # Optional: default state for new issues
  defaultLabels:        # Optional: default labels
    - taskflow
```

---

## Status Mapping

| TaskFlow Status | Plane State Group | Plane State |
|-----------------|-------------------|-------------|
| pending | backlog | Backlog |
| in_progress | started | In Progress |
| done | completed | Done |
| blocked | started | Blocked (custom) |
| deferred | backlog | Deferred (custom) |
| cancelled | cancelled | Cancelled |
| pending_review | started | In Review (custom) |

**Note:** Custom states must be created in Plane project settings.

---

## Priority Mapping

| TaskFlow Priority | Plane Priority |
|-------------------|----------------|
| high | urgent |
| medium | medium |
| low | low |

---

## Operation Implementations

### createTask(input: CreateTaskInput) → Task

```python
def createTask(input):
    config = loadConfig()

    # Map priority
    plane_priority = PRIORITY_MAP.get(input.priority, "medium")

    # Get default state
    state = input.get("state") or config.plane.get("defaultState", "Backlog")

    # Get labels (include defaults + any specified)
    labels = config.plane.get("defaultLabels", [])
    if input.get("labels"):
        labels.extend(input["labels"])
    if not labels:
        labels = ["taskflow"]  # Require at least one label

    # Build description with acceptance criteria
    description = input.description or ""
    if input.acceptanceCriteria:
        description += "\n\n## Acceptance Criteria\n"
        for criterion in input.acceptanceCriteria:
            description += f"- [ ] {criterion}\n"

    # Create issue via MCP
    result = mcp__plane__create_issue(
        workspace_slug=config.plane.workspace,
        project_id=config.plane.project,
        name=input.title,
        description=description,
        priority=plane_priority,
        state=state,
        labels=labels
    )

    # If module specified, add to module
    if config.plane.get("module"):
        mcp__plane__add_issue_to_module(
            workspace_slug=config.plane.workspace,
            project_id=config.plane.project,
            module_id=config.plane.module,
            issue_id=result["id"]
        )

    # Convert to TaskFlow format
    return planeToTask(result)
```

---

### getTask(id: string) → Task | null

```python
def getTask(id):
    config = loadConfig()

    try:
        result = mcp__plane__get_issue(
            workspace_slug=config.plane.workspace,
            project_id=config.plane.project,
            issue_id=id
        )
        return planeToTask(result)
    except:
        return None
```

---

### updateTask(id: string, updates: Partial<Task>) → Task

```python
def updateTask(id, updates):
    config = loadConfig()

    # Build update payload
    payload = {}

    if "title" in updates:
        payload["name"] = updates["title"]

    if "description" in updates:
        payload["description"] = updates["description"]

    if "priority" in updates:
        payload["priority"] = PRIORITY_MAP.get(updates["priority"], "medium")

    if "status" in updates:
        # Need to get state_id from state name
        states = mcp__plane__list_states(
            workspace_slug=config.plane.workspace,
            project_id=config.plane.project
        )
        state_name = STATUS_TO_STATE.get(updates["status"], "Backlog")
        for state in states["results"]:
            if state["name"].lower() == state_name.lower():
                payload["state_id"] = state["id"]
                break

    result = mcp__plane__update_issue(
        workspace_slug=config.plane.workspace,
        project_id=config.plane.project,
        issue_id=id,
        **payload
    )

    return planeToTask(result)
```

---

### deleteTask(id: string) → void

```python
def deleteTask(id):
    # In Plane, we don't delete - we mark as Cancelled
    return setStatus(id, "cancelled", "Task cancelled via TaskFlow")
```

---

### setStatus(id: string, status: TaskStatus, note?: string) → Task

```python
def setStatus(id, status, note=None):
    config = loadConfig()

    # Get state_id for the target status
    states = mcp__plane__list_states(
        workspace_slug=config.plane.workspace,
        project_id=config.plane.project
    )

    state_name = STATUS_TO_STATE.get(status, "Backlog")
    state_id = None
    for state in states["results"]:
        if state["name"].lower() == state_name.lower():
            state_id = state["id"]
            break

    if not state_id:
        raise ValidationError("status", f"No Plane state found for: {status}")

    # Update issue state
    result = mcp__plane__update_issue(
        workspace_slug=config.plane.workspace,
        project_id=config.plane.project,
        issue_id=id,
        state_id=state_id
    )

    # Add comment if note provided
    if note:
        addNote(id, note, STATUS_NOTE_MAP.get(status, "progress"))

    return planeToTask(result)
```

---

### addNote(id: string, content: string, type: NoteType) → Note

```python
def addNote(id, content, note_type):
    config = loadConfig()

    # Format comment with type prefix
    formatted = f"**[{note_type.upper()}]** {content}"

    result = mcp__plane__add_comment(
        workspace_slug=config.plane.workspace,
        project_id=config.plane.project,
        issue_id=id,
        comment=formatted
    )

    return {
        "id": result.get("id", f"comment-{uuid4().hex[:8]}"),
        "timestamp": datetime.now().isoformat() + "Z",
        "type": note_type,
        "content": content,
        "author": "taskflow"
    }
```

---

### getNotes(id: string) → Note[]

```python
def getNotes(id):
    config = loadConfig()

    result = mcp__plane__list_comments(
        workspace_slug=config.plane.workspace,
        project_id=config.plane.project,
        issue_id=id
    )

    notes = []
    for comment in result.get("results", []):
        # Parse note type from comment prefix
        content = comment.get("comment_html", "")
        note_type = "progress"  # default

        # Try to extract type from **[TYPE]** prefix
        import re
        match = re.match(r'\*\*\[(\w+)\]\*\*\s*(.*)', content, re.DOTALL)
        if match:
            note_type = match.group(1).lower()
            content = match.group(2)

        notes.append({
            "id": comment["id"],
            "timestamp": comment.get("created_at", ""),
            "type": note_type,
            "content": content,
            "author": comment.get("actor_id", "unknown")
        })

    return notes
```

---

### listTasks(filters?: TaskFilters) → Task[]

```python
def listTasks(filters=None):
    config = loadConfig()

    # Build Plane filters
    plane_filters = {}

    if filters and filters.get("status"):
        # Map TaskFlow statuses to Plane state names
        state_names = [STATUS_TO_STATE.get(s, s) for s in filters["status"]]
        # Note: Plane API may need state group, not name
        plane_filters["state"] = state_names[0] if len(state_names) == 1 else None

    if filters and filters.get("priority"):
        priorities = [PRIORITY_MAP.get(p, p) for p in filters["priority"]]
        plane_filters["priority"] = priorities[0] if len(priorities) == 1 else None

    result = mcp__plane__list_issues(
        workspace_slug=config.plane.workspace,
        project_id=config.plane.project,
        limit=filters.get("limit", 50) if filters else 50,
        **{k: v for k, v in plane_filters.items() if v is not None}
    )

    tasks = [planeToTask(issue) for issue in result.get("results", [])]

    # Apply filters that Plane API doesn't support
    if filters:
        if filters.get("type"):
            # Filter by epic/task based on whether issue has children
            pass  # Complex - would need sub-issue check

        if filters.get("parentId"):
            tasks = [t for t in tasks if t.get("parentId") == filters["parentId"]]

        if filters.get("search"):
            query = filters["search"].lower()
            tasks = [t for t in tasks
                     if query in t["title"].lower()
                     or query in t.get("description", "").lower()]

        if filters.get("offset"):
            tasks = tasks[filters["offset"]:]

    return tasks
```

---

### searchTasks(query: string) → Task[]

```python
def searchTasks(query):
    # Plane doesn't have native search, so we filter locally
    all_tasks = listTasks({"limit": 100})
    query_lower = query.lower()

    return [t for t in all_tasks
            if query_lower in t["title"].lower()
            or query_lower in t.get("description", "").lower()]
```

---

### createEpic(title: string, description?: string) → Task

```python
def createEpic(title, description=None):
    config = loadConfig()

    # Create issue
    task = createTask({
        "title": title,
        "description": description,
        "priority": "high",
        "labels": ["epic", "taskflow"]
    })

    # If modules are supported, create a module for this epic
    # (Modules in Plane act like feature groups)
    # This is optional - epics can also just be issues with sub-issues

    return task
```

---

### addSubtask(epicId: string, task: CreateTaskInput) → Task

```python
def addSubtask(epicId, task_input):
    config = loadConfig()

    # Verify parent exists
    parent = getTask(epicId)
    if not parent:
        raise TaskNotFoundError(epicId)

    # Create subtask
    task = createTask(task_input)

    # Note: Plane has sub-issues feature
    # The API linkage depends on Plane version
    # For now, we reference parent in description

    # Add reference to parent in description
    updated_desc = task.get("description", "") + f"\n\nParent: {parent['externalId'] or epicId}"
    updateTask(task["id"], {"description": updated_desc})

    # Add note to parent about subtask
    addNote(epicId, f"Subtask created: {task['title']} ({task['id']})", "reference")

    return task
```

---

### linkDependency(taskId: string, dependsOnId: string) → void

```python
def linkDependency(taskId, dependsOnId):
    config = loadConfig()

    # Plane supports issue links
    # Add as comment/reference for now
    depends_on = getTask(dependsOnId)
    if not depends_on:
        raise TaskNotFoundError(dependsOnId)

    addNote(taskId, f"Depends on: {depends_on['title']} ({dependsOnId})", "reference")
```

---

### sync() → void

```python
def sync():
    # Force refresh from Plane - clear any local cache
    # The MCP tools always fetch fresh data, so this is effectively a no-op
    pass
```

---

### getBackendInfo() → BackendInfo

```python
def getBackendInfo():
    config = loadConfig()

    # Verify connection
    try:
        projects = mcp__plane__list_projects(
            workspace_slug=config.plane.workspace
        )
        connected = True
    except:
        connected = False

    return {
        "type": "plane",
        "name": "Plane",
        "connected": connected,
        "workspace": config.plane.workspace,
        "project": config.plane.project,
        "module": config.plane.get("module"),
        "supportsEpics": True,
        "supportsSubtasks": True,
        "externalUrl": f"https://${{PLANE_URL}}/{config.plane.workspace}/{config.plane.project}"
    }
```

---

## Conversion Functions

### planeToTask(issue: PlaneIssue) → Task

```python
def planeToTask(issue):
    """Convert Plane issue to TaskFlow task format."""

    # Map Plane state to TaskFlow status
    state_group = issue.get("state", {}).get("group", "backlog")
    status = STATE_GROUP_TO_STATUS.get(state_group, "pending")

    # Map Plane priority to TaskFlow priority
    plane_priority = issue.get("priority", "medium")
    priority = REVERSE_PRIORITY_MAP.get(plane_priority, "medium")

    # Determine type (epic if has children or "epic" label)
    labels = [l.get("name", "") for l in issue.get("labels", [])]
    task_type = "epic" if "epic" in labels else "task"

    return {
        "id": issue["id"],
        "title": issue.get("name", ""),
        "description": issue.get("description", ""),
        "status": status,
        "priority": priority,
        "type": task_type,
        "parentId": issue.get("parent"),
        "dependencies": [],  # Would need separate API call
        "acceptanceCriteria": [],  # Parse from description if formatted
        "notes": [],  # Loaded separately via getNotes
        "createdAt": issue.get("created_at", ""),
        "updatedAt": issue.get("updated_at", ""),
        "createdBy": issue.get("created_by"),
        "externalId": issue.get("sequence_id"),  # e.g., "WORK-123"
        "externalUrl": f"https://${{PLANE_URL}}/issue/{issue['id']}"
    }
```

---

## Mappings

```python
# TaskFlow status → Plane state name
STATUS_TO_STATE = {
    "pending": "Backlog",
    "in_progress": "In Progress",
    "done": "Done",
    "blocked": "Blocked",
    "deferred": "Deferred",
    "cancelled": "Cancelled",
    "pending_review": "In Review"
}

# Plane state group → TaskFlow status
STATE_GROUP_TO_STATUS = {
    "backlog": "pending",
    "unstarted": "pending",
    "started": "in_progress",
    "completed": "done",
    "cancelled": "cancelled"
}

# TaskFlow priority → Plane priority
PRIORITY_MAP = {
    "high": "urgent",
    "medium": "medium",
    "low": "low"
}

# Plane priority → TaskFlow priority
REVERSE_PRIORITY_MAP = {
    "urgent": "high",
    "high": "high",
    "medium": "medium",
    "low": "low",
    "none": "low"
}

# Status → note type for auto-notes
STATUS_NOTE_MAP = {
    "in_progress": "started",
    "done": "completed",
    "blocked": "blocked",
    "cancelled": "completed"
}
```

---

## Detection

```python
def isAvailable():
    """Check if Plane backend is available."""
    # Check if Plane MCP tools exist
    # This is done by the backend loader
    return tool_exists("mcp__plane__list_issues")

def detectConfig():
    """Auto-detect Plane configuration."""
    try:
        workspaces = mcp__plane__list_workspaces()
        if workspaces.get("results"):
            workspace = workspaces["results"][0]

            projects = mcp__plane__list_projects(
                workspace_slug=workspace["slug"]
            )
            if projects.get("results"):
                project = projects["results"][0]

                return {
                    "workspace": workspace["slug"],
                    "project": project["id"],
                    "detected": True
                }
    except:
        pass

    return {"detected": False}
```

---

**Backend Version:** 2.0
**Requires:** Plane MCP tools (`mcp__plane__*`)
