---
description: Manage TaskFlow tags for parallel work contexts
---

# /task-tag

Manage tagged task lists for parallel work streams (feature branches, phases, experiments).

## What This Command Does

Tags provide isolated task contexts. Each tag has its own `tasks.json`, allowing:
- Parallel feature development without conflicts
- Phase-based project organization
- Experimental branches without affecting main tasks

## Subcommands

### `/task-tag` (no args)
Show current tag and list all available tags.

### `/task-tag list`
List all tags with stats.

### `/task-tag use <name>`
Switch to a different tag context.

### `/task-tag create <name>`
Create a new tag (optionally from current git branch).

### `/task-tag delete <name>`
Delete a tag (with confirmation).

### `/task-tag copy <from> <to>`
Copy tasks from one tag to another.

## Directory Structure

```
.tasks/
├── config.json           # Project config
├── state.json            # Current tag, timestamps
└── tags/
    ├── master/
    │   └── tasks.json    # Default tag
    ├── feat-auth/
    │   └── tasks.json
    └── phase-2/
        └── tasks.json
```

## State File (`.tasks/state.json`)

```json
{
  "currentTag": "master",
  "lastSwitched": "2025-11-29T14:30:00Z",
  "tags": {
    "master": {
      "created": "2025-11-29T10:00:00Z",
      "description": "Main task list"
    },
    "feat-auth": {
      "created": "2025-11-29T12:00:00Z",
      "description": "Authentication feature",
      "branch": "feat/user-authentication"
    }
  }
}
```

## Workflow

### Show Current Tag (`/task-tag`)

```
┌─────────────────────────────────────────────────────────────────┐
│ TaskFlow Tags: my-project                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Current: master                                                 │
│                                                                 │
│ Available tags:                                                 │
│   • master (active)     8 tasks (3 done, 1 in progress)         │
│   • feat-auth           5 tasks (0 done)                        │
│   • phase-2             0 tasks                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Commands:                                                       │
│   /task-tag use <name>     Switch to tag                        │
│   /task-tag create <name>  Create new tag                       │
│   /task-tag delete <name>  Remove tag                           │
└─────────────────────────────────────────────────────────────────┘
```

### Create Tag (`/task-tag create <name>`)

**Arguments:**
- `<name>` - Tag name (lowercase, hyphens allowed, no spaces)
- `--from-branch` - Auto-name from current git branch
- `--copy-from=<tag>` - Copy tasks from another tag
- `--description="..."` - Optional description

**Workflow:**

1. Validate tag name (alphanumeric + hyphens, no spaces)
2. Check tag doesn't already exist
3. Create directory `.tasks/tags/<name>/`
4. Create empty `tasks.json` (or copy if `--copy-from`)
5. Update `state.json` with new tag
6. Optionally switch to new tag

```
/task-tag create feat-auth --description="User authentication feature"

Created tag: feat-auth
Location: .tasks/tags/feat-auth/tasks.json
Tasks: 0

Switch to this tag now? [Y/n]
```

**With --from-branch:**

```bash
# On branch feat/user-authentication
/task-tag create --from-branch

Detected branch: feat/user-authentication
Creating tag: feat-user-authentication

Created tag: feat-user-authentication
Branch linked: feat/user-authentication

Switch to this tag now? [Y/n]
```

### Switch Tag (`/task-tag use <name>`)

**Workflow:**

1. Validate tag exists
2. Check for unsaved work in current tag (in_progress tasks)
3. Update `state.json` with new current tag
4. Display new context summary

```
/task-tag use feat-auth

⚠ Warning: You have 1 task in progress on 'master':
   Task 3: Implement caching

Switch anyway? This won't lose progress - you can switch back.
[Y]es / [N]o / [C]omplete first

> Y

Switched to tag: feat-auth
Tasks: 5 (0 done, 0 in progress, 5 pending)

Run /task-next to start working.
```

### Delete Tag (`/task-tag delete <name>`)

**Safeguards:**
- Cannot delete currently active tag
- Cannot delete `master` tag (protected)
- Requires confirmation
- Shows task count before deletion

```
/task-tag delete feat-auth

⚠ Delete tag 'feat-auth'?
   Contains: 5 tasks (2 done, 3 pending)
   This cannot be undone.

Type 'delete feat-auth' to confirm:
```

### Copy Tasks (`/task-tag copy <from> <to>`)

**Options:**
- `--status=<status>` - Only copy tasks with specific status
- `--renumber` - Renumber task IDs in destination (default: true)

```
/task-tag copy master phase-2 --status=pending

Copying from 'master' to 'phase-2':
  - 5 pending tasks selected
  - IDs will be renumbered starting at 1

Proceed? [Y/n]

Copied 5 tasks to 'phase-2'.
```

## Integration with Other Commands

All task commands operate on the **current tag**:

- `/task-init` creates `master` tag by default
- `/task-parse` saves to current tag
- `/task-list` shows current tag's tasks
- `/task-next` selects from current tag
- `/task-status` updates in current tag

**Tag-aware output:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Tasks: my-project [feat-auth]                                   │
│        ^^^^^^^^^^^^^^^^^^^^^ shows current tag if not master    │
├─────────────────────────────────────────────────────────────────┤
```

## Edge Cases

### Tag Name Validation

Valid: `master`, `feat-auth`, `phase-2`, `v1-release`
Invalid: `Feat Auth`, `feat/auth`, `master!`, `my tag`

```
/task-tag create "my feature"

Error: Invalid tag name 'my feature'
Tag names must be lowercase alphanumeric with hyphens only.
Examples: feat-auth, phase-2, bugfix-login
```

### Non-existent Tag

```
/task-tag use nonexistent

Error: Tag 'nonexistent' does not exist.

Available tags:
  • master
  • feat-auth

Create it with: /task-tag create nonexistent
```

### Protected Master Tag

```
/task-tag delete master

Error: Cannot delete 'master' tag.
The master tag is protected as the default context.

To remove all tasks from master, use /task-parse with a new PRD
or manually clear .tasks/tags/master/tasks.json
```

### Git Branch Integration

When `autoTagFromBranch: true` in config:

```
# Automatically detect and offer to create/switch tags based on git branch

$ git checkout -b feat/new-feature

# Next task command detects branch change
/task-next

Detected git branch: feat/new-feature
No matching tag found.

Create tag 'feat-new-feature' for this branch? [Y/n]
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Invalid tag name | Show naming rules and examples |
| Tag already exists | Suggest `use` or `--force` to overwrite |
| Tag not found | List available tags, suggest create |
| Delete active tag | Must switch first |
| Delete master | Blocked (protected) |
| No `.tasks/` directory | Run `/task-init` first |

## Examples

```bash
# Show current tag and list all
/task-tag

# Create tag for feature work
/task-tag create feat-user-auth --description="User authentication"

# Create from current git branch
/task-tag create --from-branch

# Switch to different tag
/task-tag use feat-user-auth

# Copy pending tasks to new phase
/task-tag create phase-2
/task-tag copy master phase-2 --status=pending

# Clean up completed feature branch
/task-tag use master
/task-tag delete feat-user-auth
```

## Related

- Command: /task-init (creates master tag)
- Command: /task-list (shows current tag's tasks)
- Design: ~/.claude/knowledge/guides/taskflow-design.md
