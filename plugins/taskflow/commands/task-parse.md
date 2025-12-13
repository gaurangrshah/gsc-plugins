---
description: Parse PRD document into structured tasks
---

# /task-parse

Parse a Product Requirements Document (PRD) and generate structured, dependency-aware tasks.

## What This Command Does

1. Read the specified PRD file
2. Analyze content using AI to extract tasks
3. Generate structured tasks with dependencies and acceptance criteria
4. **CHECKPOINT**: Present tasks for human review
5. On approval, save to current tag's `tasks.json`
6. Update central index stats

## Arguments

- `<prd-path>` - **Required.** Path to PRD file (relative to project root, typically `docs/PRD/*.md`)
- `--num-tasks=N` - Optional. Hint for target number of tasks (default: 10)
- `--append` - Append to existing tasks instead of replacing
- `--tag=<name>` - Parse into specific tag (default: current tag)

## Prerequisites

- Project must be initialized (`/task-init` run first)
- `.tasks/` directory must exist
- PRD file should exist (typically in `docs/PRD/` directory)

## PRD Location Convention

PRD files should be stored in:
```
<project-root>/docs/PRD/<feature-name>.md
```

Examples:
- `docs/PRD/user-authentication.md`
- `docs/PRD/api-v2.md`
- `docs/PRD/dashboard-redesign.md`

## Workflow

### Step 1: Validate Setup

**Check TaskFlow initialized:**
```python
if not exists(".tasks/state.json"):
    error("TaskFlow not initialized in this project.")
    suggest("Run /task-init first")
    exit()
```

**Load current tag:**
```python
state = read_json(".tasks/state.json")
current_tag = args.tag or state["currentTag"]
tasks_file = f".tasks/tags/{current_tag}/tasks.json"

if not exists(tasks_file):
    error(f"Tag '{current_tag}' does not exist.")
    suggest(f"Run /task-tag create {current_tag}")
    exit()
```

### Step 2: Read PRD

**Try to find and read PRD file:**

```python
prd_path = args.prd_path

# Handle relative paths
if not prd_path.startswith('/'):
    prd_path = os.path.join(project_root, prd_path)

if not exists(prd_path):
    # Try common variations
    alternatives = [
        f"docs/PRD/{prd_path}",
        f"docs/PRD/{prd_path}.md",
        f"docs/{prd_path}",
    ]
    # Check each alternative...
```

**If file doesn't exist:**
```
PRD file not found: docs/PRD/feature.md

Searched locations:
  ✗ docs/PRD/feature.md
  ✗ docs/PRD/feature
  ✗ docs/feature.md

Available PRDs in docs/PRD/:
  • user-authentication.md (3.2 KB)
  • api-redesign.md (5.1 KB)
  • dashboard-v2.md (2.8 KB)

Usage: /task-parse docs/PRD/<filename>.md
```

**If file is empty or too short:**
```
PRD file appears to be empty or incomplete: docs/PRD/feature.md

Size: 45 bytes (expected: 500+ bytes for meaningful task generation)

A good PRD typically includes:
  • Feature description and goals
  • User stories or use cases
  • Technical requirements
  • Success criteria
  • Dependencies

See: ~/.claude/knowledge/guides/taskflow-design.md for PRD tips
```

**If file is very large (>50KB):**
```
PRD file is large: docs/PRD/full-spec.md (127 KB)

Large PRDs may generate many tasks. Options:
  1. Parse anyway (may generate 20+ tasks)
  2. Specify --num-tasks=N to limit scope
  3. Split PRD into smaller feature documents

Proceed with full PRD? [Y/n]
```

### Step 3: Check Existing Tasks

**If tag already has tasks and not using --append:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Tag 'master' already has tasks                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Current tasks: 8 (3 done, 1 in progress, 4 pending)             │
│ PRD source: docs/PRD/original-feature.md                        │
│                                                                 │
│ Parsing new PRD will REPLACE existing tasks.                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Options:                                                        │
│   • Replace all tasks (existing progress lost)                  │
│   • Append new tasks (use --append)                             │
│   • Create new tag (use --tag=<name>)                           │
│   • Cancel                                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Step 4: Parse with AI

Use the following prompt to generate tasks:

---

**SYSTEM PROMPT FOR TASK GENERATION:**

