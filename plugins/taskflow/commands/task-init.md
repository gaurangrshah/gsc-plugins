---
description: Initialize TaskFlow task tracking in current project
---

# /task-init

Initialize the TaskFlow task management system in the current project directory.

## What This Command Does

1. Detect current environment (atlas, dev-vm, or default)
2. Create `.tasks/` directory structure with tag support
3. Create `master` tag with empty `tasks.json`
4. Create `state.json` to track current tag
5. **Auto-detect Gitea** and offer to enable sync (graceful fallback if unavailable)
6. Register project in central index (if index path configured)

## Arguments

- `[project-name]` - Optional project name (defaults to directory name)
- `--no-index` - Skip registering in central index
- `--tag=<name>` - Create with initial tag other than `master`
- `--no-gitea` - Skip Gitea auto-detection (local only)
- `--gitea` - Enable Gitea sync without prompting (assumes available)

## Prerequisites

- Must be in a directory (project root)
- Write permissions to current directory

## Workflow

### Step 1: Environment Detection

Read hostname and load config from `~/.claude/task-config.json`:

```bash
HOSTNAME=$(hostname)
```

Match against configured environments to get workspace path and index location.

If no environment matches, use defaults with warning:
```
Warning: Unknown environment 'my-host'. Using default configuration.
Project will not be added to central index.
```

### Step 2: Validate Location

**Check current directory is suitable:**

```python
cwd = os.getcwd()

# Must be a directory (not root, not home directly)
if cwd in ['/', os.path.expanduser('~')]:
    error("Cannot initialize TaskFlow in root or home directory.")
    suggest("Navigate to a project directory first.")

# Should not be inside .tasks/ or similar
if '.tasks' in cwd:
    error("Cannot initialize inside a .tasks directory.")
```

**Check for existing initialization:**

If `.tasks/` exists:
```
┌─────────────────────────────────────────────────────────────────┐
│ TaskFlow already initialized in this directory                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Found: .tasks/                                                  │
│ Tags: master, feat-auth                                         │
│ Tasks: 8 total (3 done, 1 in progress)                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Options:                                                        │
│   • Continue using existing setup                               │
│   • Reinitialize (WARNING: deletes all tasks)                   │
│   • Cancel                                                      │
└─────────────────────────────────────────────────────────────────┘
```

Use AskUserQuestion for reinitialize decision.

### Step 3: Create Directory Structure

```bash
mkdir -p .tasks/tags/master
```

**Structure created:**
```
.tasks/
├── config.json          # Project-level config (optional overrides)
├── state.json           # Current tag tracking
└── tags/
    └── master/
        └── tasks.json   # Default tag task list
```

### Step 4: Create State File

Create `.tasks/state.json`:

```json
{
  "currentTag": "master",
  "lastSwitched": "<ISO-8601-timestamp>",
  "tags": {
    "master": {
      "created": "<ISO-8601-timestamp>",
      "description": "Main task list"
    }
  }
}
```

### Step 5: Create Tasks File

Create `.tasks/tags/master/tasks.json`:

```json
{
  "version": "1.0",
  "project": "<project-name>",
  "tag": "master",
  "prdSource": null,
  "created": "<ISO-8601-timestamp>",
  "updated": "<ISO-8601-timestamp>",
  "tasks": []
}
```

### Step 6: Gitea Auto-Detection

**Check if Gitea is available:**

```bash
# Try to reach Gitea API via ubuntu-mini
ssh -o ConnectTimeout=3 ubuntu-mini 'source ~/.config/gitea/credentials 2>/dev/null && \
  curl -s --max-time 3 "${GITEA_URL}/api/v1/version" \
  -H "Authorization: token ${GITEA_TOKEN}" 2>/dev/null | jq -r .version' 2>/dev/null
```

**If Gitea is reachable:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Gitea detected at git.internal.muhaha.dev                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Enable Gitea sync for this project?                             │
│                                                                 │
│ This will:                                                      │
│   • Create issues in gs/tasks when you run /task-parse          │
│   • Sync task status changes to Gitea kanban                    │
│   • Allow visual task management at:                            │
│     http://git.internal.muhaha.dev/gs/tasks/projects            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ [Y]es - Enable Gitea sync                                       │
│ [N]o  - Local TaskFlow only                                     │
└─────────────────────────────────────────────────────────────────┘
```

**If Gitea is NOT reachable:**
```
Note: Gitea sync not available (ubuntu-mini unreachable or Gitea offline)
      Continuing with local TaskFlow only.
      Run /task-sync later to enable Gitea integration.
