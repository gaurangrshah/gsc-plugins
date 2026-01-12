---
name: task-migrate-config
description: Migrate from old JSON config to new .local.md format
args: [--dry-run] [--force] [--global]
version: "2.0"
---

# /task-migrate-config

Migrate TaskFlow configuration from old JSON format to new `.local.md` format.

## Usage

```bash
/task-migrate-config                    # Interactive migration
/task-migrate-config --dry-run          # Preview changes without writing
/task-migrate-config --force            # Overwrite existing .local.md
/task-migrate-config --global           # Migrate to global config only
```

---

## Old Config Format (v1.x)

**Location:** `~/.claude/task-config.json`

```json
{
  "version": "1.1",
  "environments": {
    "my-machine": {
      "hostname": "my-machine",
      "workspacePath": "/home/user/projects",
      "indexPath": "/home/user/projects/.task-index.json"
    }
  },
  "defaults": {
    "checkpoints": ["parse", "execute", "complete"],
    "syncTodoWrite": true,
    "defaultPriority": "medium",
    "defaultNumTasks": 10,
    "defaultTag": "master"
  }
}
```

---

## New Config Format (v2.x)

**Location:** `~/.gsc-plugins/taskflow.local.md` (global) or `./.taskflow.local.md` (project)

```yaml
---
backend: local

local:
  path: .tasks/

# Legacy settings preserved
legacy:
  environments:
    my-machine:
      workspacePath: /home/user/projects
      indexPath: /home/user/projects/.task-index.json

defaults:
  defaultPriority: medium
  defaultTag: master
  checkpoints:
    - parse
    - execute
    - complete
  syncTodoWrite: true

hygiene:
  requireCompletionNotes: true
  requireBlockerReason: true
  promptForNotes: true
  autoSyncToWorklog: false
---

# TaskFlow Configuration

Migrated from ~/.claude/task-config.json on <timestamp>
```

---

## Workflow

### Step 1: Check for Existing Config

```python
old_config_path = os.path.expanduser("~/.claude/task-config.json")
new_global_path = os.path.expanduser("~/.gsc-plugins/taskflow.local.md")
new_project_path = "./.taskflow.local.md"

# Check if old config exists
if not os.path.exists(old_config_path):
    print("No old config found at ~/.claude/task-config.json")
    print("Nothing to migrate. Use /task-init to create new config.")
    return

# Check if new config already exists
if os.path.exists(new_global_path) and not args.force:
    print(f"New config already exists: {new_global_path}")
    print("Use --force to overwrite, or delete it first.")
    return
```

### Step 2: Read Old Config

```python
with open(old_config_path, 'r') as f:
    old_config = json.load(f)

version = old_config.get("version", "1.0")
environments = old_config.get("environments", {})
defaults = old_config.get("defaults", {})

print(f"Found TaskFlow config v{version}")
print(f"  Environments: {len(environments)}")
print(f"  Defaults: {len(defaults)} settings")
```

### Step 3: Detect Available Backends

```python
# Detect what backends are available
backends = detectBackends()

# Default to local (preserving v1.x behavior)
suggested_backend = "local"

# If Plane or GitHub available, suggest but don't require
if any(b["name"] == "plane" and b["available"] for b in backends):
    print("\n  Plane integration detected - you can switch after migration")
if any(b["name"] == "github" and b["available"] for b in backends):
    print("  GitHub integration detected - you can switch after migration")
```

### Step 4: Build New Config

```python
def buildNewConfig(old_config, backend="local"):
    """Convert old JSON config to new YAML format."""

    new_config = {
        "backend": backend,
        backend: {"path": ".tasks/"} if backend == "local" else {},
        "defaults": {},
        "hygiene": {
            "requireCompletionNotes": True,
            "requireBlockerReason": True,
            "promptForNotes": True,
            "autoSyncToWorklog": False
        }
    }

    # Map old defaults to new
    old_defaults = old_config.get("defaults", {})

    if "defaultPriority" in old_defaults:
        new_config["defaults"]["defaultPriority"] = old_defaults["defaultPriority"]

    if "defaultTag" in old_defaults:
        new_config["defaults"]["defaultTag"] = old_defaults["defaultTag"]

    if "checkpoints" in old_defaults:
        new_config["defaults"]["checkpoints"] = old_defaults["checkpoints"]

    if "syncTodoWrite" in old_defaults:
        new_config["defaults"]["syncTodoWrite"] = old_defaults["syncTodoWrite"]

    # Preserve environment configs in legacy section (for reference)
    if old_config.get("environments"):
        new_config["legacy"] = {
            "environments": old_config["environments"],
            "note": "Preserved from v1.x config. Environments are no longer used in v2.x."
        }

    return new_config
```

### Step 5: Preview Changes (--dry-run)

```python
if args.dry_run:
    print("\n--- DRY RUN - No changes will be made ---\n")
    print("Old config: ~/.claude/task-config.json")
    print(f"New config: {new_global_path if args.global else 'auto-selected'}")
    print("\nNew configuration would be:")
    print("---")
    print(yaml.dump(new_config, default_flow_style=False))
    print("---")
    return
```

### Step 6: Choose Scope

