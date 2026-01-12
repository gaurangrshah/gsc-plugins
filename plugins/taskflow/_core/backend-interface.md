# TaskFlow Backend Interface v2.0

Standard interface that all TaskFlow backends must implement.

---

## Overview

TaskFlow commands interact with tasks through this abstraction layer. Each backend (Local, Plane, GitHub, Linear) implements these operations, translating them to their native API.

```
┌─────────────────────────────────────────────────────────────┐
│                    TaskFlow Commands                        │
│         /task-add  /task-done  /task-list  etc.            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend Interface                         │
│    createTask() setStatus() addNote() listTasks() etc.     │
└─────────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │  Local   │       │  Plane   │       │  GitHub  │
   │ .tasks/  │       │   MCP    │       │    gh    │
   └──────────┘       └──────────┘       └──────────┘
```

---

## Data Types

### Task

```yaml
Task:
  id: string              # Unique identifier (backend-specific format)
  title: string           # Task title (action-oriented)
  description: string     # Detailed description
  status: TaskStatus      # Current status
  priority: Priority      # high | medium | low
  type: TaskType          # task | epic | subtask

  # Relationships
  parentId: string?       # Parent epic/task ID (if subtask)
  dependencies: string[]  # IDs of tasks that must complete first

  # Metadata
  createdAt: ISO8601
  updatedAt: ISO8601
  createdBy: string?      # Agent or user who created

  # Acceptance criteria
  acceptanceCriteria: string[]

  # Notes/comments history
  notes: Note[]

  # Backend-specific
  externalId: string?     # Issue number, URL, etc.
  externalUrl: string?    # Link to view in external system
```

### TaskStatus

```yaml
TaskStatus:
  - pending         # Not started
  - in_progress     # Currently being worked on
  - done            # Completed
  - blocked         # Waiting on something
  - deferred        # Postponed for later
  - cancelled       # Will not be done
  - pending_review  # Agent-created, awaiting approval
```

### Priority

```yaml
Priority:
  - high    # Urgent, blocks others, foundational
  - medium  # Important, standard priority
  - low     # Nice-to-have, no blockers
```

### TaskType

```yaml
TaskType:
  - epic     # Large task with children (PRD-level)
  - task     # Standard task
  - subtask  # Child of another task
```

### Note

```yaml
Note:
  id: string
  timestamp: ISO8601
  type: NoteType
  content: string
  author: string?       # Agent or user
```

### NoteType

```yaml
NoteType:
  - started       # Work began
  - progress      # Progress update
  - decision      # Decision made (why this approach)
  - gotcha        # Surprise/unexpected finding
  - workaround    # Hack/technical debt noted
  - blocked       # Why blocked
  - unblocked     # How unblocked
  - completed     # Completion notes
  - reference     # Links, PRs, commits
  - review        # Agent review feedback
```

### TaskFilters

```yaml
TaskFilters:
  status: TaskStatus[]?    # Filter by status(es)
  priority: Priority[]?    # Filter by priority
  type: TaskType[]?        # Filter by type
  parentId: string?        # Get children of specific task
  createdBy: string?       # Filter by creator
  search: string?          # Full-text search
  limit: number?           # Max results
  offset: number?          # Pagination
```

### CreateTaskInput

```yaml
CreateTaskInput:
  title: string                    # Required
  description: string?
  priority: Priority?              # Default: medium
  type: TaskType?                  # Default: task
  parentId: string?                # If creating subtask
  dependencies: string[]?
  acceptanceCriteria: string[]?
  createdBy: string?               # Agent name if agent-created
  requiresReview: boolean?         # If true, starts as pending_review
```

---

## Required Operations

Every backend MUST implement these operations.

### Task CRUD

#### createTask(input: CreateTaskInput) → Task

Create a new task/issue.

```yaml
Input:
  title: "Add JWT token handling"
  description: "Implement JWT generation and validation"
  priority: high
  acceptanceCriteria:
    - "Tokens expire after 1 hour"
    - "Refresh tokens supported"

Output:
  id: "task-123"
  title: "Add JWT token handling"
  status: pending
  externalId: "WORK-456"
  externalUrl: "https://plane.internal/issue/WORK-456"
  ...
```

**Backend translations:**
- Local: Append to tasks.json, assign next ID
- Plane: `mcp__plane__create_issue(name, description, priority, labels)`
- GitHub: `gh issue create --title --body --label`

---

#### getTask(id: string) → Task | null

Retrieve a single task by ID.

**Backend translations:**
- Local: Find in tasks.json by ID
- Plane: `mcp__plane__get_issue(issue_id)`
- GitHub: `gh issue view {id} --json`

---

#### updateTask(id: string, updates: Partial<Task>) → Task

Update task fields (title, description, priority, etc.).

