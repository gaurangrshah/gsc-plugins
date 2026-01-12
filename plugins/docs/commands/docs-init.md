---
name: docs-init
description: Initialize documentation structure for a project with frontmatter standards
args: [--path <dir>] [--guide <name>] [--global] [--with-worklog]
version: "2.0"
---

# /docs-init

Initialize documentation structure and configuration.

## Usage

```bash
/docs-init                              # Interactive setup
/docs-init --path ~/docs                # Specify docs root
/docs-init --global                     # Save as global default
/docs-init --with-worklog               # Enable worklog integration
```

## Options

| Flag | Description |
|------|-------------|
| `--path <dir>` | Documentation root directory |
| `--guide <name>` | Main guide filename (default: `guide.md`) |
| `--global` | Save config globally (`~/.gsc-plugins/docs.local.md`) |
| `--project` | Save config for project only (`./.docs.local.md`) |
| `--with-worklog` | Enable worklog integration |

---

## Workflow

### Step 1: Check Existing Config

```python
# Check for existing configs
project_config = "./.docs.local.md"
global_config = os.path.expanduser("~/.gsc-plugins/docs.local.md")

if os.path.exists(project_config):
    print("Docs already configured for this project.")
    print(f"Config: {project_config}")
    response = AskUserQuestion({
        "question": "What would you like to do?",
        "header": "Config exists",
        "options": [
            {"label": "Keep existing", "description": "Exit without changes"},
            {"label": "Reconfigure", "description": "Update configuration"},
            {"label": "View config", "description": "Show current settings"}
        ]
    })
    if response == "Keep existing":
        return
    elif response == "View config":
        showConfig(project_config)
        return
```

### Step 2: Prompt for Settings

```python
# Use arg or prompt for docs_root
if args.path:
    docs_root = args.path
else:
    response = AskUserQuestion({
        "question": "Where should documentation be stored?",
        "header": "Docs Root",
        "options": [
            {"label": "~/docs (Recommended)", "description": "Standard location in home directory"},
            {"label": "./docs", "description": "In current project directory"},
            {"label": "Custom path", "description": "Specify a different location"}
        ]
    })

    if "~/docs" in response:
        docs_root = "~/docs"
    elif "./docs" in response:
        docs_root = "./docs"
    else:
        docs_root = input("Enter documentation path: ")

# Expand path
docs_root = os.path.expanduser(docs_root)
```

### Step 3: Detect Worklog

```python
# Check for worklog MCP tools
worklog_mcp = tool_exists('mcp__worklog__store_knowledge')

# Check for worklog.db in common locations
worklog_db = None
for path in ['~/.claude/worklog/worklog.db', '~/.gsc-plugins/worklog.db']:
    if os.path.exists(os.path.expanduser(path)):
        worklog_db = path
        break

# Prompt for worklog integration
if worklog_mcp or worklog_db or args.with_worklog:
    if worklog_mcp:
        print("Worklog MCP detected - can store learnings cross-project")
    elif worklog_db:
        print(f"Worklog database found: {worklog_db}")

    if not args.with_worklog:
        response = AskUserQuestion({
            "question": "Enable worklog integration?",
            "header": "Worklog",
            "options": [
                {"label": "Yes (Recommended)", "description": "Store learnings to shared knowledge base"},
                {"label": "No", "description": "Keep documentation isolated"}
            ]
        })
        enable_worklog = "Yes" in response
    else:
        enable_worklog = True
else:
    enable_worklog = False
```

### Step 4: Select Scope

```python
if not args.global and not args.project:
    response = AskUserQuestion({
        "question": "Save configuration for?",
        "header": "Scope",
        "options": [
            {"label": "This project", "description": "Save to ./.docs.local.md"},
            {"label": "All projects (global)", "description": "Save to ~/.gsc-plugins/docs.local.md"}
        ]
    })
    scope = "global" if "global" in response.lower() else "project"
else:
    scope = "global" if args.global else "project"
```

### Step 5: Create Directory Structure