```python
if not args.global:
    scope = AskUserQuestion({
        "question": "Where should the migrated config be saved?",
        "header": "Scope",
        "options": [
            {
                "label": "Global (Recommended)",
                "description": f"Save to {new_global_path}"
            },
            {
                "label": "This project only",
                "description": f"Save to {new_project_path}"
            }
        ],
        "multiSelect": False
    })

    target_path = new_global_path if "Global" in scope else new_project_path
else:
    target_path = new_global_path
```

### Step 7: Backup Old Config

```python
# Create backup directory
backup_dir = os.path.expanduser("~/.claude/.backups")
os.makedirs(backup_dir, exist_ok=True)

# Backup with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = f"{backup_dir}/task-config.json.{timestamp}.bak"

shutil.copy2(old_config_path, backup_path)
print(f"\nBackup created: {backup_path}")
```

### Step 8: Write New Config

```python
# Ensure target directory exists
os.makedirs(os.path.dirname(target_path), exist_ok=True)

# Convert to YAML frontmatter format
yaml_content = f"""---
backend: {new_config["backend"]}

{new_config["backend"]}:
{indent(yaml.dump(new_config[new_config["backend"]], default_flow_style=False), "  ")}

defaults:
{indent(yaml.dump(new_config["defaults"], default_flow_style=False), "  ")}

hygiene:
{indent(yaml.dump(new_config["hygiene"], default_flow_style=False), "  ")}

{f"legacy:" + chr(10) + indent(yaml.dump(new_config.get("legacy", {}), default_flow_style=False), "  ") if new_config.get("legacy") else ""}
---

# TaskFlow Configuration

Migrated from ~/.claude/task-config.json
Date: {datetime.now().isoformat()}
Original version: {old_config.get("version", "unknown")}

## Changes in v2.0

- Backend abstraction: Local, Plane, GitHub, Linear support
- Task hygiene: Notes for decisions, gotchas, workarounds
- Epic support: Complex tasks become epics with subtasks
- Project/global scope: Per-project or global settings

## Switch Backend

To use a different backend:

```bash
/task config --backend=plane
/task config --backend=github
```
"""

with open(target_path, 'w') as f:
    f.write(yaml_content)

print(f"New config written: {target_path}")
```

### Step 9: Offer to Remove Old Config

```python
response = AskUserQuestion({
    "question": "Remove old config file?",
    "header": "Cleanup",
    "options": [
        {
            "label": "Yes, remove it",
            "description": "Delete ~/.claude/task-config.json (backup preserved)"
        },
        {
            "label": "No, keep both",
            "description": "Keep old config for reference"
        }
    ],
    "multiSelect": False
})

if "Yes" in response:
    os.remove(old_config_path)
    print("Old config removed.")
else:
    print("Old config preserved at ~/.claude/task-config.json")
```

### Step 10: Confirm Success

```
┌─────────────────────────────────────────────────────────────┐
│  Migration Complete!                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Old config: ~/.claude/task-config.json                     │
│  New config: ~/.gsc-plugins/taskflow.local.md               │
│  Backup: ~/.claude/.backups/task-config.json.20260112.bak   │
│                                                             │
│  Backend: local (default - preserves v1.x behavior)         │
│  Environments: Preserved in 'legacy' section                │
│                                                             │
│  To switch backends:                                        │
│    /task config --backend=plane                             │
│    /task config --backend=github                            │
│                                                             │
│  Test your setup:                                           │
│    /task-list                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Field Mapping

| Old Field (v1.x) | New Field (v2.x) | Notes |
|------------------|------------------|-------|
| `version` | *(removed)* | Version in plugin.json |
| `environments.*.workspacePath` | `legacy.environments.*.workspacePath` | Preserved for reference |
| `environments.*.indexPath` | `legacy.environments.*.indexPath` | No longer used |
| `defaults.checkpoints` | `defaults.checkpoints` | Direct mapping |
| `defaults.syncTodoWrite` | `defaults.syncTodoWrite` | Direct mapping |
| `defaults.defaultPriority` | `defaults.defaultPriority` | Direct mapping |
| `defaults.defaultNumTasks` | *(removed)* | No longer configurable |
| `defaults.defaultTag` | `defaults.defaultTag` | Direct mapping |
| *(new)* | `backend` | Backend type |
| *(new)* | `hygiene.*` | Task hygiene settings |

---

## Error Handling

### Old Config Not Found

```
No old config found at ~/.claude/task-config.json

Nothing to migrate. TaskFlow v2.0 will auto-configure on first use.
Run /task-init or any /task-* command to get started.
```

### New Config Already Exists

```
TaskFlow v2.0 config already exists:
  ~/.gsc-plugins/taskflow.local.md

Options:
  1. Use --force to overwrite
  2. Delete existing file and run migration again
  3. Keep existing config (no migration needed)
```

### Invalid JSON in Old Config

```
Error reading old config: ~/.claude/task-config.json

  JSON parse error at line 5: unexpected token

Fix the JSON syntax error and try again, or use:
  /task-init --force
to create fresh config (old settings will be lost).
```

---

## Examples

```bash
# Preview what migration would do
/task-migrate-config --dry-run

# Migrate to global config
/task-migrate-config --global

# Force overwrite existing config
/task-migrate-config --force

# Full migration with cleanup
/task-migrate-config
# Follow prompts to choose scope and cleanup
```

---

**Command Version:** 2.0
**One-time operation:** Only needed when upgrading from v1.x to v2.x
