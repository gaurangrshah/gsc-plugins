---
name: task-setup
description: First-run setup for TaskFlow - configure backend and preferences
trigger: auto  # Triggered when no config exists
version: "2.0"
---

# TaskFlow First-Run Setup

Triggered automatically when TaskFlow commands are used without existing configuration.

---

## Trigger Conditions

This setup runs when:
1. No `./.taskflow.local.md` in current directory
2. No `~/.gsc-plugins/taskflow.local.md` globally
3. User runs any `/task-*` command

---

## Setup Flow

### Step 1: Detect Available Backends

```python
def detectBackends():
    backends = []

    # Local is always available (default)
    backends.append({
        "name": "local",
        "available": True,
        "label": "Local (.tasks/)",
        "description": "Store tasks locally - works offline, no setup"
    })

    # Check Plane MCP
    if tool_exists("mcp__plane__list_issues"):
        try:
            workspaces = mcp__plane__list_workspaces()
            if workspaces.get("results"):
                ws = workspaces["results"][0]
                backends.append({
                    "name": "plane",
                    "available": True,
                    "label": "Plane",
                    "description": f"Sync with Plane - workspace: {ws['slug']}",
                    "workspace": ws["slug"]
                })
        except:
            pass

    # Check GitHub CLI
    try:
        result = bash("gh auth status 2>&1")
        if "Logged in" in result:
            # Try to get current repo
            repo_info = bash("gh repo view --json owner,name 2>/dev/null || echo '{}'")
            repo = json.loads(repo_info)
            if repo.get("owner"):
                desc = f"Sync with GitHub Issues - {repo['owner']['login']}/{repo['name']}"
            else:
                desc = "Sync with GitHub Issues - authenticated"
            backends.append({
                "name": "github",
                "available": True,
                "label": "GitHub",
                "description": desc,
                "owner": repo.get("owner", {}).get("login"),
                "repo": repo.get("name")
            })
    except:
        pass

    # Check Linear MCP (if exists)
    if tool_exists("mcp__linear__list_issues"):
        backends.append({
            "name": "linear",
            "available": True,
            "label": "Linear",
            "description": "Sync with Linear issues"
        })

    return backends
```

### Step 2: Display Detection Results

```markdown
┌─────────────────────────────────────────────────────────────┐
│  TaskFlow Setup                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Detected integrations:                                     │
│                                                             │
│    ✓ Plane     - workspace: gsdev                           │
│    ✓ GitHub    - authenticated as myuser                    │
│    ✗ Linear    - not detected                               │
│                                                             │
│  Default: Local .tasks/ (no setup required)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Ask Backend Preference

Use AskUserQuestion with local as default:

```python
def askBackendPreference(backends):
    options = []

    # Local always first (default)
    options.append({
        "label": "Local only (Recommended)",
        "description": "Use .tasks/ folder - works offline, no external sync"
    })

    # Add detected integrations
    for backend in backends:
        if backend["name"] != "local" and backend["available"]:
            options.append({
                "label": backend["label"],
                "description": backend["description"]
            })

    return AskUserQuestion({
        "question": "Where should TaskFlow store tasks?",
        "header": "Backend",
        "options": options,
        "multiSelect": False
    })
```

### Step 4: Backend-Specific Configuration

#### If Local Selected

No additional config needed. Proceed to scope.

#### If Plane Selected

```python
def configurePlane(detected_workspace):
    # Get projects in workspace
    projects = mcp__plane__list_projects(workspace_slug=detected_workspace)

    options = []
    for project in projects.get("results", []):
        options.append({
            "label": project["name"],
            "description": project.get("description", "")[:50]
        })

    selected = AskUserQuestion({
        "question": "Which Plane project should tasks go to?",
        "header": "Project",
        "options": options,
        "multiSelect": False
    })

    return {
        "workspace": detected_workspace,
        "project": selected
    }
```

#### If GitHub Selected

```python
def configureGitHub(detected_owner, detected_repo):
    if detected_owner and detected_repo:
        # Confirm detected repo
        confirm = AskUserQuestion({
            "question": f"Use {detected_owner}/{detected_repo} for task tracking?",
            "header": "Repository",
            "options": [
                {"label": "Yes", "description": f"Use {detected_owner}/{detected_repo}"},
                {"label": "Different repo", "description": "Specify another repository"}
            ],
            "multiSelect": False
        })

        if confirm == "Yes":
            return {"owner": detected_owner, "repo": detected_repo}

    # Manual entry needed
    print("Enter repository as owner/repo (e.g., myuser/tasks):")
    # Would need text input here
    return {"owner": "...", "repo": "..."}
