# TaskFlow Task Hygiene & Note Prompts

Capturing institutional knowledge through valuable note-taking.

---

## Autonomous Mode (Agents/Orchestrators)

**If running autonomously (no user prompts), follow this section only.**

### Agent Self-Documentation Protocol

When TaskFlow is used by agents (appgen, webgen, subagents), prompts are disabled. Agents MUST self-document by calling `backend.addNote()` at key moments.

### Required Note Points

| Event | Note Type | What to Capture |
|-------|-----------|-----------------|
| Starting task | `started` | Approach being taken |
| Decision made | `decision` | What was chosen and why |
| Unexpected behavior | `gotcha` | What surprised you, how resolved |
| Workaround used | `workaround` | What hack was needed, why |
| Blocked | `blocked` | What's blocking, what's needed |
| Task complete | `completed` | Summary, changes, follow-ups |

### Autonomous Workflow

```python
# At task start
backend.addNote(task_id, f"Starting: {approach_summary}", "started")

# When making decisions (REQUIRED for non-trivial choices)
backend.addNote(task_id,
    f"Chose {option} over {alternatives} because {rationale}",
    "decision")

# When hitting unexpected issues
backend.addNote(task_id,
    f"Gotcha: {what_happened}. Resolution: {how_fixed}",
    "gotcha")

# When using workarounds
backend.addNote(task_id,
    f"Workaround: {hack_description}. Ideal: {proper_solution}. Reason: {why_not_ideal}",
    "workaround")

# At task completion (REQUIRED)
backend.addNote(task_id,
    f"Completed. Changes: {files_modified}. Outcome: {result}",
    "completed")
```

### Minimum Requirements (Autonomous)

Before marking ANY task `done` in autonomous mode:

```python
def validateCompletion(task_id):
    notes = backend.getNotes(task_id)

    # Must have at least started + completed notes
    has_started = any(n["type"] == "started" for n in notes)
    has_completed = any(n["type"] == "completed" for n in notes)

    if not (has_started and has_completed):
        # Add auto-generated completion note
        backend.addNote(task_id,
            "Task completed (auto-generated - agent did not provide notes)",
            "completed")
```

### Orchestrator Enforcement

Orchestrators (appgen-orchestrator, webgen-orchestrator) should:

1. **Before dispatching task:** Add `started` note with context
2. **After agent returns:** Validate notes exist
3. **If no notes:** Add summary from agent output
4. **Promote valuable notes:** Flag decisions/gotchas for worklog

```python
# In orchestrator
def completeCheckpoint(task_id, agent_output):
    notes = backend.getNotes(task_id)

    # Extract decisions from agent output
    decisions = extractDecisions(agent_output)
    for decision in decisions:
        backend.addNote(task_id, decision, "decision")

    # Extract gotchas
    gotchas = extractGotchas(agent_output)
    for gotcha in gotchas:
        backend.addNote(task_id, gotcha, "gotcha")

    # Add completion summary
    backend.addNote(task_id, summarize(agent_output), "completed")
```

### Worklog Auto-Sync (Autonomous)

In autonomous mode, automatically sync high-value notes to worklog without prompting:

```python
def autoSyncToWorklog(task_id):
    if not config.get("autoSyncToWorklog"):
        return

    notes = backend.getNotes(task_id)

    for note in notes:
        # Auto-promote decisions and gotchas
        if note["type"] in ["decision", "gotcha", "workaround"]:
            mcp__worklog__store_memory(
                key=f"taskflow_{task_id}_{note['id']}",
                content=note["content"],
                memory_type="fact",
                importance=7 if note["type"] == "decision" else 8,
                tags=f"taskflow,{note['type']},auto-captured"
            )
```

---

## Interactive Mode (User-Driven)

**The rest of this document applies to interactive (non-autonomous) usage.**

Skip this section if in autonomous mode.

---

## Philosophy

> Tasks are more than checkboxes. The journey matters as much as the destination.

