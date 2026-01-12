# TaskFlow Backend Loader

Logic for detecting, selecting, and loading the appropriate backend.

---

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Any /task-* command                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Check project config: ./.taskflow.local.md              │
│  2. Check global config: ~/.gsc-plugins/taskflow.local.md   │
│  3. No config? → Detect & prompt user                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Load appropriate backend                                   │
│  Return backend instance for command to use                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Config File Format

### Project-level (`./.taskflow.local.md`)

```yaml
---
backend: plane

plane:
  workspace: gsdev
  project: work
  module: my-feature  # Optional: default module for new issues
---

# TaskFlow - My Project

Project-specific task configuration.
```

### Global (`~/.gsc-plugins/taskflow.local.md`)

```yaml
---
backend: plane

plane:
  workspace: gsdev
  project: work

github:
  owner: myuser
  repo: tasks

defaults:
  defaultPriority: medium
  agentReviewRequired: true
  promptForNotes: true
  autoSyncToWorklog: false
---

# TaskFlow Global Configuration

Default settings for all projects.
```

---

## Load Sequence

```python
def loadBackend():
    # 1. Try project-level config (new format)
    project_config = loadConfig("./.taskflow.local.md")
    if project_config and project_config.backend:
        return initBackend(project_config)

    # 2. Try global config (new format)
    global_config = loadConfig("~/.gsc-plugins/taskflow.local.md")
    if global_config and global_config.backend:
        return initBackend(global_config)

    # 3. BACKWARDS COMPATIBILITY: Check for old v1.x JSON config
    legacy_config = loadLegacyConfig("~/.claude/task-config.json")
    if legacy_config:
        print("Found legacy TaskFlow config (v1.x format)")
        print("Run /task-migrate-config to upgrade to v2.0 format")
        print("")
        # Use local backend with old defaults (preserves v1.x behavior)
        return initBackend({
            "backend": "local",
            "local": {"path": ".tasks/"},
            "defaults": legacy_config.get("defaults", {})
        })

    # 4. No config - detect and prompt
    return detectAndPrompt()


def loadLegacyConfig(path):
    """Load old v1.x JSON config format for backwards compatibility."""
    expanded_path = os.path.expanduser(path)
    if not os.path.exists(expanded_path):
        return None

    try:
        with open(expanded_path, 'r') as f:
            config = json.load(f)

        # Validate it's a v1.x config
        if "version" in config and config["version"].startswith("1."):
            return config
        if "environments" in config or "defaults" in config:
            return config

        return None
    except (json.JSONDecodeError, IOError):
        return None
```

---

## Backend Detection

### Detection Logic

```bash
# Run these checks to detect available backends

detectBackends() {
    AVAILABLE=""

    # Local is always available
    AVAILABLE="local"

    # Check Plane MCP
    # Look for mcp__plane__ tools in available tools
    if tool_exists "mcp__plane__list_issues"; then
        AVAILABLE="$AVAILABLE,plane"
    fi

    # Check GitHub CLI
    if command -v gh &>/dev/null; then
        if gh auth status &>/dev/null 2>&1; then
            AVAILABLE="$AVAILABLE,github"
        fi
    fi

    # Check Linear MCP
    if tool_exists "mcp__linear__list_issues" || \
       tool_exists "mcp__linear__create_issue"; then
        AVAILABLE="$AVAILABLE,linear"
    fi

    # Check Jira MCP (future)
    if tool_exists "mcp__jira__*"; then
        AVAILABLE="$AVAILABLE,jira"
    fi

    echo "$AVAILABLE"
}
```

### Detection Output

```yaml
detected_backends:
  - name: local
    available: true
    reason: "Always available"

  - name: plane
    available: true
    reason: "mcp__plane__* tools detected"
    workspace: gsdev  # If detectable

  - name: github
    available: true
    reason: "gh CLI authenticated"
    user: myuser

  - name: linear
    available: false
    reason: "No Linear MCP detected"
```

---

## First-Run Prompt Flow

When no config exists:

### Step 1: Show Detected Backends