```

**Store Gitea config if enabled:**

Update `.tasks/config.json`:
```json
{
  "projectName": "<project-name>",
  "gitea": {
    "enabled": true,
    "repo": "gs/tasks",
    "autoSync": true,
    "labelPrefix": "<project-slug>"
  }
}
```

If user declines or Gitea unavailable:
```json
{
  "projectName": "<project-name>",
  "gitea": {
    "enabled": false
  }
}
```

### Step 7: Create Project Config

Create `.tasks/config.json`:

```json
{
  "projectName": "<project-name>",
  "checkpoints": ["parse", "execute", "complete"],
  "syncTodoWrite": true,
  "gitea": {
    "enabled": true|false,
    "repo": "gs/tasks",
    "autoSync": true,
    "labelPrefix": "<project-slug>"
  }
}
```

**Gitea config fields:**
- `enabled`: Whether Gitea sync is active
- `repo`: Target Gitea repository (default: gs/tasks)
- `autoSync`: Auto-push to Gitea after /task-parse and status changes
- `labelPrefix`: Prefix for Gitea labels to group project tasks

### Step 8: Update Central Index

If index path is configured for environment:

1. Read existing index or create new one
2. Add/update project entry
3. Write back to index file

```json
{
  "version": "1.0",
  "projects": {
    "<project-slug>": {
      "name": "<project-name>",
      "path": "<absolute-path-to-project>",
      "created": "<ISO-8601-timestamp>",
      "lastAccessed": "<ISO-8601-timestamp>",
      "currentTag": "master",
      "stats": {
        "total": 0,
        "pending": 0,
        "in_progress": 0,
        "done": 0
      }
    }
  }
}
```

**Index file creation:**
If index file doesn't exist, create it:
```json
{
  "version": "1.0",
  "projects": {}
}
```

**Handle index errors gracefully:**
- If index directory doesn't exist: warn and skip
- If index file is corrupted: warn, backup, create fresh
- If no write permission: warn and skip

### Step 9: Confirm Success

**With Gitea enabled:**
```
TaskFlow initialized in: /home/gs/workspace/projects/my-project

Structure created:
  .tasks/
  ├── config.json (gitea: enabled)
  ├── state.json (tracking: master tag)
  └── tags/master/tasks.json

Registered in: ~/workspace/.task-index.json
Gitea sync: enabled → gs/tasks (auto-sync on)
Kanban: http://git.internal.muhaha.dev/gs/tasks/projects

Next steps:
  1. Create a PRD document in docs/PRD/
  2. Run /task-parse docs/PRD/your-feature.md
     (Tasks will auto-sync to Gitea)

Or run /task to see status overview.
```

**Without Gitea (local only):**
```
TaskFlow initialized in: /home/gs/workspace/projects/my-project

Structure created:
  .tasks/
  ├── config.json (gitea: disabled)
  ├── state.json (tracking: master tag)
  └── tags/master/tasks.json

Registered in: ~/workspace/.task-index.json
Gitea sync: disabled (run /task-sync to enable later)

Next steps:
  1. Create a PRD document in docs/PRD/
  2. Run /task-parse docs/PRD/your-feature.md

Or run /task to see status overview.
```

## Edge Cases

### Directory Name Contains Special Characters

```
# In directory: /home/gs/workspace/My Project (2024)
/task-init

Project name derived: my-project-2024
Slug: my-project-2024

Using sanitized name. Override with: /task-init "Custom Name"
```

**Sanitization rules:**
- Lowercase
- Replace spaces with hyphens
- Remove special characters except hyphens
- Collapse multiple hyphens

### Git Repository Detection

If in a git repository, offer to use repo name:

```
Detected git repository: my-awesome-repo

Use repository name as project name? [Y/n]
```

### Nested Projects

If parent directory has `.tasks/`:

```
Warning: Parent directory contains TaskFlow initialization.
  Parent: /home/gs/workspace/projects/.tasks/

Continue with nested initialization? This creates separate task tracking.
[Y]es / [N]o
```

### Non-Writable Directory

```
Error: Cannot write to current directory.

Check permissions:
  Directory: /home/gs/workspace/readonly-project
  Required: Write permission

Try: sudo chown $USER:$USER /path/to/project
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Root or home directory | Block with clear message |
| `.tasks/` exists | Offer reinitialize or continue |
| No write permission | Error with chmod/chown suggestion |
| Index file corrupt | Backup, warn, continue without index |
| Index directory missing | Create it or skip indexing |
| Special chars in name | Sanitize and show result |
| Nested project | Warn and confirm |

## Examples

```bash
# Initialize in current directory (auto-detects Gitea)
/task-init

# Initialize with specific project name
/task-init my-awesome-project

# Initialize without adding to central index
/task-init --no-index

# Initialize with custom initial tag
/task-init --tag=phase-1

# Initialize with Gitea sync enabled (skip detection prompt)
/task-init --gitea

# Initialize local-only, skip Gitea detection entirely
/task-init --no-gitea
```

## Related

- Command: /task-parse (next step after init)
- Command: /task-tag (manage tags)
- Command: /task-sync (manual Gitea sync)
- Design: ~/.claude/knowledge/guides/taskflow-design.md
- Config: ~/.claude/task-config.json
- Gitea: http://git.internal.muhaha.dev/gs/tasks/projects
