# Docs Plugin Config Loader

Logic for loading documentation configuration with backwards compatibility.

---

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Any /docs-* command or docs skill                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Check project config: ./.docs.local.md                  │
│  2. Check global config: ~/.gsc-plugins/docs.local.md       │
│  3. No config? → Run /docs-init                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Return config object for skill/command to use              │
└─────────────────────────────────────────────────────────────┘
```

---

## Config File Format (v2.0)

### Project-level (`./.docs.local.md`)

```yaml
---
docs_root: ./docs
main_guide: ./docs/guide.md
knowledge_base: ./.knowledge

worklog:
  enabled: false
  # db_path: ~/.claude/worklog/worklog.db
---

# Docs Configuration - Project

Project-specific documentation settings.
```

### Global (`~/.gsc-plugins/docs.local.md`)

```yaml
---
docs_root: ~/docs
main_guide: ~/docs/system-guide.md
knowledge_base: ~/.gsc-plugins/knowledge

worklog:
  enabled: true
  use_mcp: true  # Use worklog MCP tools if available

defaults:
  frontmatter_required: true
  validate_on_save: false
  journal_dir: /tmp
---

# Docs Configuration - Global

Default settings for all projects.
```

---

## Load Sequence

```python
def loadDocsConfig():
    # 1. Try project-level config
    project_config = loadLocalMdConfig("./.docs.local.md")
    if project_config:
        return project_config

    # 2. Try global config
    global_config = loadLocalMdConfig("~/.gsc-plugins/docs.local.md")
    if global_config:
        return global_config

    # 3. No config found - return None (trigger setup)
    return None


def loadLocalMdConfig(path):
    """Load config from .local.md file with YAML frontmatter."""
    expanded_path = os.path.expanduser(path)
    if not os.path.exists(expanded_path):
        return None

    try:
        with open(expanded_path, 'r') as f:
            content = f.read()

        # Parse YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                config = yaml.safe_load(yaml_content)
                return normalizeConfig(config)

        return None
    except (yaml.YAMLError, IOError):
        return None


def normalizeConfig(config):
    """Normalize config to standard format with defaults."""
    normalized = {
        'docs_root': os.path.expanduser(config.get('docs_root', '~/docs')),
        'main_guide': os.path.expanduser(config.get('main_guide', '')),
        'knowledge_base': os.path.expanduser(config.get('knowledge_base', '~/.gsc-plugins/knowledge')),
        'worklog': config.get('worklog', {'enabled': False}),
        'defaults': config.get('defaults', {})
    }

    # Default main_guide if not set
    if not normalized['main_guide']:
        normalized['main_guide'] = f"{normalized['docs_root']}/guide.md"

    return normalized
```

---

## Config Fields

### Required

| Field | Type | Description |
|-------|------|-------------|
| `docs_root` | path | Root directory for documentation |
| `main_guide` | path | Path to main guide file (single source of truth) |

### Optional

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `knowledge_base` | path | `~/.gsc-plugins/knowledge` | Cross-project knowledge directory |
| `worklog.enabled` | bool | false | Enable worklog integration |
| `worklog.use_mcp` | bool | true | Use MCP tools instead of direct DB |
| `worklog.db_path` | path | - | Direct path to worklog.db (if not using MCP) |
| `defaults.frontmatter_required` | bool | true | Require frontmatter on all docs |
| `defaults.validate_on_save` | bool | false | Run validation after updates |
| `defaults.journal_dir` | path | /tmp | Directory for journal files |

---

## Usage in Commands/Skills

```python
# At start of any docs command/skill
config = loadDocsConfig()

if not config:
    print("Docs not configured. Run /docs-init to set up.")
    return

# Use config values
docs_root = config['docs_root']
main_guide = config['main_guide']
knowledge_base = config['knowledge_base']

# Check worklog integration
if config['worklog']['enabled']:
    if config['worklog'].get('use_mcp') and tool_exists('mcp__worklog__store_knowledge'):
        # Use MCP tools
        mcp__worklog__store_knowledge(...)
    elif config['worklog'].get('db_path'):
        # Use direct DB access
        sqlite3(config['worklog']['db_path'], ...)
```

---

## First-Run Setup

When no config exists, `/docs-init` runs the setup flow:

```python
def triggerDocsSetup():
    print("Docs plugin not configured.")
    print("")
    print("Run /docs-init to set up documentation structure.")
```

---

## Worklog Integration

When worklog is available, docs can store knowledge and log work.

### Detection

```python
def detectWorklog():
    # Check for worklog MCP tools
    if tool_exists('mcp__worklog__store_knowledge'):
        return {'available': True, 'type': 'mcp'}

    # Check for worklog.db path in config
    if config['worklog'].get('db_path'):
        path = os.path.expanduser(config['worklog']['db_path'])
        if os.path.exists(path):
            return {'available': True, 'type': 'sqlite', 'path': path}

    return {'available': False}
```

### Storing Knowledge

```python
def storeToWorklog(category, title, content, tags):
    worklog = detectWorklog()

    if not worklog['available']:
        return False

    if worklog['type'] == 'mcp':
        mcp__worklog__store_knowledge(
            category=category,
            title=title,
            content=content,
            tags=tags,
            source_agent="docs"
        )
    else:
        # Direct SQLite
        sqlite3(worklog['path'], f"""
            INSERT INTO knowledge_base (category, title, content, tags, source_agent)
            VALUES ('{category}', '{title}', '{content}', '{tags}', 'docs')
        """)

    return True
```

---

## Error Handling

### Config Parse Error

```
Error reading docs config: ~/.gsc-plugins/docs.local.md

  YAML parse error at line 5: unexpected token

Fix the config file or delete it to reconfigure with /docs-init.
```

### Missing Required Paths

```
Docs configuration incomplete.

  docs_root: ~/docs (exists: ✓)
  main_guide: ~/docs/guide.md (exists: ✗)

Run /docs-init to create missing files, or update your config.
```

---

**Version:** 2.0
**Used By:** All docs commands and skills
