# TaskFlow Integration Guide

**Version:** 1.0.0
**Created:** 2025-12-13

## Overview

WebGen optionally integrates with the TaskFlow plugin to provide structured task tracking during website generation. This integration is **completely optional** and **non-breaking**—WebGen works identically with or without TaskFlow.

## Quick Start

### 1. Install Both Plugins

```bash
# Install TaskFlow
cp -r taskflow ~/.claude/plugins/local-plugins/

# Install WebGen
cp -r webgen ~/.claude/plugins/local-plugins/

# Restart Claude Code
```

### 2. Use WebGen Normally

```bash
/webgen restaurant landing page for Bistro Bliss
```

### 3. Accept TaskFlow When Prompted

```
TaskFlow detected. Track this project with tasks? (y/n)
```

Type `y` to enable task tracking, or `n` to continue with standard workflow.

## What You Get

When TaskFlow integration is enabled:

### Visual Progress Tracking

```
Tasks:
1. ✅ Conduct competitive research
2. ✅ Scaffold project architecture
3. 🔄 Implement landing page components
   - ✅ Hero component
   - ✅ Features section
   - ⏳ CTA section
4. ⏳ Generate legal pages
5. ⏳ Final documentation
```

### Checkpoint Alignment

Each WebGen checkpoint maps to TaskFlow tasks:

| Checkpoint | TaskFlow Task | Status Updates |
|------------|---------------|----------------|
| 1. Requirements | *(No task - initialization)* | TaskFlow initialized |
| 2. Research | "Conduct competitive research" | `pending` → `in_progress` → `done` |
| 3. Architecture | "Scaffold project architecture" | `pending` → `in_progress` → `done` |
| 4. Implementation | "Implement components" | `pending` → `in_progress` → `done` |
| 4.5. Legal | "Generate legal pages" | `pending` → `in_progress` → `done` |
| 5. Final | "Final documentation" | `pending` → `in_progress` → `done` |

### Resume Capability

If your session is interrupted:

```bash
# Check task status
/task-list

# Resume from where you left off
/task-next
```

## Task Structure Example

### For a Landing Page Project

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Conduct competitive research",
      "description": "Research restaurant website competitors",
      "status": "done",
      "priority": "high",
      "phase": "research",
      "acceptanceCriteria": [
        "3+ competitors analyzed",
        "Research saved to research/competitive-analysis.md",
        "Design patterns documented"
      ]
    },
    {
      "id": 2,
      "title": "Scaffold project architecture",
      "description": "Initialize React + Vite + Tailwind project",
      "status": "done",
      "priority": "high",
      "phase": "architecture",
      "dependencies": [1],
      "subtasks": [
        {"id": "2.1", "title": "Create project structure", "status": "done"},
        {"id": "2.2", "title": "Run pnpm install", "status": "done"},
        {"id": "2.3", "title": "Verify dev server", "status": "done"}
      ]
    },
    {
      "id": 3,
      "title": "Implement landing page components",
      "description": "Generate all landing page sections",
      "status": "in_progress",
      "priority": "high",
      "phase": "implementation",
      "dependencies": [2],
      "subtasks": [
        {"id": "3.1", "title": "Hero component", "status": "done"},
        {"id": "3.2", "title": "Features section", "status": "done"},
        {"id": "3.3", "title": "Menu showcase", "status": "in_progress"},
        {"id": "3.4", "title": "Testimonials", "status": "pending"},
        {"id": "3.5", "title": "Reservation CTA", "status": "pending"}
      ],
      "acceptanceCriteria": [
        "All components generated with docstrings",
        "Code review passed",
        "Accessibility compliant",
        "Preview screenshot captured"
      ]
    },
    {
      "id": 4,
      "title": "Generate legal pages",
      "description": "Create privacy policy and terms of service",
      "status": "pending",
      "priority": "low",
      "phase": "legal",
      "dependencies": [3]
    },
    {
      "id": 5,
      "title": "Final documentation",
      "description": "Generate README, design decisions, screenshot",
      "status": "pending",
      "priority": "medium",
      "phase": "final",
      "dependencies": [4]
    }
  ]
}
```

## Commands Available

When TaskFlow is enabled, you can use TaskFlow commands within your WebGen project:

| Command | Use Case |
|---------|----------|
| `/task-list` | View all tasks and their status |
| `/task-next` | Get AI recommendation for next task |
| `/task-show <id>` | View detailed task information |
| `/task-status <id> <status>` | Manually update task status |
| `/task-expand <id>` | Break a task into subtasks |

**Note:** The orchestrator automatically updates task statuses at checkpoints. Manual commands are for advanced users.

## Opting Out

### Decline at Prompt

```
TaskFlow detected. Track this project with tasks? (y/n)

User: n

