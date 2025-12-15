---
name: taskflow-integration
description: Optional TaskFlow integration for AppGen projects
version: 1.0.0
---

# TaskFlow Integration Skill

**Purpose:** Enable optional task management for AppGen projects when TaskFlow plugin is available.

**Integration Type:** Non-breaking, opt-in

---

## Core Principle: Optional Enhancement

**This skill provides TaskFlow integration WITHOUT breaking AppGen when TaskFlow is unavailable.**

**Rules:**
- ✅ Detect TaskFlow availability before offering integration
- ✅ Gracefully degrade if TaskFlow not found
- ✅ User can decline even if TaskFlow is available
- ✅ NEVER error if TaskFlow missing
- ✅ AppGen works identically with or without TaskFlow

---

## Detection Protocol

### 1. Check TaskFlow Availability

**At appgen session start**, check for TaskFlow:

```bash
# Method 1: Check for taskflow plugin directory
if [ -d "$HOME/.claude/plugins/local-plugins/taskflow" ]; then
  TASKFLOW_AVAILABLE=true
else
  TASKFLOW_AVAILABLE=false
fi

# Method 2: Try to locate task command
if command -v task-init &> /dev/null; then
  TASKFLOW_AVAILABLE=true
fi
```

**Store result** in session context:
- `taskflow_available: true|false`
- `taskflow_enabled: true|false` (user's choice)

### 2. Offer Integration (If Available)

**After requirements confirmed (Checkpoint 1):**

```markdown
## CHECKPOINT 1 COMPLETE

**Project:** {project-name}
**Type:** {project-type}
**Output:** {output-dir}

**TaskFlow Detected:**
I detected TaskFlow is available. Would you like to track this project with tasks?

- **Yes** - Initialize task tracking, break requirements into tasks
- **No** - Continue with standard AppGen workflow

What would you like to do?
```

**If user declines:**
```markdown
Understood. Proceeding with standard AppGen workflow...
```

**If user accepts:**
```markdown
✅ TaskFlow enabled for this project.
Initializing task tracking...
```

---

## Integration Points

### Phase 1: Requirements → Task Initialization

**Trigger:** User accepts TaskFlow integration

**Actions:**
1. Initialize TaskFlow in project directory
2. Create initial task structure from requirements
3. Optionally parse requirements as PRD

**Implementation:**

```bash
cd {output-dir}

# Initialize TaskFlow
/task-init

# Option A: Parse requirements.md as PRD (if structured)
if [ -f "docs/requirements.md" ]; then
  /task-parse docs/requirements.md
fi

# Option B: Create tasks manually from requirements
# (Use if requirements not in PRD format)
```

**Task Structure from Requirements:**

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Conduct competitive research",
      "description": "Research {industry} competitors and extract design patterns",
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
      "description": "Initialize {tech-stack} project with proper structure",
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
      "title": "Implement {component-name}",
      "description": "Generate {component-name} component",
      "status": "pending",
      "priority": "medium",
      "phase": "implementation",
      "dependencies": [2]
    }
  ]
}
```

### Phase 2-4: Task Tracking During Implementation

**At each checkpoint:**

**Before starting phase:**
```bash
/task-status {task-id} in_progress
```

**During implementation:**
- Update subtasks as components completed
- Track blockers if encountered
- Use `/task-next` for prioritization

**After phase complete:**
```bash
/task-status {task-id} done
```

**Example for Checkpoint 4 (Implementation):**

```markdown
Starting Implementation phase...

# Update TaskFlow
/task-status 3 in_progress

# Generate components
[Component generation...]

# Mark subtasks complete
/task-status 3.1 done  # Hero component
/task-status 3.2 done  # Features section
/task-status 3.3 done  # CTA component

# Mark main task complete
/task-status 3 done

✅ Implementation complete
```

### Phase 5: Final Task Completion

**At project completion:**

1. Mark all remaining tasks as complete
2. Generate task summary
3. Include in final report

**Implementation:**

```bash
# List any incomplete tasks
/task-list --status pending,in_progress