**Backend translations:**
- Local: Modify tasks.json entry
- Plane: `mcp__plane__update_issue(issue_id, ...)`
- GitHub: `gh issue edit {id} --title --body`

---

#### deleteTask(id: string) → void

Remove or cancel a task.

**Backend translations:**
- Local: Remove from tasks.json (or mark cancelled)
- Plane: Update state to "Cancelled"
- GitHub: `gh issue close {id}` with "cancelled" label

---

### Status Management

#### setStatus(id: string, status: TaskStatus, note?: string) → Task

Change task status with optional note.

```yaml
Input:
  id: "task-123"
  status: done
  note: "Completed. Gotcha: needed to handle token refresh edge case."

Behavior:
  1. Update task status
  2. Add note with type based on status transition
  3. Sync to external system
  4. Return updated task
```

**Status → Note type mapping:**
- → in_progress: "started"
- → done: "completed"
- → blocked: "blocked"
- → pending (from blocked): "unblocked"

**Backend translations:**
- Local: Update status field, append note
- Plane: `mcp__plane__update_issue(state_id)` + `add_comment()`
- GitHub: Label changes + `gh issue comment`

---

#### getStatus(id: string) → TaskStatus

Get current status of a task.

---

### Notes & Comments

#### addNote(id: string, content: string, type: NoteType) → Note

Add a note/comment to a task.

```yaml
Input:
  id: "task-123"
  content: "Decided to use jose library instead of jsonwebtoken"
  type: decision

Output:
  id: "note-456"
  timestamp: "2024-01-15T14:30:00Z"
  type: decision
  content: "Decided to use jose library instead of jsonwebtoken"
```

**Backend translations:**
- Local: Append to task.notes array
- Plane: `mcp__plane__add_comment()` with formatted content
- GitHub: `gh issue comment` with type prefix

---

#### getNotes(id: string) → Note[]

Get all notes for a task.

---

### Listing & Search

#### listTasks(filters?: TaskFilters) → Task[]

List tasks with optional filtering.

```yaml
Input:
  filters:
    status: [pending, in_progress]
    priority: [high]

Output:
  - id: "task-1", title: "Set up auth", status: in_progress, ...
  - id: "task-2", title: "Add validation", status: pending, ...
```

**Backend translations:**
- Local: Filter tasks.json in memory
- Plane: `mcp__plane__list_issues(state, priority)`
- GitHub: `gh issue list --state --label`

---

#### searchTasks(query: string) → Task[]

Full-text search across task titles and descriptions.

---

### Hierarchy & Dependencies

#### createEpic(title: string, description?: string) → Task

Create an epic (parent task for grouping).

**Backend translations:**
- Local: Create task with type="epic"
- Plane: Create issue + Module, or parent issue
- GitHub: Create issue with "epic" label

---

#### addSubtask(epicId: string, task: CreateTaskInput) → Task

Create a subtask under an epic.

**Backend translations:**
- Local: Create task with parentId set
- Plane: Create issue, link to parent
- GitHub: Create issue, reference parent in body

---

#### linkDependency(taskId: string, dependsOnId: string) → void

Mark that taskId depends on dependsOnId.

**Backend translations:**
- Local: Add to dependencies array
- Plane: Issue link
- GitHub: Reference in body or linked issues

---

### Sync & Metadata

#### sync() → void

Force sync with external system (if applicable).

- Local: No-op (already in sync)
- Plane/GitHub: Fetch latest state from remote

---

#### getBackendInfo() → BackendInfo

Return information about the current backend.

```yaml
Output:
  type: "plane"
  name: "Plane"
  connected: true
  workspace: "gsdev"
  project: "work"
  supportsEpics: true
  supportsSubtasks: true
  externalUrl: "https://plane.internal.muhaha.dev/gsdev/work"
```

---

## Optional Operations

Backends MAY implement these if supported.

#### importTasks(tasks: Task[]) → Task[]

Bulk import tasks (e.g., from PRD parse or migration).

#### exportTasks(filters?: TaskFilters) → Task[]

Export tasks for backup or migration.

#### getMetrics() → Metrics

Return task statistics (counts by status, priority, etc.).

---

## Error Handling

All operations should throw typed errors:

```yaml
TaskNotFoundError:
  message: "Task not found"
  taskId: string

BackendConnectionError:
  message: "Failed to connect to backend"
  backend: string
  cause: string

ValidationError:
  message: "Invalid input"
  field: string
  reason: string

PermissionError:
  message: "Not authorized"
  operation: string
```

---

## Backend Detection

To detect available backends:

```bash
# Plane MCP available?
mcp__plane__list_projects exists → Plane available

# GitHub CLI available and authenticated?
gh auth status → GitHub available

# Linear MCP available?
mcp__linear__* exists → Linear available

# Local always available
.tasks/ can be created → Local available
```

---

**Interface Version:** 2.0
**Used By:** All TaskFlow commands
