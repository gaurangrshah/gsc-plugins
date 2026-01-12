# TaskFlow Epic & Issue Strategy

Guidelines for when to create epics vs simple tasks, and how to manage task hierarchies.

---

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         EPIC                                │
│  Large feature or initiative with multiple subtasks         │
│  Example: "User Authentication System"                      │
├─────────────────────────────────────────────────────────────┤
│  ├── TASK: Set up JWT infrastructure                        │
│  ├── TASK: Implement login endpoint                         │
│  ├── TASK: Implement logout endpoint                        │
│  ├── TASK: Add refresh token flow                           │
│  └── TASK: Write auth middleware                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      SIMPLE TASK                            │
│  Standalone work item, no children                          │
│  Example: "Fix typo in README"                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Decision Tree: Epic vs Task

```
Is this from a PRD or large feature spec?
├─ YES → Create EPIC
│        └─ Parse subtasks from PRD sections
│
└─ NO → Is this a single action?
        ├─ YES → Create TASK
        │
        └─ NO (multiple steps) →
           Will it take more than 1 session to complete?
           ├─ YES → Create EPIC
           │        └─ Add subtasks for each major step
           │
           └─ NO → Create TASK
                   └─ Track steps in notes, not subtasks
```

---

## When to Create Epics

### Always Create Epic For:

| Source | Example |
|--------|---------|
| PRD parsing | `/task-parse docs/PRD/auth-system.md` → Epic with subtasks |
| Feature requests | "Implement dark mode" with UI, state, persistence steps |
| Multi-day work | Any work spanning multiple sessions |
| Cross-cutting concerns | "Improve performance" affecting multiple areas |

### Epic Indicators:

- Contains phrases like "implement", "build", "create system"
- Has acceptance criteria with 3+ items
- Requires changes to 3+ files or modules
- Will generate 3+ commits

---

## When to Create Simple Tasks

### Always Create Task For:

| Type | Example |
|------|---------|
| Bug fixes | "Fix login button not responding on mobile" |
| Quick changes | "Update copyright year in footer" |
| Documentation | "Add API documentation for /users endpoint" |
| Refactoring | "Rename getUserById to findUserById" |
| Chores | "Update dependencies to latest versions" |

### Task Indicators:

- Single action verb: "fix", "update", "add", "remove"
- Completable in one session
- Affects 1-2 files
- Single commit expected

---

## PRD → Epic Conversion

When parsing a PRD, TaskFlow automatically creates an epic structure:

### Input PRD Structure

```markdown
# User Authentication System

## Overview
Implement JWT-based authentication...

## Requirements
1. Users can register with email/password
2. Users can log in and receive tokens
3. Tokens refresh automatically
4. Protected routes require valid token

## Technical Approach
- Use bcrypt for password hashing
- JWT with 1-hour expiry
- Refresh tokens stored in httpOnly cookies
```

### Output Epic Structure

```yaml
Epic: "User Authentication System"
  Priority: high
  Source: docs/PRD/auth-system.md

  Subtasks:
    - title: "Set up auth infrastructure"
      priority: high
      acceptanceCriteria:
        - "bcrypt configured for password hashing"
        - "JWT secret configured"

    - title: "Implement user registration"
      priority: high
      acceptanceCriteria:
        - "POST /auth/register works"
        - "Passwords hashed before storage"

    - title: "Implement login endpoint"
      priority: high
      acceptanceCriteria:
        - "POST /auth/login returns tokens"
        - "Invalid credentials return 401"

    - title: "Add token refresh flow"
      priority: medium
      acceptanceCriteria:
        - "Refresh token in httpOnly cookie"
        - "Access token refreshes silently"

    - title: "Create auth middleware"
      priority: high
      acceptanceCriteria:
        - "Protected routes reject invalid tokens"
        - "Token expiry handled gracefully"
```

---

## Expanding Tasks to Epics