# Mark project complete
/task-status {final-task-id} done

# Generate summary
/task-list --summary
```

**Include in final report:**

```markdown
## CHECKPOINT 5 COMPLETE: Project finished

**Project Summary:**
- Location: {output-dir}
- Stack: {tech-stack}
- Preview: {url}

**Task Summary:**
- Total tasks: {count}
- Completed: {completed}
- Time tracked: {duration}
- Phases: Research → Architecture → Implementation → Legal → Final

**Deliverables:**
[Standard appgen deliverables...]
```

---

## TaskFlow Commands Reference

### Commands Used in Integration

| Command | When | Purpose |
|---------|------|---------|
| `/task-init` | Checkpoint 1 | Initialize task tracking |
| `/task-parse <prd>` | Checkpoint 1 (optional) | Parse structured requirements |
| `/task-status <id> <status>` | Each checkpoint | Update task status |
| `/task-list` | Any phase | View current tasks |
| `/task-next` | Implementation | Get recommended next task |
| `/task-show <id>` | Any phase | View task details |
| `/task-expand <id>` | Complex tasks | Break into subtasks |

### Status Mapping

| AppGen Phase | TaskFlow Status |
|--------------|-----------------|
| Not started | `pending` |
| In progress | `in_progress` |
| Complete | `done` |
| Blocked (code review issues) | `blocked` |
| Skipped (legal pages) | `deferred` |

---

## Phase-Specific Task Examples

### Checkpoint 2: Research

```json
{
  "id": 1,
  "title": "Conduct competitive research",
  "description": "Research fintech competitors and extract patterns",
  "status": "in_progress",
  "priority": "high",
  "subtasks": [
    {
      "id": "1.1",
      "title": "Research Betterment",
      "status": "done"
    },
    {
      "id": "1.2",
      "title": "Research Wealthfront",
      "status": "in_progress"
    },
    {
      "id": "1.3",
      "title": "Extract design patterns",
      "status": "pending"
    }
  ],
  "acceptanceCriteria": [
    "3+ competitors analyzed",
    "Research saved to research/competitive-analysis.md",
    "Design patterns documented"
  ]
}
```

### Checkpoint 3: Architecture

```json
{
  "id": 2,
  "title": "Scaffold project architecture",
  "description": "Initialize React + Vite + Tailwind project",
  "status": "pending",
  "priority": "high",
  "dependencies": [1],
  "subtasks": [
    {
      "id": "2.1",
      "title": "Create project structure",
      "status": "pending"
    },
    {
      "id": "2.2",
      "title": "Run pnpm install",
      "status": "pending"
    },
    {
      "id": "2.3",
      "title": "Verify dev server",
      "status": "pending"
    }
  ],
  "acceptanceCriteria": [
    "Project structure created",
    "Dependencies installed",
    "Dev server running on port 5173"
  ]
}
```

### Checkpoint 4: Implementation

```json
{
  "id": 3,
  "title": "Implement landing page components",
  "description": "Generate all landing page sections",
  "status": "pending",
  "priority": "high",
  "dependencies": [2],
  "subtasks": [
    {
      "id": "3.1",
      "title": "Hero component",
      "status": "pending"
    },
    {
      "id": "3.2",
      "title": "Features section",
      "status": "pending"
    },
    {
      "id": "3.3",
      "title": "Trust indicators",
      "status": "pending"
    },
    {
      "id": "3.4",
      "title": "Pricing section",
      "status": "pending"
    },
    {
      "id": "3.5",
      "title": "CTA section",
      "status": "pending"
    }
  ],
  "acceptanceCriteria": [
    "All components generated with docstrings",
    "Code review passed",
    "Accessibility compliant",
    "Preview screenshot captured"
  ]
}
```

---

## Error Handling

### TaskFlow Not Available

```markdown
# User requests TaskFlow integration
User: "Use TaskFlow for this project"

# Detection fails
Agent: "I don't see TaskFlow installed on this system.
Would you like to:
1. Continue with standard AppGen workflow
2. Install TaskFlow first (provide instructions)