Understood. Proceeding with standard WebGen workflow...
```

### No TaskFlow Installed

If TaskFlow isn't installed, WebGen proceeds normally with no prompts or errors.

## Technical Details

### Detection Method

WebGen checks for TaskFlow's presence:

```bash
if [ -d "$HOME/.claude/plugins/local-plugins/taskflow" ]; then
  TASKFLOW_AVAILABLE=true
else
  TASKFLOW_AVAILABLE=false
fi
```

### Storage Location

Tasks are stored in the project directory:

```
bistro-bliss - webgen/
└── .tasks/
    ├── state.json
    └── tags/
        └── master/
            └── tasks.json
```

### Status Synchronization

| Event | TaskFlow Update |
|-------|-----------------|
| Phase starts | `/task-status {id} in_progress` |
| Phase completes | `/task-status {id} done` |
| Code review blocks | `/task-status {id} blocked` |
| Legal pages skipped | `/task-status {id} deferred` |

## Benefits

### For Solo Developers

- **Progress visibility:** See exactly where you are in the generation
- **Resume capability:** Pick up where you left off if interrupted
- **Completion checklist:** Clear acceptance criteria per phase

### For Team Workflows

- **Shared context:** Other team members can see generation progress
- **Parallel work:** TaskFlow tags enable multiple features in progress
- **Historical record:** Task history shows what was generated and when

## Troubleshooting

### "TaskFlow command not found"

**Cause:** TaskFlow plugin not installed or not activated

**Solution:**
```bash
# Check if TaskFlow is installed
ls ~/.claude/plugins/local-plugins/taskflow

# If missing, install it
cp -r /path/to/taskflow ~/.claude/plugins/local-plugins/

# Restart Claude Code
```

### Tasks not updating

**Cause:** TaskFlow commands failing silently

**Solution:** Check task status manually:
```bash
cd your-project - webgen/
/task-list
```

If no tasks exist, TaskFlow may not have initialized properly. Continue with standard WebGen workflow.

### Want to disable integration

**Solution:** Simply decline when prompted:
```
TaskFlow detected. Track this project with tasks? (y/n)
User: n
```

Or, if you never want the prompt, uninstall TaskFlow:
```bash
rm -rf ~/.claude/plugins/local-plugins/taskflow
```

## Examples

### Example 1: Simple Landing Page

```
User: /webgen portfolio site for Jane Doe, photographer

Orchestrator: [Detects TaskFlow]
TaskFlow detected. Track this project with tasks? (y/n)

User: y

Orchestrator: ✅ TaskFlow enabled
Initializing tasks...

Tasks created:
1. Conduct competitive research (high priority)
2. Scaffold project architecture (depends on #1)
3. Implement portfolio components (depends on #2)
4. Final documentation (depends on #3)

Starting with task #1...
/task-status 1 in_progress

[Researches competitor portfolios...]

/task-status 1 done
✅ Research complete (1/4 tasks done)

Moving to task #2...
```

### Example 2: Multi-Page Site

```
User: /webgen multi-page healthcare site for Clarity Health

Orchestrator: [Detects TaskFlow]
TaskFlow detected. Track this project with tasks? (y/n)

User: y

Orchestrator: ✅ TaskFlow enabled

Tasks created:
1. Conduct competitive research
2. Scaffold multi-page architecture
3. Implement home page components
4. Implement services page components
5. Implement about page components
6. Implement contact page components
7. Generate legal pages (privacy, terms, HIPAA notice)
8. Final documentation

[Proceeds through each task with status updates...]

Final Summary:
✅ 8/8 tasks complete
✅ All pages implemented
✅ Legal pages generated
✅ Documentation complete
```

## Integration Architecture

### Orchestrator Role

The `@webgen-orchestrator` agent:
1. Detects TaskFlow at session start
2. Offers integration to user
3. Initializes TaskFlow if accepted
4. Creates tasks from requirements
5. Updates task status at each checkpoint
6. Includes task summary in final report

### WebGen Agent Role

The `@webgen` agent:
- Receives task context from orchestrator
- Updates subtasks during implementation
- Reports task completion back to orchestrator

### Skill Role

The `taskflow-integration` skill:
- Provides detection logic
- Defines task structure patterns
- Documents status mapping
- Handles error scenarios gracefully

## Version History

### v1.0.0 (2025-12-13)

- Initial TaskFlow integration
- Non-breaking, opt-in design
- Detection at Checkpoint 1
- Automatic task creation from requirements
- Status synchronization at all checkpoints
- Task summary in final report

## Related Documentation

- [TaskFlow Plugin README](../../taskflow/README.md)
- [WebGen Orchestrator Agent](../agents/webgen-orchestrator.md)
- [TaskFlow Integration Skill](../skills/taskflow-integration/skill.md)
- [WebGen Architecture](./ARCHITECTURE.md)

---

**Remember:** TaskFlow integration is completely optional. WebGen works perfectly without it—this just adds structured task tracking for those who want it.
