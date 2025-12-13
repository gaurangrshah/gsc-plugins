---
description: Break a task into smaller subtasks
---

# /task-expand

Break down a complex task into smaller, manageable subtasks using AI analysis.

## What This Command Does

1. Load task by ID from `.tasks/tasks.json`
2. Analyze task complexity and generate subtasks
3. **CHECKPOINT**: Present subtasks for human review
4. On approval, save subtasks to task
5. Update task status if needed

## Arguments

- `<task-id>` - **Required.** Task ID to expand (e.g., `3`)
- `--num=N` - Optional. Target number of subtasks (default: 3-5)
- `--force` - Expand even if subtasks already exist (replaces them)

## Prerequisites

- Project must have tasks (`.tasks/tasks.json` exists)
- Task must exist and not already have subtasks (unless `--force`)

## Workflow

### Step 1: Load Task

Read `.tasks/tasks.json` and find the specified task.

If task already has subtasks:
```
Task 3 already has 4 subtasks:
  3.1 Create registration endpoint (done)
  3.2 Create login endpoint (in_progress)
  3.3 Create token refresh endpoint (pending)
  3.4 Create logout endpoint (pending)

Use --force to replace existing subtasks, or work with current ones.
```

### Step 2: Generate Subtasks with AI

Use the following prompt:

---

**SYSTEM PROMPT FOR SUBTASK GENERATION:**

```
Break down this task into smaller, actionable subtasks.

## Parent Task
ID: <TASK_ID>
Title: <TASK_TITLE>
Description: <TASK_DESCRIPTION>
Priority: <TASK_PRIORITY>

Acceptance Criteria:
<ACCEPTANCE_CRITERIA>

## Instructions
1. Create <NUM_SUBTASKS> subtasks that together complete the parent task
2. Each subtask should be completable in 30-90 minutes
3. Subtasks should be sequential where there are natural dependencies
4. First subtask should be the logical starting point
5. Final subtask should complete/verify the parent task

## Output Format
Return ONLY valid JSON (no markdown, no explanation):

{
  "subtasks": [
    {
      "id": "<TASK_ID>.1",
      "title": "<action-oriented title>",
      "status": "pending"
    },
    {
      "id": "<TASK_ID>.2",
      "title": "<action-oriented title>",
      "status": "pending"
    }
  ]
}

## Rules
- Subtask IDs must be <parent_id>.<sequential_number> (e.g., 3.1, 3.2, 3.3)
- All subtasks start with status "pending"
- Titles should start with action verbs
- Together, subtasks should fully address all acceptance criteria
```

---

### Step 3: Validate Subtasks

Before presenting to user:

1. **JSON Valid**: Parse without errors
2. **IDs Correct**: Format is `<parent_id>.<number>`, sequential
3. **Status Valid**: All are "pending"
4. **Coverage**: Subtasks should address acceptance criteria

### Step 4: CHECKPOINT - Human Review

Present generated subtasks:

```
┌─────────────────────────────────────────────────────────────────┐
│ Expanding Task 3: Implement user authentication                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Generated 4 subtasks:                                           │
│                                                                 │
│   3.1 Set up authentication middleware and JWT utilities        │
│   3.2 Create user registration endpoint with validation         │
│   3.3 Create login endpoint with token generation               │
│   3.4 Implement token refresh and logout endpoints              │
│                                                                 │
│ Criteria coverage:                                              │
│   ✓ Users can register with email/password → 3.2                │
│   ✓ Users can log in and receive JWT token → 3.3                │
│   ✓ Tokens expire after 24 hours → 3.1, 3.3                     │
│   ✓ Refresh token flow extends session → 3.4                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Approve these subtasks?                                         │
└─────────────────────────────────────────────────────────────────┘
```

Use AskUserQuestion:

```json
{
  "question": "Approve these subtasks?",
  "header": "Subtask Review",
  "options": [
    {"label": "Approve", "description": "Save subtasks to task"},
    {"label": "Edit", "description": "Modify before saving"},
    {"label": "Regenerate", "description": "Try again with different breakdown"},
    {"label": "Cancel", "description": "Keep task without subtasks"}
  ],
  "multiSelect": false
}
```

### Step 5: Handle Response

**If Approve:**
- Proceed to save

**If Edit:**
- Ask which subtask(s) to modify
- Allow adding/removing/renaming
- Re-display and confirm

**If Regenerate:**
- Ask for guidance (more/fewer subtasks, different focus)
- Re-run Step 2 with adjusted prompt
- Return to Step 4

**If Cancel:**
- Exit without changes

### Step 6: Save Subtasks

Update the task in `tasks.json`:

```python
task.subtasks = generated_subtasks
task.updated = now_iso8601()

# If task was pending, could mark as ready for subtask work
# Status remains unchanged - user starts work via /task-next
```

### Step 7: Confirm Success

```
Task expanded successfully!

Task 3: Implement user authentication
  └── 4 subtasks created:
      ○ 3.1 Set up authentication middleware and JWT utilities
      ○ 3.2 Create user registration endpoint with validation
      ○ 3.3 Create login endpoint with token generation
      ○ 3.4 Implement token refresh and logout endpoints

Next steps:
  - Run /task-next to start with subtask 3.1
  - Run /task-show 3 to see full task details
  - Run /task-status 3.1 in_progress to start manually
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Task not found | Show available task IDs |
| Task already has subtasks | Suggest --force or work with existing |
| Cannot expand subtask | Subtasks cannot have sub-subtasks |
| Task is done | Cannot expand completed tasks |
| Generation failed | Retry once, then show error |

## Examples

```bash
# Expand task 3 into subtasks
/task-expand 3

# Expand with specific subtask count
/task-expand 3 --num=6

# Replace existing subtasks
/task-expand 3 --force
```

## Related

- Command: /task-show (view task and subtasks)
- Command: /task-next (start working on subtask)
- Command: /task-status (update subtask status)
- Command: /task-parse (initial task generation)