```
Analyze this Product Requirements Document and generate a structured task breakdown.

## Instructions
1. Identify discrete, implementable units of work
2. Establish dependencies (what must complete before what)
3. Order by logical implementation sequence
4. Each task should be completable in a focused work session (1-4 hours)
5. Include clear, measurable acceptance criteria for each task
6. Assign priority based on:
   - high: Foundational work, blocks other tasks
   - medium: Important features, some dependencies
   - low: Nice-to-have, no blockers

## Output Format
Return ONLY valid JSON matching this exact schema (no markdown, no explanation, no code fences):

{
  "tasks": [
    {
      "id": 1,
      "title": "<concise action-oriented title - start with verb>",
      "description": "<what needs to be done and why - 1-3 sentences>",
      "status": "pending",
      "priority": "high|medium|low",
      "dependencies": [],
      "subtasks": [],
      "acceptanceCriteria": [
        "<specific, measurable criterion>",
        "<another criterion>"
      ]
    }
  ]
}

## Rules
- IDs must be sequential integers starting at 1
- No circular dependencies allowed
- Task 1 MUST have empty dependencies array (entry point)
- Dependencies reference task IDs that must complete first
- Each task needs 2-5 acceptance criteria
- Titles should start with action verbs (Create, Implement, Add, Configure, etc.)
- Keep descriptions focused on WHAT and WHY, not HOW
- Do NOT include markdown code fences or any text outside the JSON

## Target Task Count
Aim for approximately <NUM_TASKS> top-level tasks. Break down further only if a task would take more than 4 hours.

## PRD Content
<PRD_CONTENT>
```

---

### Step 5: Validate Generated Tasks

**Validation checks (in order):**

1. **JSON Valid**: Parse without errors
   - Strip markdown code fences if present
   - Handle common JSON errors (trailing commas, single quotes)

2. **Schema Complete**: All required fields present
   ```python
   required_fields = ["id", "title", "description", "status", "priority", "dependencies", "acceptanceCriteria"]
   for task in tasks:
       missing = [f for f in required_fields if f not in task]
       if missing:
           error(f"Task {task.get('id', '?')} missing fields: {missing}")
   ```

3. **No Circular Dependencies**: Build and validate graph
   ```python
   def has_cycle(tasks):
       # Build adjacency list
       # Run DFS cycle detection
       # Return cycle path if found
   ```

4. **Dependencies Exist**: All referenced IDs valid
   ```python
   task_ids = {t["id"] for t in tasks}
   for task in tasks:
       for dep in task["dependencies"]:
           if dep not in task_ids:
               error(f"Task {task['id']} depends on non-existent task {dep}")
   ```

5. **Has Entry Point**: At least one task with no dependencies
   ```python
   entry_points = [t for t in tasks if not t["dependencies"]]
   if not entry_points:
       error("No entry point task (all tasks have dependencies)")
   ```

6. **IDs Sequential**: No gaps or duplicates
   ```python
   ids = sorted([t["id"] for t in tasks])
   expected = list(range(1, len(tasks) + 1))
   if ids != expected:
       error(f"IDs should be {expected}, got {ids}")
   ```

**If validation fails:**
```
Validation errors in generated tasks:

  ✗ Task 3 depends on non-existent task 7
  ✗ Circular dependency: 4 → 5 → 6 → 4
  ✗ Task 2 missing 'acceptanceCriteria' field

Attempting to fix automatically...
[If fixable, show fixed version]
[If not, offer to regenerate]
```

### Step 6: CHECKPOINT - Human Review

Present generated tasks for approval:

```
┌─────────────────────────────────────────────────────────────────┐
│ PRD Parsed: <N> tasks generated                                 │
│ Source: <prd-path>                                              │
│ Tag: <current-tag>                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. [HIGH] <Task 1 title>                                       │
│     └── No dependencies                                         │
│     └── Criteria: <count> acceptance criteria                   │
│                                                                 │
│  2. [HIGH] <Task 2 title>                          (needs: 1)   │
│     └── Depends on: Task 1                                      │
│     └── Criteria: <count> acceptance criteria                   │
│                                                                 │
│  3. [MED]  <Task 3 title>                          (needs: 1,2) │
│     └── Depends on: Task 1, Task 2                              │
│     └── Criteria: <count> acceptance criteria                   │
│                                                                 │
│  ... (show all tasks)                                           │
│                                                                 │
│ Summary:                                                        │
│   HIGH: <count> | MEDIUM: <count> | LOW: <count>                │
│   Estimated entry points: <count>                               │
│   Max dependency depth: <count>                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Review the task breakdown above.                                │
└─────────────────────────────────────────────────────────────────┘
```

Use AskUserQuestion:

```json
{
  "question": "Approve this task breakdown?",
  "header": "Task Review",
  "options": [
    {"label": "Approve", "description": "Save tasks and continue"},
    {"label": "Edit", "description": "Modify specific tasks before saving"},
    {"label": "Regenerate", "description": "Parse PRD again with different approach"},
    {"label": "Cancel", "description": "Discard and exit"}
  ],
  "multiSelect": false
}
```

### Step 7: Handle Response

**If Approve:**
- Proceed to save

**If Edit:**
- Ask: "Which task(s) to modify? (e.g., 1,3,5 or 'all')"
- For each task, ask what to change:
  - Title
  - Description
  - Priority
  - Dependencies
  - Acceptance criteria