```python
# Create docs directories
dirs_to_create = [
    docs_root,
    f"{docs_root}/security",
    f"{docs_root}/guides",
    f"{docs_root}/services",
    f"{docs_root}/baselines"
]

for dir_path in dirs_to_create:
    os.makedirs(dir_path, exist_ok=True)

# Create subdirectory READMEs
subdirs = ['security', 'guides', 'services']
for subdir in subdirs:
    readme_path = f"{docs_root}/{subdir}/README.md"
    if not os.path.exists(readme_path):
        writeSubdirReadme(readme_path, subdir)
```

### Step 6: Create Main Guide (if needed)

```python
guide_name = args.guide or "guide.md"
main_guide = f"{docs_root}/{guide_name}"

if not os.path.exists(main_guide):
    writeMainGuideTemplate(main_guide)
    print(f"Created main guide: {main_guide}")
else:
    print(f"Main guide exists: {main_guide}")
```

### Step 7: Create Frontmatter Schema

```python
schema_path = f"{docs_root}/FRONTMATTER-SCHEMA.md"
if not os.path.exists(schema_path):
    writeFrontmatterSchema(schema_path)
```

### Step 8: Write Config File

```python
knowledge_base = '~/.gsc-plugins/knowledge'

config_content = f"""---
docs_root: {docs_root}
main_guide: {main_guide}
knowledge_base: {knowledge_base}

worklog:
  enabled: {str(enable_worklog).lower()}
  use_mcp: {str(worklog_mcp).lower()}
{"  db_path: " + worklog_db if worklog_db and not worklog_mcp else ""}

defaults:
  frontmatter_required: true
  validate_on_save: false
  journal_dir: /tmp
---

# Docs Configuration

{"Global" if scope == "global" else "Project"} documentation settings.
Initialized: {datetime.now().isoformat()}

## Paths

- **docs_root**: {docs_root}
- **main_guide**: {main_guide}
- **knowledge_base**: {knowledge_base}

## Integration

- **Worklog**: {"Enabled" if enable_worklog else "Disabled"}
"""

# Determine config path
if scope == "global":
    config_path = os.path.expanduser("~/.gsc-plugins/docs.local.md")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
else:
    config_path = "./.docs.local.md"

with open(config_path, 'w') as f:
    f.write(config_content)

print(f"Config saved: {config_path}")
```

### Step 9: Confirm Success

```
┌─────────────────────────────────────────────────────────────┐
│  Docs initialized!                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Structure created:                                         │
│    ~/docs/                                                  │
│    ├── guide.md          (main guide)                       │
│    ├── FRONTMATTER-SCHEMA.md                                │
│    ├── security/                                            │
│    ├── guides/                                              │
│    ├── services/                                            │
│    └── baselines/                                           │
│                                                             │
│  Config: ~/.gsc-plugins/docs.local.md (global)              │
│  Worklog: Enabled (MCP)                                     │
│                                                             │
│  Next steps:                                                │
│    1. Edit ~/docs/guide.md with your system info            │
│    2. Run /docs-validate to check structure                 │
│    3. Use inline updates for all changes                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Templates

### Main Guide Template

```python
def writeMainGuideTemplate(path):
    content = """---
title: "System Guide"
type: reference
created: {date}
updated: {date}
---

# System Guide

> Single source of truth for system configuration and operations.

## Current State

| Component | Status | Notes |
|-----------|--------|-------|
| Example   | ✅ OK  | -     |

## Quick Reference

### Access Points

- **Service A**: https://...
- **Service B**: https://...

## Configuration

### Section 1

Configuration details here.

**Key Lessons:**
- Lesson 1
- Lesson 2

### Section 2

More configuration.

## Troubleshooting

### Common Issues

**Issue:** Description
**Solution:** How to fix

## Change History

### {date}
- Initial documentation created
""".format(date=datetime.now().strftime('%Y-%m-%d'))

    with open(path, 'w') as f:
        f.write(content)
```

---

## Examples

```bash
# Basic initialization (interactive)
/docs-init

# Initialize with specific path
/docs-init --path ~/projects/myapp/docs

# Initialize as global default
/docs-init --global

# Initialize with worklog integration
/docs-init --with-worklog
```

---

**Command Version:** 2.0
**Creates:** Directory structure, config file, main guide template