```
┌─────────────────────────────────────────────────────────────┐
│  TaskFlow Setup                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Detected integrations:                                     │
│                                                             │
│    ✓ Plane     - Connected to gsdev workspace               │
│    ✓ GitHub    - Authenticated as myuser                    │
│    ✗ Linear    - Not detected                               │
│                                                             │
│  Default: Local .tasks/ folder (no setup required)          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Ask Backend Preference

Use AskUserQuestion. **Local is always the first/default option.**

**If integrations detected:**

```json
{
  "question": "Where should TaskFlow store tasks?",
  "header": "Backend",
  "options": [
    {
      "label": "Local only (Recommended)",
      "description": "Use .tasks/ folder - works offline, no external sync"
    },
    {
      "label": "Plane",
      "description": "Sync with Plane issues - detected workspace: gsdev"
    },
    {
      "label": "GitHub",
      "description": "Sync with GitHub Issues - authenticated as myuser"
    }
  ],
  "multiSelect": false
}
```

**If NO integrations detected:**

```json
{
  "question": "No issue tracker integrations detected. Use local storage?",
  "header": "Backend",
  "options": [
    {
      "label": "Yes, use local .tasks/",
      "description": "Store tasks in .tasks/ folder - works offline"
    },
    {
      "label": "Configure integration manually",
      "description": "Set up Plane/GitHub/Linear connection"
    }
  ],
  "multiSelect": false
}
```

### Step 3: Ask Scope

```json
{
  "question": "Save this preference for?",
  "header": "Scope",
  "options": [
    {
      "label": "This project only",
      "description": "Save to ./.taskflow.local.md - other projects will ask again"
    },
    {
      "label": "All projects (global)",
      "description": "Save to ~/.gsc-plugins/taskflow.local.md - becomes default"
    },
    {
      "label": "This session only",
      "description": "Don't save - will ask again next time"
    }
  ],
  "multiSelect": false
}
```

### Step 4: Backend-Specific Config

If Plane selected:

```json
{
  "question": "Which Plane project should tasks go to?",
  "header": "Project",
  "options": [
    {"label": "work", "description": "General work tasks"},
    {"label": "infra", "description": "Infrastructure tasks"},
    {"label": "personal", "description": "Personal tasks"}
  ],
  "multiSelect": false
}
```

If GitHub selected:

```
Which repository should tasks go to?

Enter as owner/repo (e.g., myuser/project-tasks): _
```

### Step 5: Save Config

Based on scope selection:

```python
if scope == "project":
    writeConfig("./.taskflow.local.md", config)
    print("Saved to ./.taskflow.local.md")

elif scope == "global":
    writeConfig("~/.gsc-plugins/taskflow.local.md", config)
    print("Saved to ~/.gsc-plugins/taskflow.local.md")

else:  # session only
    # Store in session context, don't write file
    SESSION_BACKEND = config
    print("Using for this session only")
```

### Step 6: Confirm

**If Local selected:**

```
┌─────────────────────────────────────────────────────────────┐
│  TaskFlow configured!                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Backend: Local (.tasks/)                                   │
│  Storage: ./.tasks/tasks.json                               │
│  Saved to: ~/.gsc-plugins/taskflow.local.md (global)        │
│                                                             │
│  Tasks stored locally - no external sync.                   │
│  Change anytime with: /task config --backend=plane          │
│                                                             │
│  Run /task add "your first task" to get started.            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**If Plane selected:**

```
┌─────────────────────────────────────────────────────────────┐
│  TaskFlow configured!                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Backend: Plane                                             │
│  Workspace: gsdev                                           │
│  Project: work                                              │
│  Saved to: ~/.gsc-plugins/taskflow.local.md (global)        │
│                                                             │
│  Tasks will sync to:                                        │
│  https://plane.internal.muhaha.dev/gsdev/work               │
│                                                             │
│  Run /task add "your first task" to get started.            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**If GitHub selected:**

```
┌─────────────────────────────────────────────────────────────┐
│  TaskFlow configured!                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Backend: GitHub Issues                                     │
│  Repository: myuser/my-project                              │
│  Saved to: ~/.gsc-plugins/taskflow.local.md (global)        │
│                                                             │
│  Tasks will sync to:                                        │
│  https://github.com/myuser/my-project/issues                │
│                                                             │
│  Run /task add "your first task" to get started.            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Backend Initialization

