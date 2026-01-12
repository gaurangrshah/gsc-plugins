---
name: task-init
description: Initialize TaskFlow in current project
args: [--backend=local|plane|github] [--global]
version: "2.0"
---

# /task-init

Initialize TaskFlow task tracking with backend selection.

## Usage

```bash
/task-init                           # Interactive setup
/task-init --backend=local           # Quick local setup
/task-init --backend=plane --global  # Plane as global default
```

## Arguments

| Flag | Description |
|------|-------------|
| `--backend` | Skip detection, use specified backend |
| `--global` | Save config globally (all projects) |
| `--project` | Save config for this project only |

---

## Workflow

### Step 1: Check Existing Config

```python
# Check for existing config
if exists("./.taskflow.local.md"):
    print("TaskFlow already configured for this project.")
    print("Use /task config to view or change settings.")
    return

if exists("~/.gsc-plugins/taskflow.local.md") and not args.project:
    print("Global TaskFlow config exists.")
    response = AskUserQuestion({
        "question": "Use global config or create project-specific?",
        "header": "Config",
        "options": [
            {"label": "Use global", "description": "Apply existing global settings"},
            {"label": "Project config", "description": "Create settings for this project only"}
        ]
    })
    if response == "Use global":
        print("Using global TaskFlow config.")
        return
```

### Step 2: Detect Available Backends

→ See `_core/backend-loader.md` for detection logic

```python
backends = detectBackends()
# Returns: [
#   {"name": "local", "available": True, ...},
#   {"name": "plane", "available": True, "workspace": "gsdev", ...},
#   {"name": "github", "available": True, "owner": "user", ...}
# ]
```

### Step 3: Display Detection Results

```
┌─────────────────────────────────────────────────────────────┐
│  TaskFlow Setup                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Detected integrations:                                     │
│    ✓ Plane   - workspace: gsdev                             │
│    ✓ GitHub  - authenticated as myuser                      │
│    ✗ Linear  - not detected                                 │
│                                                             │
│  Default: Local .tasks/ (no setup required)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Select Backend

```python
if args.backend:
    selected = args.backend
else:
    # Build options - local always first
    options = [
        {"label": "Local only (Recommended)", "description": "Use .tasks/ - works offline"}
    ]
    for b in backends:
        if b["name"] != "local" and b["available"]:
            options.append({"label": b["label"], "description": b["description"]})

    selected = AskUserQuestion({
        "question": "Where should TaskFlow store tasks?",
        "header": "Backend",
        "options": options
    })
```

### Step 5: Backend-Specific Config

#### Local (default)

No additional config needed.

#### Plane

```python
if selected == "Plane":
    # Get projects
    projects = mcp__plane__list_projects(workspace_slug=detected_workspace)

    project = AskUserQuestion({
        "question": "Which Plane project?",
        "header": "Project",
        "options": [{"label": p["name"], "description": ""} for p in projects["results"]]
    })

    backend_config = {
        "workspace": detected_workspace,
        "project": project
    }
```

#### GitHub

```python
if selected == "GitHub":
    if detected_repo:
        confirm = AskUserQuestion({
            "question": f"Use {detected_owner}/{detected_repo}?",
            "header": "Repo",
            "options": [
                {"label": "Yes", "description": f"Use current repo"},
                {"label": "Different", "description": "Specify another"}
            ]
        })
        if confirm == "Yes":
            backend_config = {"owner": detected_owner, "repo": detected_repo}
        else:
            # Manual input needed
            pass
```

### Step 6: Select Scope

```python
if not args.global and not args.project:
    scope = AskUserQuestion({
        "question": "Save configuration for?",
        "header": "Scope",
        "options": [
            {"label": "This project", "description": "Save to ./.taskflow.local.md"},
            {"label": "All projects", "description": "Save to ~/.gsc-plugins/taskflow.local.md"}
        ]
    })
else:
    scope = "All projects" if args.global else "This project"
```

### Step 7: Write Config

```python
config_content = f"""---
backend: {selected.lower()}

{selected.lower()}:
{yaml_dump(backend_config)}

hygiene:
  requireCompletionNotes: true
  requireBlockerReason: true
  promptForNotes: true
  autoSyncToWorklog: false
---

# TaskFlow Configuration

Initialized: {datetime.now().isoformat()}
"""

if scope == "This project":
    path = "./.taskflow.local.md"
else:
    path = os.path.expanduser("~/.gsc-plugins/taskflow.local.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)

write_file(path, config_content)
```

### Step 8: Initialize Local Storage (if local backend)

```python
if selected.lower() == "local":
    os.makedirs(".tasks", exist_ok=True)
    write_json(".tasks/tasks.json", {
        "version": "2.0",
        "project": os.path.basename(os.getcwd()),
        "created": datetime.now().isoformat(),
        "tasks": []
    })
```

### Step 9: Confirm

```
┌─────────────────────────────────────────────────────────────┐
│  TaskFlow initialized!                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Backend: Local (.tasks/)                                   │
│  Config:  ./.taskflow.local.md                              │
│                                                             │
│  Get started:                                               │
│    /task-add "Your first task"                              │
│    /task-parse docs/PRD/feature.md                          │
│    /task-list                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Setup (No Prompts)

```bash
# Local backend, project scope
/task-init --backend=local

# Plane backend, global scope
/task-init --backend=plane --global

# GitHub backend with current repo
/task-init --backend=github
```

---

## Reconfigure

```bash
# View current config
/task config

# Change backend
/task config --backend=plane

# Reset and re-init
/task config --reset
```

---

**Command Version:** 2.0
**Triggers:** First-run setup flow