- Re-display modified tasks and confirm

**If Regenerate:**
- Ask for guidance with AskUserQuestion:
  ```json
  {
    "question": "How should I adjust the task generation?",
    "header": "Regenerate",
    "options": [
      {"label": "More tasks", "description": "Break down into smaller pieces"},
      {"label": "Fewer tasks", "description": "Higher-level groupings"},
      {"label": "Different focus", "description": "I'll provide specific guidance"},
      {"label": "Try again", "description": "Same settings, fresh attempt"}
    ],
    "multiSelect": false
  }
  ```
- Adjust prompt based on response
- Re-run Step 4

**If Cancel:**
- Exit without saving
- Display: "No changes made. PRD not parsed."

### Step 8: Save Tasks

**For --append mode:**
```python
existing = read_json(tasks_file)
max_id = max([t["id"] for t in existing["tasks"]], default=0)

# Renumber new tasks
for i, task in enumerate(new_tasks):
    old_id = task["id"]
    task["id"] = max_id + i + 1
    # Update any internal dependencies
    for t in new_tasks:
        t["dependencies"] = [
            (max_id + d) if d == old_id else d
            for d in t["dependencies"]
        ]

existing["tasks"].extend(new_tasks)
existing["updated"] = now_iso8601()
```

**Write to tag's tasks.json:**

```json
{
  "version": "1.0",
  "project": "<project-name>",
  "tag": "<current-tag>",
  "prdSource": "<prd-path>",
  "created": "<original-or-now>",
  "updated": "<ISO-8601-now>",
  "tasks": [<generated-tasks>]
}
```

### Step 9: Update Central Index

Update project stats in central index:

```python
stats = {
    "total": len(tasks),
    "pending": len([t for t in tasks if t["status"] == "pending"]),
    "in_progress": len([t for t in tasks if t["status"] == "in_progress"]),
    "done": len([t for t in tasks if t["status"] == "done"])
}
update_index(project_slug, stats, current_tag)
```

### Step 10: Confirm Success

```
Tasks saved successfully!

  Project: <project-name>
  Tag: <current-tag>
  PRD Source: <prd-path>
  Tasks Created: <N>

  Breakdown:
    HIGH priority: <count>
    MEDIUM priority: <count>
    LOW priority: <count>

  Entry points (no dependencies):
    Task 1: <title>

Next steps:
  - Run /task-list to see all tasks
  - Run /task-next to get started
  - Run /task-show <id> for task details
```

## Edge Cases

### PRD Contains Code Blocks

The parser should handle PRDs with embedded code examples without treating them as task content.

### PRD Is Not English

```
Note: PRD appears to be in a non-English language.
Task generation will proceed, but titles/descriptions will match PRD language.
```

### Very Few Requirements in PRD

```
Warning: PRD seems minimal. Only <N> tasks generated.

This might indicate:
  • PRD needs more detail
  • Feature is genuinely small
  • Consider combining with other PRDs

Proceed anyway? [Y/n]
```

### Conflicting Dependencies Detected

If AI generates conflicting or illogical dependencies:

```
Warning: Dependency structure may have issues:

  Task 5 depends on Task 6, but Task 6 depends on Task 5
  This creates a circular dependency.

Auto-fixing by removing dependency from Task 6 → Task 5.
Please review after approval.
```

## Error Handling

| Error | Resolution |
|-------|------------|
| No `.tasks/` directory | Prompt to run `/task-init` first |
| Tag doesn't exist | Suggest creating tag or using existing |
| PRD file not found | List available PRDs in `docs/PRD/`, suggest path |
| PRD file empty | Error with guidance on PRD content |
| PRD file too large | Warn and offer options |
| JSON parse failure | Strip fences, retry once, show raw on failure |
| Circular dependency | Show cycle, auto-fix or regenerate |
| Existing tasks | Offer replace/append/new-tag options |
| User cancels | Confirm no changes made |

## Examples

```bash
# Parse PRD for authentication feature
/task-parse docs/PRD/user-authentication.md

# Parse with target task count hint
/task-parse docs/PRD/api-redesign.md --num-tasks=15

# Add tasks from additional PRD (phase 2)
/task-parse docs/PRD/phase2-features.md --append

# Parse into specific tag
/task-parse docs/PRD/experiment.md --tag=experimental
```

## Tips for Good PRDs

The quality of generated tasks depends on PRD quality. Good PRDs include:

- Clear feature descriptions
- User stories or use cases
- Technical requirements or constraints
- Success criteria
- Non-functional requirements (performance, security)
- Dependencies on external systems

## Related

- Command: /task-init (prerequisite)
- Command: /task-list (view generated tasks)
- Command: /task-next (start working)
- Command: /task-tag (manage tags)
- Design: ~/.claude/knowledge/guides/taskflow-design.md
