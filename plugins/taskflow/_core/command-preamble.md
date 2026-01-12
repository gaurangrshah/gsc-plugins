# TaskFlow Command Preamble

**Include at the start of ALL TaskFlow commands.**

---

## Backend Loading

```python
# REQUIRED: Load backend before any task operations
backend = loadBackend()

if not backend:
    # No config exists - trigger first-run setup
    # See: skills/task-setup/skill.md
    triggerSetup()
    return

# Note: loadBackend() handles backwards compatibility automatically:
# - Checks .local.md formats first (new v2.x)
# - Falls back to ~/.claude/task-config.json (old v1.x)
# - Shows migration notice if old format detected
# - See: _core/backend-loader.md (Backwards Compatibility section)
```

---

## Import Reference

All commands have access to:

```python
# Backend operations (from backend-interface.md)
backend.createTask(input)
backend.getTask(id)
backend.updateTask(id, updates)
backend.deleteTask(id)
backend.setStatus(id, status, note)
backend.addNote(id, content, type)
backend.getNotes(id)
backend.listTasks(filters)
backend.searchTasks(query)
backend.createEpic(title, description)
backend.addSubtask(epicId, task)
backend.linkDependency(taskId, dependsOnId)
backend.sync()
backend.getBackendInfo()

# Config access
config = loadConfig()
config.backend          # "local" | "plane" | "github"
config.hygiene          # Hygiene settings
config.defaults         # Default values
```

---

## Hygiene Integration

For commands that change task status:

```python
# Check if interactive or autonomous
if isAutonomous():
    # See: _core/task-hygiene.md (Autonomous Mode section)
    # Auto-add notes, no prompts
    pass
else:
    # See: _core/task-hygiene.md (Interactive Mode section)
    # Prompt for notes based on config
    if config.hygiene.promptForNotes:
        note = promptForNote(status_change)
        if note:
            backend.addNote(task_id, note, noteType)
```

---

## Error Handling

```python
try:
    result = backend.operation(...)
except TaskNotFoundError as e:
    print(f"Task not found: {e.task_id}")
    return
except BackendConnectionError as e:
    print(f"Cannot connect to {e.backend}: {e.cause}")
    print("Try: /task config --backend=local")
    return
except ValidationError as e:
    print(f"Invalid {e.field}: {e.reason}")
    return
```

---

## Common Patterns

### Get Task or Error

```python
task = backend.getTask(task_id)
if not task:
    print(f"Task not found: {task_id}")
    return
```

### List with Filters

```python
tasks = backend.listTasks({
    "status": ["pending", "in_progress"],
    "priority": ["high"],
    "limit": 20
})
```

### Status Change with Notes

```python
# Follows hygiene protocol
task = backend.setStatus(task_id, "done", completion_note)

# Auto-sync if configured
if config.hygiene.autoSyncToWorklog:
    syncNotesToWorklog(task_id)
```

---

**Version:** 2.0
**Used By:** All /task-* commands
