# TaskFlow GitHub Backend

Implementation of the backend interface for GitHub Issues.

---

## Overview

The GitHub backend syncs tasks with GitHub Issues using the `gh` CLI. Tasks map to issues, epics map to issues with the "epic" label.

```
TaskFlow Task  ←→  GitHub Issue
TaskFlow Epic  ←→  GitHub Issue + "epic" label
TaskFlow Note  ←→  GitHub Issue Comment
```

---

## Configuration

```yaml
# In .taskflow.local.md or ~/.gsc-plugins/taskflow.local.md
backend: github

github:
  owner: myuser           # Repository owner
  repo: my-project        # Repository name
  defaultLabels:          # Optional: labels for new issues
    - taskflow
```

---

## Status Mapping

GitHub Issues only have `open` and `closed` states. TaskFlow uses labels to track detailed status.

| TaskFlow Status | GitHub State | GitHub Label |
|-----------------|--------------|--------------|
| pending | open | `status:pending` |
| in_progress | open | `status:in-progress` |
| done | closed | (none needed) |
| blocked | open | `status:blocked` |
| deferred | open | `status:deferred` |
| cancelled | closed | `status:cancelled` |
| pending_review | open | `status:pending-review` |

---

## Priority Mapping

| TaskFlow Priority | GitHub Label |
|-------------------|--------------|
| high | `priority:high` |
| medium | `priority:medium` |
| low | `priority:low` |

---

## Operation Implementations

### createTask(input: CreateTaskInput) → Task

```bash
# Build labels
LABELS="taskflow"
[ -n "$PRIORITY" ] && LABELS="$LABELS,priority:$PRIORITY"
[ "$REQUIRES_REVIEW" = "true" ] && LABELS="$LABELS,status:pending-review"

# Build body with acceptance criteria
BODY="$DESCRIPTION"
if [ -n "$ACCEPTANCE_CRITERIA" ]; then
    BODY="$BODY

## Acceptance Criteria
$ACCEPTANCE_CRITERIA"
fi

# Create issue
gh issue create \
    --repo "$OWNER/$REPO" \
    --title "$TITLE" \
    --body "$BODY" \
    --label "$LABELS"
```

```python
def createTask(input):
    config = loadConfig()

    # Build labels
    labels = config.github.get("defaultLabels", ["taskflow"])
    if input.priority:
        labels.append(f"priority:{input.priority}")
    if input.requiresReview:
        labels.append("status:pending-review")
    else:
        labels.append("status:pending")

    # Build body
    body = input.description or ""
    if input.acceptanceCriteria:
        body += "\n\n## Acceptance Criteria\n"
        for criterion in input.acceptanceCriteria:
            body += f"- [ ] {criterion}\n"

    # Create via gh CLI
    result = bash(f'''
        gh issue create \
            --repo {config.github.owner}/{config.github.repo} \
            --title "{escape(input.title)}" \
            --body "{escape(body)}" \
            --label "{','.join(labels)}" \
            --json number,title,body,state,labels,createdAt,updatedAt
    ''')

    return ghToTask(json.loads(result))
```

---

### getTask(id: string) → Task | null

```python
def getTask(id):
    config = loadConfig()

    try:
        result = bash(f'''
            gh issue view {id} \
                --repo {config.github.owner}/{config.github.repo} \
                --json number,title,body,state,labels,createdAt,updatedAt,comments
        ''')
        return ghToTask(json.loads(result))
    except:
        return None
```

---

### updateTask(id: string, updates: Partial<Task>) → Task

```python
def updateTask(id, updates):
    config = loadConfig()

    args = []

    if "title" in updates:
        args.append(f'--title "{escape(updates["title"])}"')

    if "description" in updates:
        args.append(f'--body "{escape(updates["description"])}"')

    if args:
        bash(f'''
            gh issue edit {id} \
                --repo {config.github.owner}/{config.github.repo} \
                {' '.join(args)}
        ''')

    # Handle label updates separately
    if "priority" in updates:
        # Remove old priority labels, add new one
        bash(f'''
            gh issue edit {id} \
                --repo {config.github.owner}/{config.github.repo} \
                --remove-label "priority:high,priority:medium,priority:low" \
                --add-label "priority:{updates['priority']}"
        ''')

    return getTask(id)
```

---

### deleteTask(id: string) → void

```python
def deleteTask(id):
    # GitHub issues can't be deleted via API, close with cancelled label
    setStatus(id, "cancelled", "Task cancelled via TaskFlow")
```

---

### setStatus(id: string, status: TaskStatus, note?: string) → Task