If a task turns out to be larger than expected, promote it:

### Command: `/task-expand`

```bash
/task-expand task-001

# Converts task-001 to an epic and prompts for subtasks
```

### Flow:

1. Change task type from `task` to `epic`
2. Prompt for subtask breakdown:

```json
{
  "question": "How should we break down this epic?",
  "header": "Subtasks",
  "options": [
    {
      "label": "Auto-generate from description",
      "description": "Let Claude analyze and suggest subtasks"
    },
    {
      "label": "Add manually",
      "description": "I'll specify each subtask"
    },
    {
      "label": "Keep as single task",
      "description": "Cancel - don't convert to epic"
    }
  ]
}
```

3. Create subtasks with parent reference
4. Update external system (Plane/GitHub) if applicable

---

## Backend-Specific Behavior

### Local Backend

```json
{
  "id": "task-001",
  "type": "epic",
  "title": "Auth System",
  "children": ["task-002", "task-003", "task-004"]
}
```

Children tracked via `parentId` field on subtasks.

### Plane Backend

**Option A: Modules**
- Epic → Plane Module
- Subtasks → Issues in that module

**Option B: Parent Issues**
- Epic → Issue with "epic" label
- Subtasks → Issues linked to parent

TaskFlow uses Option B by default (more portable).

### GitHub Backend

- Epic → Issue with "epic" label
- Subtasks → Issues referencing parent in body
- Task list in epic body tracks completion:

```markdown
## Subtasks

- [x] #42 Set up auth infrastructure
- [ ] #43 Implement registration
- [ ] #44 Implement login
```

---

## Progress Tracking

### Epic Completion

Epic is complete when ALL subtasks are done:

```python
def checkEpicCompletion(epicId):
    subtasks = backend.listTasks({"parentId": epicId})

    total = len(subtasks)
    done = len([t for t in subtasks if t["status"] == "done"])

    if done == total:
        # Auto-complete epic
        backend.setStatus(epicId, "done", f"All {total} subtasks completed")
    else:
        # Update progress note
        backend.addNote(epicId, f"Progress: {done}/{total} subtasks complete", "progress")
```

### Visual Progress

```
Epic: User Authentication System [████████░░] 80%

  ✓ Set up auth infrastructure
  ✓ Implement registration
  ✓ Implement login
  ✓ Add token refresh
  ○ Create auth middleware (in_progress)
```

---

## Dependency Handling

### Between Subtasks

```yaml
# In epic "Auth System"
subtasks:
  - id: task-002
    title: "Set up infrastructure"

  - id: task-003
    title: "Implement login"
    dependencies: [task-002]  # Must complete infrastructure first

  - id: task-004
    title: "Add middleware"
    dependencies: [task-003]  # Needs login to test
```

### Task Order Suggestions

```bash
/task-next

# Output:
Next recommended task: task-003 "Implement login"

Reason:
- Dependency task-002 is complete
- High priority
- No blockers

Blocked tasks:
- task-004 (waiting on: task-003)
```

---

## Configuration

In `.taskflow.local.md`:

```yaml
---
backend: local

epic:
  # Auto-create epic for PRD parsing
  autoEpicFromPRD: true

  # Minimum subtasks to auto-create epic
  minSubtasksForEpic: 3

  # Auto-complete epic when all subtasks done
  autoCompleteEpic: true

  # Track subtask progress in epic notes
  trackProgress: true
---
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `/task-add "Title" --type=epic` | Create epic directly |
| `/task-parse <prd>` | Parse PRD into epic + subtasks |
| `/task-expand <id>` | Convert task to epic |
| `/task-add "Sub" --parent=<epic-id>` | Add subtask to epic |
| `/task-list --type=epic` | List only epics |
| `/task-show <epic-id>` | Show epic with subtask tree |

---

**Strategy Version:** 2.0
**Used By:** /task-add, /task-parse, /task-expand