Once config is loaded, initialize the appropriate backend:

```python
def initBackend(config):
    backend_type = config.backend

    if backend_type == "plane":
        return PlaneBackend(
            workspace=config.plane.workspace,
            project=config.plane.project,
            module=config.plane.get("module")
        )

    elif backend_type == "github":
        return GitHubBackend(
            owner=config.github.owner,
            repo=config.github.repo
        )

    elif backend_type == "linear":
        return LinearBackend(
            team=config.linear.team
        )

    else:  # local (default)
        return LocalBackend(
            path=config.local.get("path", ".tasks/")
        )
```

---

## Session Context

For commands that run multiple operations, cache the backend:

```python
# At start of command
backend = loadBackend()

# Use throughout command
task = backend.createTask(...)
backend.setStatus(task.id, "in_progress")
backend.addNote(task.id, "Started work", "started")

# Backend handles all translations internally
```

---

## Error Handling

### Config Parse Error

```
Error reading TaskFlow config: ~/.gsc-plugins/taskflow.local.md

  YAML parse error at line 5: unexpected token

Fix the config file or delete it to reconfigure.
```

### Backend Connection Error

```
Cannot connect to Plane backend.

  Workspace: gsdev
  Error: mcp__plane__list_projects returned error

Options:
  1. Check Plane MCP configuration
  2. Switch to local backend: /task config --backend=local
  3. Reconfigure: /task config --reset
```

### Backend Not Available

```
Configured backend 'linear' is not available.

  Linear MCP tools not detected.

Options:
  1. Install Linear MCP server
  2. Switch backend: /task config --backend=plane
  3. Use local: /task config --backend=local
```

---

## Config Commands

### View Current Config

```bash
/task config

# Output:
TaskFlow Configuration
─────────────────────────
Backend: plane
Workspace: gsdev
Project: work

Config file: ~/.gsc-plugins/taskflow.local.md (global)
```

### Change Backend

```bash
/task config --backend=github

# Prompts for GitHub-specific config, saves
```

### Reset Config

```bash
/task config --reset

# Deletes config, runs first-run setup again
```

---

## Backwards Compatibility (v1.x → v2.x)

TaskFlow v2.0 maintains backwards compatibility with v1.x JSON configs.

### Detection Priority

```
1. ./.taskflow.local.md        (project, new format)
2. ~/.gsc-plugins/taskflow.local.md  (global, new format)
3. ~/.claude/task-config.json  (global, OLD format - triggers migration notice)
4. No config                   (first-run setup)
```

### When Old Config Detected

If `~/.claude/task-config.json` exists but no `.local.md` config:

```
Found legacy TaskFlow config (v1.x format)
Run /task-migrate-config to upgrade to v2.0 format

[Command continues with local backend using old defaults]
```

**Behavior:**
- Commands still work (no breaking changes)
- Local `.tasks/` backend used (same as v1.x)
- Old `defaults` settings honored
- Migration notice shown once per session

### Migration Path

```bash
# Preview migration
/task-migrate-config --dry-run

# Run migration
/task-migrate-config

# After migration, old config can be removed
```

### Old Format Reference

**`~/.claude/task-config.json` (v1.x):**

```json
{
  "version": "1.1",
  "environments": {
    "hostname": {
      "workspacePath": "/path/to/workspace",
      "indexPath": "/path/to/.task-index.json"
    }
  },
  "defaults": {
    "checkpoints": ["parse", "execute", "complete"],
    "syncTodoWrite": true,
    "defaultPriority": "medium",
    "defaultTag": "master"
  }
}
```

**Note:** The `environments` section with `workspacePath` and `indexPath` is deprecated.
v2.0 uses project-level `.taskflow.local.md` files instead of hostname-based routing.

---

**Version:** 2.0
**Used By:** All TaskFlow commands (first step)
