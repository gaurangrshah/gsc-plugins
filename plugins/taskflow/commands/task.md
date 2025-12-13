---
description: TaskFlow orchestrator - conversational task management
---

# /task

Conversational interface for TaskFlow task management. Interprets natural language requests and routes to appropriate task commands.

## What This Skill Does

1. Parse natural language task management requests
2. Route to appropriate `/task-*` command
3. Provide contextual help and suggestions
4. Handle multi-step workflows conversationally

## Usage

Invoke with natural language:

```
/task <natural language request>
```

Or just `/task` for status overview.

## Request Routing

| User Says | Routes To |
|-----------|-----------|
| "initialize", "init", "set up tasks" | `/task-init` |
| "parse", "generate tasks from", "read PRD" | `/task-parse` |
| "list", "show all", "what tasks" | `/task-list` |
| "next", "what should I work on", "what's next" | `/task-next` |
| "show task N", "details for N", "what's task N" | `/task-show N` |
| "done", "complete", "finished task N" | `/task-status N done` |
| "start task N", "working on N" | `/task-status N in_progress` |
| "expand", "break down task N" | `/task-expand N` |
| "block", "blocked on N" | `/task-status N blocked` |
| "defer", "postpone task N" | `/task-status N deferred` |
| "help", "how do I", "what can you do" | Show help |

## Workflow

### Step 1: Parse Intent

Analyze the user's request to determine intent:

```python
intents = {
    "init": ["initialize", "init", "set up", "create tasks"],
    "parse": ["parse", "generate", "from prd", "read prd", "create from"],
    "list": ["list", "show all", "all tasks", "what tasks", "overview"],
    "next": ["next", "what should", "recommend", "what's next", "start"],
    "show": ["show", "details", "tell me about", "what's task", "describe"],
    "done": ["done", "complete", "finished", "mark done", "completed"],
    "start": ["start", "begin", "working on", "in progress"],
    "expand": ["expand", "break down", "split", "subtasks"],
    "block": ["block", "blocked", "stuck", "waiting"],
    "defer": ["defer", "postpone", "later", "skip"],
    "help": ["help", "how", "what can", "commands"]
}

# Extract task ID if present
task_id = extract_task_id(request)  # e.g., "task 3" → 3
```

### Step 2: Context Check

Before routing, check project context:

```python
# Check if in a project with tasks
has_tasks = exists(".tasks/tasks.json")

if not has_tasks and intent not in ["init", "help"]:
    suggest_init()
    return
```

### Step 3: Route to Command

Execute the appropriate command:

```python
if intent == "init":
    execute("/task-init")
elif intent == "parse":
    prd_path = extract_path(request) or prompt_for_prd()
    execute(f"/task-parse {prd_path}")
elif intent == "list":
    filters = extract_filters(request)  # --status, --priority
    execute(f"/task-list {filters}")
elif intent == "next":
    execute("/task-next")
elif intent == "show":
    execute(f"/task-show {task_id}")
elif intent == "done":
    execute(f"/task-status {task_id} done")
elif intent == "start":
    execute(f"/task-status {task_id} in_progress")
elif intent == "expand":
    execute(f"/task-expand {task_id}")
elif intent == "block":
    execute(f"/task-status {task_id} blocked")
elif intent == "defer":
    execute(f"/task-status {task_id} deferred")
elif intent == "help":
    show_help()
```

### Step 4: Handle Ambiguity

If intent unclear, ask for clarification:

```
I'm not sure what you want to do. Did you mean:

  • /task-list - See all tasks
  • /task-next - Get next recommended task
  • /task-show <id> - View specific task details

Or tell me more about what you need.
```

## Context-Aware Responses

### No Project Initialized
```
No TaskFlow project found in current directory.

To get started:
  1. Run /task-init to initialize
  2. Create a PRD in docs/PRD/your-feature.md
  3. Run /task-parse docs/PRD/your-feature.md

Or run /task help for more information.
```

### Project Has No Tasks
```
TaskFlow is initialized, but no tasks yet.

To generate tasks:
  1. Create a PRD document in docs/PRD/
  2. Run: /task parse docs/PRD/your-prd.md

Available PRDs found:
  • docs/PRD/feature-spec.md
  • docs/PRD/api-design.md
```

### Status Overview (just `/task`)
```
┌─────────────────────────────────────────────────────────────────┐
│ TaskFlow: my-project                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Progress: ████████░░░░░░░░ 50% (4/8 tasks)                      │
│                                                                 │
│ Current: Task 5 - Implement caching (in_progress)               │
│ Next up: Task 6 - Add logging                                   │
│                                                                 │
│ Status breakdown:                                               │
│   ✓ Done: 4                                                     │
│   ● In Progress: 1                                              │
│   ○ Pending: 2                                                  │
│   ◌ Blocked: 1                                                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Quick actions:                                                  │
│   /task done 5     - Complete current task                      │
│   /task next       - See next recommendation                    │
│   /task list       - View all tasks                             │
└─────────────────────────────────────────────────────────────────┘
```

## Example Conversations

### Starting Fresh
```
User: /task initialize
→ Executes /task-init

User: /task parse the PRD at docs/PRD/auth-feature.md
→ Executes /task-parse docs/PRD/auth-feature.md

User: /task what should I work on first?
→ Executes /task-next
```

### During Development
```
User: /task
→ Shows status overview with current task

User: /task I finished the authentication task
→ Executes /task-status 3 done (infers current task)

User: /task show me task 5
→ Executes /task-show 5

User: /task break down task 6 into smaller pieces
→ Executes /task-expand 6
```

### Handling Issues
```
User: /task I'm blocked on task 4, waiting for API access
→ Executes /task-status 4 blocked
→ Optionally records note about API access

User: /task let's defer the caching task for now
→ Executes /task-status 7 deferred

User: /task what's still pending?
→ Executes /task-list --status=pending
```

## Help Output

When user asks for help:

```
TaskFlow - AI-Powered Task Management

Commands:
  /task                    Status overview
  /task init               Initialize in current project
  /task parse <prd>        Generate tasks from PRD
  /task list               List all tasks
  /task next               Get next recommended task
  /task show <id>          View task details
  /task done <id>          Mark task complete
  /task start <id>         Start working on task
  /task expand <id>        Break into subtasks
  /task block <id>         Mark task as blocked
  /task defer <id>         Postpone task

Natural language examples:
  "What should I work on next?"
  "I finished task 3"
  "Show me the details for task 5"
  "Break down task 4 into smaller pieces"
  "Parse the PRD at docs/PRD/feature.md"

Documentation: ~/.claude/knowledge/guides/taskflow-design.md
```

## Error Handling

| Situation | Response |
|-----------|----------|
| No task ID when required | Ask for task ID or show list |
| Invalid task ID | Show available task IDs |
| Ambiguous request | Ask for clarification with options |
| Command fails | Show error and suggest fix |

## Related

- Design: ~/.claude/knowledge/guides/taskflow-design.md
- Commands: /task-init, /task-parse, /task-list, /task-show, /task-next, /task-status, /task-expand