```python
def setStatus(id, status, note=None):
    config = loadConfig()

    # Remove all status labels first
    status_labels = "status:pending,status:in-progress,status:blocked,status:deferred,status:pending-review,status:cancelled"

    if status == "done":
        # Close issue
        bash(f'''
            gh issue close {id} \
                --repo {config.github.owner}/{config.github.repo} \
                --reason completed
        ''')
        bash(f'''
            gh issue edit {id} \
                --repo {config.github.owner}/{config.github.repo} \
                --remove-label "{status_labels}"
        ''')
    elif status == "cancelled":
        # Close with cancelled label
        bash(f'''
            gh issue close {id} \
                --repo {config.github.owner}/{config.github.repo} \
                --reason "not planned"
        ''')
        bash(f'''
            gh issue edit {id} \
                --repo {config.github.owner}/{config.github.repo} \
                --remove-label "{status_labels}" \
                --add-label "status:cancelled"
        ''')
    else:
        # Reopen if closed, update label
        bash(f'''
            gh issue reopen {id} \
                --repo {config.github.owner}/{config.github.repo} 2>/dev/null || true
        ''')
        label = STATUS_TO_LABEL.get(status, "status:pending")
        bash(f'''
            gh issue edit {id} \
                --repo {config.github.owner}/{config.github.repo} \
                --remove-label "{status_labels}" \
                --add-label "{label}"
        ''')

    # Add comment if note provided
    if note:
        addNote(id, note, STATUS_NOTE_MAP.get(status, "progress"))

    return getTask(id)
```

---

### addNote(id: string, content: string, type: NoteType) → Note

```python
def addNote(id, content, note_type):
    config = loadConfig()

    # Format comment with type prefix
    formatted = f"**[{note_type.upper()}]** {content}"

    bash(f'''
        gh issue comment {id} \
            --repo {config.github.owner}/{config.github.repo} \
            --body "{escape(formatted)}"
    ''')

    return {
        "id": f"comment-{uuid4().hex[:8]}",
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

    result = bash(f'''
        gh issue view {id} \
            --repo {config.github.owner}/{config.github.repo} \
            --json comments
    ''')

    data = json.loads(result)
    notes = []

    for comment in data.get("comments", []):
        body = comment.get("body", "")
        note_type = "progress"

        # Parse type from **[TYPE]** prefix
        import re
        match = re.match(r'\*\*\[(\w+)\]\*\*\s*(.*)', body, re.DOTALL)
        if match:
            note_type = match.group(1).lower()
            body = match.group(2)

        notes.append({
            "id": comment.get("id", ""),
            "timestamp": comment.get("createdAt", ""),
            "type": note_type,
            "content": body,
            "author": comment.get("author", {}).get("login", "unknown")
        })

    return notes
```

---

### listTasks(filters?: TaskFilters) → Task[]

```python
def listTasks(filters=None):
    config = loadConfig()

    # Build gh issue list command
    args = ["--json", "number,title,body,state,labels,createdAt,updatedAt"]

    if filters:
        if filters.get("status"):
            # Map to GitHub state
            if "done" in filters["status"] or "cancelled" in filters["status"]:
                args.append("--state closed")
            elif any(s in filters["status"] for s in ["pending", "in_progress", "blocked"]):
                args.append("--state open")

        if filters.get("search"):
            args.append(f'--search "{filters["search"]}"')

        if filters.get("limit"):
            args.append(f'--limit {filters["limit"]}')
        else:
            args.append("--limit 50")

    result = bash(f'''
        gh issue list \
            --repo {config.github.owner}/{config.github.repo} \
            {' '.join(args)}
    ''')

    issues = json.loads(result)
    tasks = [ghToTask(issue) for issue in issues]

    # Apply filters that gh doesn't support directly
    if filters:
        if filters.get("status"):
            tasks = [t for t in tasks if t["status"] in filters["status"]]

        if filters.get("priority"):
            tasks = [t for t in tasks if t["priority"] in filters["priority"]]

        if filters.get("type"):
            tasks = [t for t in tasks if t["type"] in filters["type"]]

        if filters.get("offset"):
            tasks = tasks[filters["offset"]:]

    return tasks
```

---

### searchTasks(query: string) → Task[]

```python
def searchTasks(query):
    return listTasks({"search": query, "limit": 50})
```

---

### createEpic(title: string, description?: string) → Task

```python
def createEpic(title, description=None):
    config = loadConfig()

    task = createTask({
        "title": title,
        "description": description,
        "priority": "high"
    })

    # Add epic label
    bash(f'''
        gh issue edit {task["id"]} \
            --repo {config.github.owner}/{config.github.repo} \
            --add-label "epic"
    ''')

    task["type"] = "epic"
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

    # Create subtask with reference to parent
    body = task_input.get("description", "") or ""
    body += f"\n\nParent: #{epicId}"

    task_input["description"] = body
    task = createTask(task_input)

    # Add subtask label
    bash(f'''
        gh issue edit {task["id"]} \
            --repo {config.github.owner}/{config.github.repo} \
            --add-label "subtask"
    ''')

    # Add reference comment to parent
    addNote(epicId, f"Subtask created: #{task['id']} - {task['title']}", "reference")

    return task
```

