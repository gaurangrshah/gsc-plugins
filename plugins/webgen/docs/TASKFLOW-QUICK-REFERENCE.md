# TaskFlow Integration - Quick Reference

**For:** WebGen plugin agents and users
**Version:** 1.5.0

## Detection (For Agents)

```bash
# Check if TaskFlow is available
if [ -d "$HOME/.claude/plugins/local-plugins/taskflow" ]; then
  TASKFLOW_AVAILABLE=true
else
  TASKFLOW_AVAILABLE=false
fi
```

## User Prompt (Checkpoint 1)

```markdown
**TaskFlow Detected:**
I detected TaskFlow is available. Would you like to track this project with tasks?

- **Yes** - Initialize task tracking, break requirements into tasks, show progress
- **No** - Continue with standard WebGen workflow

What would you like to do?
```

## Task Structure Template

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Conduct competitive research",
      "status": "pending",
      "priority": "high",
      "phase": "research",
      "acceptanceCriteria": [
        "3+ competitors analyzed",
        "Research saved to research/competitive-analysis.md"
      ]
    },
    {
      "id": 2,
      "title": "Scaffold project architecture",
      "status": "pending",
      "priority": "high",
      "phase": "architecture",
      "dependencies": [1],
      "acceptanceCriteria": [
        "Project structure created",
        "Dev server running",
        "Infrastructure verified"
      ]
    },
    {
      "id": 3,
      "title": "Implement components",
      "status": "pending",
      "priority": "high",
      "phase": "implementation",
      "dependencies": [2],
      "subtasks": [
        {"id": "3.1", "title": "Hero component", "status": "pending"},
        {"id": "3.2", "title": "Features section", "status": "pending"},
        {"id": "3.3", "title": "CTA section", "status": "pending"}
      ]
    },
    {
      "id": 4,
      "title": "Generate legal pages",
      "status": "pending",
      "priority": "low",
      "phase": "legal",
      "dependencies": [3]
    },
    {
      "id": 5,
      "title": "Final documentation",
      "status": "pending",
      "priority": "medium",
      "phase": "final",
      "dependencies": [4]
    }
  ]
}
```

## Status Updates

### Checkpoint 2 (Research)

```bash
# Starting research
/task-status 1 in_progress

# Research complete
/task-status 1 done
```

### Checkpoint 3 (Architecture)

```bash
# Starting architecture
/task-status 2 in_progress

# Architecture complete
/task-status 2 done
```

### Checkpoint 4 (Implementation)

```bash
# Starting implementation
/task-status 3 in_progress

# As each component completes
/task-status 3.1 done  # Hero
/task-status 3.2 done  # Features
/task-status 3.3 done  # CTA

# Implementation complete
/task-status 3 done
```

### Checkpoint 4.5 (Legal - Conditional)

```bash
# If applicable
/task-status 4 in_progress
# ... generate legal pages ...
/task-status 4 done

# If skipped
/task-status 4 deferred
```

### Checkpoint 5 (Final)

```bash
# Starting final docs
/task-status 5 in_progress

# Final complete
/task-status 5 done
```

## Error Handling

### TaskFlow Command Fails

```bash
# Graceful degradation
if ! /task-init 2>/dev/null; then
  echo "TaskFlow initialization failed. Continuing with standard workflow..."
  TASKFLOW_ENABLED=false
fi
```

### No Response from TaskFlow

```markdown
⚠️ TaskFlow commands not responding.
Continuing with standard WebGen workflow.
Progress will not be tracked in TaskFlow.
```

## Final Report Template

```markdown
## CHECKPOINT 5 COMPLETE: Project finished

**Project Summary:**
- Location: {output-dir}
- Stack: {tech-stack}
- Preview: {url}
- Current branch: main

{{#if TASKFLOW_ENABLED}}
**Task Summary:**
- Total: {count} tasks, {subtask-count} subtasks
- Completed: {completed}/{total}
- Phases: Research → Architecture → Implementation → Legal → Final
- No blockers encountered
{{/if}}

**Deliverables:**
- ✅ All components generated
- ✅ Legal pages (if applicable)
- ✅ Documentation complete
- ✅ Screenshot captured
- ✅ Feature branch merged to main
```

## Commands Reference

| Command | Use Case |
|---------|----------|
| `/task-init` | Initialize TaskFlow in project |
| `/task-parse <prd>` | Parse structured requirements document |
| `/task-status <id> <status>` | Update task status |
| `/task-list` | View all tasks |
| `/task-next` | Get AI recommendation for next task |
| `/task-show <id>` | View detailed task information |

## Status Values

| Status | When to Use |
|--------|-------------|
| `pending` | Task not started yet |
| `in_progress` | Currently working on task |
| `done` | Task completed successfully |
| `blocked` | Waiting on code review or dependency |
| `deferred` | Task skipped (e.g., legal pages not needed) |

## Checkpoint Mapping

| Checkpoint | Task ID | Phase |
|------------|---------|-------|
| 1. Requirements | *(init only)* | - |
| 2. Research | 1 | `research` |
| 3. Architecture | 2 | `architecture` |
| 4. Implementation | 3 | `implementation` |
| 4.5. Legal | 4 | `legal` |
| 5. Final | 5 | `final` |

## Non-Breaking Guarantees

✅ WebGen works identically without TaskFlow
✅ User can decline even if TaskFlow available
✅ No errors if TaskFlow not installed
✅ Commands fail gracefully
✅ Standard workflow unchanged

---

**For detailed integration patterns, see:** `skills/taskflow-integration/skill.md`
**For user documentation, see:** `docs/TASKFLOW-INTEGRATION.md`