```

### Step 5: Ask Scope

```python
def askScope():
    return AskUserQuestion({
        "question": "Save this configuration for?",
        "header": "Scope",
        "options": [
            {
                "label": "This project only",
                "description": "Save to ./.taskflow.local.md"
            },
            {
                "label": "All projects (global default)",
                "description": "Save to ~/.gsc-plugins/taskflow.local.md"
            },
            {
                "label": "This session only",
                "description": "Don't save - will ask again next time"
            }
        ],
        "multiSelect": False
    })
```

### Step 6: Write Configuration

```python
def writeConfig(backend, backend_config, scope):
    config = {
        "backend": backend,
        backend: backend_config,
        "hygiene": {
            "requireCompletionNotes": True,
            "requireBlockerReason": True,
            "promptForNotes": True,
            "autoSyncToWorklog": False
        }
    }

    # Convert to YAML frontmatter
    yaml_content = f"""---
backend: {backend}

{backend}:
{indent(yaml.dump(backend_config), "  ")}

hygiene:
  requireCompletionNotes: true
  requireBlockerReason: true
  promptForNotes: true
  autoSyncToWorklog: false
---

# TaskFlow Configuration

Configured on {datetime.now().isoformat()}
"""

    if scope == "This project only":
        path = "./.taskflow.local.md"
    elif scope == "All projects (global default)":
        path = os.path.expanduser("~/.gsc-plugins/taskflow.local.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
    else:
        # Session only - store in memory, don't write
        SESSION_CONFIG = config
        return

    with open(path, "w") as f:
        f.write(yaml_content)
```

### Step 7: Confirm & Initialize

```python
def confirmSetup(backend, backend_config, scope, path):
    if backend == "local":
        # Create .tasks/ directory
        os.makedirs(".tasks", exist_ok=True)

        print(f"""
┌─────────────────────────────────────────────────────────────┐
│  TaskFlow configured!                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Backend: Local (.tasks/)                                   │
│  Storage: ./.tasks/tasks.json                               │
│  Config:  {path}
│                                                             │
│  Tasks stored locally - no external sync.                   │
│  Change anytime: /task config --backend=plane               │
│                                                             │
│  Get started:                                               │
│    /task-add "Your first task"                              │
│    /task-list                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
""")

    elif backend == "plane":
        print(f"""
┌─────────────────────────────────────────────────────────────┐
│  TaskFlow configured!                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Backend: Plane                                             │
│  Workspace: {backend_config['workspace']}
│  Project: {backend_config['project']}
│  Config: {path}
│                                                             │
│  Tasks sync to:                                             │
│  https://plane.internal.muhaha.dev/{backend_config['workspace']}/{backend_config['project']}
│                                                             │
│  Get started:                                               │
│    /task-add "Your first task"                              │
│    /task-list                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
""")

    elif backend == "github":
        print(f"""
┌─────────────────────────────────────────────────────────────┐
│  TaskFlow configured!                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Backend: GitHub Issues                                     │
│  Repository: {backend_config['owner']}/{backend_config['repo']}
│  Config: {path}
│                                                             │
│  Tasks sync to:                                             │
│  https://github.com/{backend_config['owner']}/{backend_config['repo']}/issues
│                                                             │
│  Get started:                                               │
│    /task-add "Your first task"                              │
│    /task-list                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
""")
```

---

## Quick Setup (No Prompts)

For autonomous mode or quick setup:

```bash
# Use local backend (default)
/task-init --backend=local

# Use Plane with auto-detection
/task-init --backend=plane --auto

# Use GitHub with current repo
/task-init --backend=github --auto

# Specify explicitly
/task-init --backend=plane --workspace=gsdev --project=work
```

---

## Re-Configuration

To change configuration later:

```bash
# View current config
/task config

# Change backend
/task config --backend=github

# Reset and re-run setup
/task config --reset
```

---

## Error Handling

### No Integrations Available

```
No external integrations detected.

TaskFlow will use local storage (.tasks/).

To set up integrations later:
  • Plane: Configure MCP server in settings
  • GitHub: Run `gh auth login`
  • Linear: Configure MCP server in settings

Continuing with local backend...
```

### Integration Connection Failed

```
Warning: Could not connect to Plane.

Options:
  1. Use local backend instead
  2. Retry connection
  3. Configure manually

[1/2/3]: _
```

---

**Skill Version:** 2.0
**Triggered By:** Any /task-* command when no config exists