---

### linkDependency(taskId: string, dependsOnId: string) → void

```python
def linkDependency(taskId, dependsOnId):
    depends_on = getTask(dependsOnId)
    if not depends_on:
        raise TaskNotFoundError(dependsOnId)

    addNote(taskId, f"Depends on: #{dependsOnId} - {depends_on['title']}", "reference")
```

---

### sync() → void

```python
def sync():
    # gh CLI always fetches fresh data - no-op
    pass
```

---

### getBackendInfo() → BackendInfo

```python
def getBackendInfo():
    config = loadConfig()

    # Verify connection
    try:
        bash("gh auth status")
        connected = True
    except:
        connected = False

    return {
        "type": "github",
        "name": "GitHub Issues",
        "connected": connected,
        "owner": config.github.owner,
        "repo": config.github.repo,
        "supportsEpics": True,
        "supportsSubtasks": True,
        "externalUrl": f"https://github.com/{config.github.owner}/{config.github.repo}/issues"
    }
```

---

## Conversion Functions

### ghToTask(issue: GitHubIssue) → Task

```python
def ghToTask(issue):
    """Convert GitHub issue to TaskFlow task format."""

    labels = [l.get("name", "") for l in issue.get("labels", [])]

    # Determine status from labels and state
    status = "pending"
    if issue.get("state") == "closed":
        status = "cancelled" if "status:cancelled" in labels else "done"
    else:
        for label in labels:
            if label.startswith("status:"):
                status = LABEL_TO_STATUS.get(label, "pending")
                break

    # Determine priority from labels
    priority = "medium"
    for label in labels:
        if label.startswith("priority:"):
            priority = label.split(":")[1]
            break

    # Determine type
    task_type = "task"
    if "epic" in labels:
        task_type = "epic"
    elif "subtask" in labels:
        task_type = "subtask"

    return {
        "id": str(issue.get("number")),
        "title": issue.get("title", ""),
        "description": issue.get("body", ""),
        "status": status,
        "priority": priority,
        "type": task_type,
        "parentId": None,  # Would need to parse from body
        "dependencies": [],
        "acceptanceCriteria": [],  # Would need to parse from body
        "notes": [],  # Loaded separately
        "createdAt": issue.get("createdAt", ""),
        "updatedAt": issue.get("updatedAt", ""),
        "createdBy": issue.get("author", {}).get("login"),
        "externalId": f"#{issue.get('number')}",
        "externalUrl": issue.get("url", f"https://github.com/owner/repo/issues/{issue.get('number')}")
    }
```

---

## Mappings

```python
# TaskFlow status → GitHub label
STATUS_TO_LABEL = {
    "pending": "status:pending",
    "in_progress": "status:in-progress",
    "blocked": "status:blocked",
    "deferred": "status:deferred",
    "pending_review": "status:pending-review",
    "cancelled": "status:cancelled"
}

# GitHub label → TaskFlow status
LABEL_TO_STATUS = {
    "status:pending": "pending",
    "status:in-progress": "in_progress",
    "status:blocked": "blocked",
    "status:deferred": "deferred",
    "status:pending-review": "pending_review",
    "status:cancelled": "cancelled"
}

# Status → note type
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
    """Check if GitHub backend is available."""
    try:
        result = bash("gh auth status 2>&1")
        return "Logged in" in result
    except:
        return False

def detectConfig():
    """Auto-detect GitHub configuration from current repo."""
    try:
        # Check if in a git repo with GitHub remote
        result = bash("gh repo view --json owner,name 2>/dev/null")
        data = json.loads(result)
        return {
            "owner": data["owner"]["login"],
            "repo": data["name"],
            "detected": True
        }
    except:
        return {"detected": False}
```

---

## Label Setup

For full status tracking, create these labels in your GitHub repo:

```bash
# Status labels
gh label create "status:pending" --color "FBCA04" --description "Task not started"
gh label create "status:in-progress" --color "0E8A16" --description "Task in progress"
gh label create "status:blocked" --color "D93F0B" --description "Task blocked"
gh label create "status:deferred" --color "C5DEF5" --description "Task deferred"
gh label create "status:pending-review" --color "FBCA04" --description "Awaiting review"
gh label create "status:cancelled" --color "E4E669" --description "Task cancelled"

# Priority labels
gh label create "priority:high" --color "B60205" --description "High priority"
gh label create "priority:medium" --color "FBCA04" --description "Medium priority"
gh label create "priority:low" --color "0E8A16" --description "Low priority"

# Type labels
gh label create "epic" --color "3E4B9E" --description "Epic/parent task"
gh label create "subtask" --color "BFD4F2" --description "Subtask"
gh label create "taskflow" --color "7057FF" --description "Managed by TaskFlow"
```

---

**Backend Version:** 2.0
**Requires:** GitHub CLI (`gh`) authenticated