What would you like to do?"
```

### TaskFlow Command Fails

```bash
# Graceful degradation
if ! /task-init 2>/dev/null; then
  echo "TaskFlow command failed. Continuing with standard workflow..."
  TASKFLOW_ENABLED=false
fi
```

**Never crash AppGen due to TaskFlow issues.**

---

## Session Context Tracking

### Store Integration State

**In appgen session metadata:**

```json
{
  "project": "investwise - appgen",
  "taskflow": {
    "available": true,
    "enabled": true,
    "initialized": true,
    "task_count": 12,
    "current_task": 3,
    "current_phase": "implementation"
  }
}
```

### Use for Context Awareness

```markdown
# When resuming session
Agent: "Resuming InvestWise project..."

# Check TaskFlow state
if taskflow.enabled:
  current_task = /task-show {current_task}

  "TaskFlow Status:
   - Current task: #{current_task.id} - {current_task.title}
   - Status: {current_task.status}
   - Progress: {completed}/{total} tasks complete

   Should I continue with task #{current_task.id}?"
```

---

## Benefits of Integration

**For Users:**
- ✅ Visual task progress during long generations
- ✅ Clear dependency tracking
- ✅ Resume capability if session interrupted
- ✅ Structured completion checklist
- ✅ Historical record of work done

**For Agents:**
- ✅ Clear next-action recommendations (`/task-next`)
- ✅ Dependency awareness (don't start blocked tasks)
- ✅ Progress context across checkpoints
- ✅ Shared task list with other agents

---

## Usage Example

### Full Session with TaskFlow

```
User: /appgen fintech landing page for InvestWise

Agent: [Detects TaskFlow]
TaskFlow detected. Track this project with tasks? (y/n)

User: y

Agent: ✅ TaskFlow enabled
Initializing task tracking...

/task-init
Created .tasks/ directory
Initialized master tag

Creating tasks from requirements...

Tasks created:
1. [pending] Conduct competitive research (high priority)
2. [pending] Scaffold project architecture (high priority, depends on #1)
3. [pending] Implement landing page components (medium, depends on #2)
4. [pending] Generate legal pages (low, depends on #3)
5. [pending] Final documentation (low, depends on #4)

Starting with task #1...

/task-status 1 in_progress

[Conducts research...]

/task-status 1 done

✅ Research complete
Moving to task #2...

/task-status 2 in_progress

[Scaffolds project...]

/task-status 2 done

✅ Architecture complete
Moving to task #3...

/task-status 3 in_progress

Implementing components...
- /task-status 3.1 done  # Hero
- /task-status 3.2 done  # Features
- /task-status 3.3 done  # CTA

/task-status 3 done

✅ Implementation complete

[Continues through remaining tasks...]

## FINAL REPORT

**Task Summary:**
- Total: 5 tasks, 12 subtasks
- All tasks complete ✅
- No blockers encountered
- Phases: Research → Architecture → Implementation → Legal → Final

Project complete!
```

---

## Future Enhancements (Optional)

**Potential improvements for future versions:**

1. **Effort Estimation:**
   - Track actual time vs estimated time
   - Improve estimates over time

2. **Tag-Based Organization:**
   - Use TaskFlow tags for multi-page projects
   - Separate tag per major section

3. **Template Integration:**
   - Save task templates for common project types
   - Auto-populate tasks based on project type

4. **Cross-Session Resume:**
   - Detect incomplete projects
   - Offer to resume from last checkpoint

5. **Parallel Component Generation:**
   - Use tags to track parallel component work
   - Enable distributed generation

---

## Success Criteria

**Integration is successful when:**

✅ TaskFlow detected reliably (no false negatives)
✅ User can decline without breaking workflow
✅ AppGen works identically with/without TaskFlow
✅ Tasks accurately reflect appgen phases
✅ Task statuses stay synchronized with actual progress
✅ Final report includes meaningful task summary
✅ No errors when TaskFlow unavailable
✅ Commands fail gracefully with clear messaging

---

**Version:** 1.0.0
**Created:** 2025-12-13
**Status:** Active