**Good task hygiene captures:**
- Decisions made and why
- Gotchas and surprises encountered
- Workarounds and technical debt created
- Failed approaches (so others don't repeat them)
- References to PRs, commits, documentation

**Bad task hygiene:**
- Just marking done with no context
- Process dumps without insight
- Notes that are useful to no one

---

## Note Types

| Type | When to Use | Icon |
|------|-------------|------|
| `started` | Beginning work on a task | 🚀 |
| `progress` | Meaningful progress update | 📝 |
| `decision` | Choice made between options | ⚖️ |
| `gotcha` | Surprise or unexpected finding | ⚠️ |
| `workaround` | Hack or technical debt | 🔧 |
| `blocked` | Why work is blocked | 🚧 |
| `unblocked` | How blocker was resolved | ✅ |
| `completed` | Completion summary | 🎉 |
| `reference` | Links, PRs, commits | 🔗 |
| `review` | Feedback from review | 👀 |

---

## Status-Triggered Prompts

### Starting a Task (→ in_progress)

**Prompt:**
```
Starting: "Implement login endpoint"

Any initial notes? (optional)

Examples:
- Approach you're planning to take
- Files you expect to modify
- Dependencies you need first
```

**If user provides note:** Save as `started` type

**If user skips:** Auto-generate minimal note:
```
Started work on this task.
```

---

### Completing a Task (→ done)

**Prompt (required for high priority tasks):**
```
Completing: "Implement login endpoint"

Please add completion notes:

1. What was the outcome?
2. Any gotchas or surprises?
3. Any technical debt or follow-ups?

[Required for high-priority tasks]
```

**AskUserQuestion:**
```json
{
  "question": "Add completion notes for this task?",
  "header": "Notes",
  "options": [
    {
      "label": "Add notes",
      "description": "Capture what was done, gotchas, follow-ups"
    },
    {
      "label": "Mark done (no notes)",
      "description": "Skip notes - not recommended for complex tasks"
    }
  ],
  "multiSelect": false
}
```

---

### Marking Blocked (→ blocked)

**Prompt (required):**
```
Blocking: "Add OAuth integration"

What's blocking this task?

Examples:
- Waiting on API credentials
- Dependency on task-003
- Need clarification on requirements
```

**Must provide reason.** Blocking without explanation is not allowed.

---

### Marking Unblocked (→ in_progress from blocked)

**Prompt:**
```
Unblocking: "Add OAuth integration"

How was this unblocked?

[Previous blocker: Waiting on API credentials]
```

---

## Smart Note Suggestions

When specific patterns are detected, prompt for appropriate notes:

### After Error Resolution

```
Detected: Multiple error/fix cycles in this session

Would you like to capture what went wrong and how it was fixed?

This helps future debugging of similar issues.
```

### After Approach Change

```
Detected: Significant code changes/reversions

Did you change approaches? Worth documenting why the first
approach didn't work?
```

### After Long Session

```
This task has been in_progress for 2+ hours.

Consider adding a progress note to capture:
- Current state
- What's been completed
- What remains
```

---

## Note Templates

### Decision Note

```markdown
**[DECISION]** {title}

**Context:** {what was the situation}
**Options considered:**
1. {option A} - {pros/cons}
2. {option B} - {pros/cons}

**Chosen:** {option}
**Rationale:** {why this option}
```

### Gotcha Note

```markdown
**[GOTCHA]** {title}

**Expected:** {what I thought would happen}
**Actual:** {what actually happened}
**Resolution:** {how I fixed/worked around it}
**Future note:** {what to watch out for}
```

### Workaround Note

```markdown
**[WORKAROUND]** {title}

**Ideal solution:** {what should happen}
**Current hack:** {what we're doing instead}
**Reason:** {why we can't do it right}
**Tech debt:** {should we track this?}
```

### Completion Note

```markdown
**[COMPLETED]** {summary}

**Changes:**
- {file1}: {what changed}
- {file2}: {what changed}

**Testing:** {how it was verified}
**Follow-ups:** {any new tasks needed}
**PR/Commit:** {reference}
```

---

## Worklog Integration (Interactive)

If worklog is configured, prompt to promote valuable notes:

```python
def maybePromoteToWorklog(note):
    if not config.get("autoSyncToWorklog"):
        return

    # Only promote high-value notes
    if note.type in ["decision", "gotcha", "workaround"]:
        # Ask user if this should be preserved
        if askUser("Save this to knowledge base for future reference?"):
            mcp__worklog__store_knowledge(
                category="development",
                title=f"{note.type}: {extractTitle(note)}",
                content=note.content,
                tags=f"taskflow,{note.type},{task.project}"
            )
```

---

## Configuration

In `.taskflow.local.md`:

```yaml
---
backend: local

hygiene:
  # Require notes when completing high-priority tasks
  requireCompletionNotes: true

  # Require blocker reason
  requireBlockerReason: true

  # Prompt for notes on status changes (interactive only)
  promptForNotes: true

  # Auto-sync valuable notes to worklog
  autoSyncToWorklog: false

  # Minimum note length (0 = no minimum)
  minNoteLength: 0

  # Smart suggestions based on session activity
  smartSuggestions: true
---
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `/task-note <id> "note"` | Add note to task |
| `/task-note <id> --type=decision` | Add typed note |
| `/task-status <id> done --note="..."` | Complete with note |
| `/task-status <id> blocked --reason="..."` | Block with reason |

---

**Hygiene Version:** 2.0
**Philosophy:** Capture the journey, not just the destination
