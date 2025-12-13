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
5. Register project in central index (if index path configured)

## Arguments

- `[project-name]` - Optional project name (defaults to directory name)
- `--no-index` - Skip registering in central index
- `--tag=<name>` - Create with initial tag other than `master`

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

### Step 6: Create Project Config (Optional)

Create `.tasks/config.json` only if overrides needed:

```json
{
  "projectName": "<project-name>",
  "checkpoints": ["parse", "execute", "complete"],
  "syncTodoWrite": true
}
```

*Skip this file if using all defaults - less clutter.*

### Step 7: Update Central Index

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

### Step 8: Confirm Success

```
TaskFlow initialized in: /home/gs/workspace/projects/my-project

Structure created:
  .tasks/
  ├── state.json (tracking: master tag)
  └── tags/master/tasks.json

Registered in: ~/workspace/.task-index.json

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
# Initialize in current directory
/task-init

# Initialize with specific project name
/task-init my-awesome-project

# Initialize without adding to central index
/task-init --no-index

# Initialize with custom initial tag
/task-init --tag=phase-1
```

## Related

- Command: /task-parse (next step after init)
- Command: /task-tag (manage tags)
- Design: ~/.claude/knowledge/guides/taskflow-design.md
- Config: ~/.claude/task-config.json
