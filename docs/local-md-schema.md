# .local.md Configuration Schema

Unified configuration format for all GSC plugins using YAML frontmatter in markdown files.

## Overview

All GSC plugins use `.local.md` files for configuration with:
- **YAML frontmatter** for structured settings
- **Markdown body** for documentation/notes (optional)
- **Two-tier hierarchy**: Global (`~/.gsc-plugins/`) and project-level (`.{plugin}.local.md`)

## File Locations

```
~/.gsc-plugins/                    # Global configs (user defaults)
├── appgen.local.md
├── webgen.local.md
├── taskflow.local.md
├── worklog.local.md
└── docs.local.md

{PROJECT}/                         # Project-specific overrides
├── .appgen.local.md              # Overrides global appgen config
├── .webgen.local.md              # Overrides global webgen config
└── .taskflow.local.md            # Overrides global taskflow config
```

## Configuration Hierarchy

```
1. Project-specific: {PROJECT}/.{plugin}.local.md  (highest priority)
2. Global: ~/.gsc-plugins/{plugin}.local.md        (user defaults)
3. Plugin defaults: Built-in fallbacks             (lowest priority)
```

## Schema Format

### Common Fields (All Plugins)

```yaml
---
# Required
version: "1.0"                    # Schema version

# Optional (all plugins)
knowledge_storage: sqlite         # sqlite | markdown | worklog
knowledge_path: ~/.gsc-plugins/knowledge
last_updated: 2026-01-11T21:30:00Z
---
```

### AppGen Schema

```yaml
---
version: "1.0"
knowledge_storage: sqlite

# Tech stack preferences
preferences:
  framework: nextjs               # nextjs | remix | astro | vite
  database: postgresql            # postgresql | sqlite | mysql | mongodb
  orm: prisma                     # prisma | drizzle | typeorm
  auth: authjs                    # authjs | clerk | lucia | custom
  styling: tailwind               # tailwind | css-modules | styled-components
  testing: vitest                 # vitest | jest | playwright

# Project defaults
defaults:
  typescript: true
  eslint: true
  prettier: true
  docker: false

# Documentation
auto_docs: true
docs_format: markdown             # markdown | mdx
---

# AppGen Configuration Notes

Any additional notes about your preferences or project-specific requirements.
```

### WebGen Schema

```yaml
---
version: "1.0"
knowledge_storage: sqlite

# Tech stack preferences
preferences:
  framework: nextjs               # nextjs | astro | gatsby
  styling: tailwind               # tailwind | css | scss
  components: shadcn              # shadcn | radix | headless
  deployment: vercel              # vercel | netlify | cloudflare

# Design system
design:
  color_scheme: system            # light | dark | system
  font_primary: inter
  font_mono: jetbrains-mono
  border_radius: 0.5rem

# Documentation
auto_docs: true
---
```

### TaskFlow Schema

```yaml
---
version: "1.0"

# Behavior
checkpoints:
  - parse
  - execute
  - complete
sync_todowrite: true
default_priority: medium
default_num_tasks: 10
default_tag: master
auto_tag_from_branch: false

# Integrations
plane:
  enabled: true
  workspace: gsdev
  project: null                   # Auto-detect from module

gitea:
  enabled: false
  repo: null
  auto_sync: false
  label_prefix: null
---
```

### Worklog Schema

```yaml
---
version: "1.0"

# Database backend
backend: sqlite                   # sqlite | postgresql
db_path: ~/.claude/worklog/worklog.db

# PostgreSQL (if backend: postgresql)
postgres:
  host: localhost
  port: 5433
  database: worklog
  # Credentials via gopass or environment

# Hooks behavior
hooks: light                      # off | remind | light | full | aggressive

# Session tracking
track_sessions: true
auto_recall_context: true
---
```

### Docs Schema

```yaml
---
version: "1.0"
knowledge_storage: worklog

# Paths
docs_root: ~/docs
main_guide: ~/docs/README.md
journal_dir: /tmp

# Behavior
auto_reconcile: false
validate_links: true
validate_frontmatter: true
---
```

## Parsing Rules

### Reading Configuration

```python
def read_config(plugin: str, project_path: str = None) -> dict:
    """
    Read plugin configuration with hierarchy:
    1. Project-specific (if exists)
    2. Global (if exists)
    3. Built-in defaults
    """
    config = get_builtin_defaults(plugin)

    # Layer global config
    global_path = Path.home() / ".gsc-plugins" / f"{plugin}.local.md"
    if global_path.exists():
        config.update(parse_frontmatter(global_path))

    # Layer project config (highest priority)
    if project_path:
        project_config = Path(project_path) / f".{plugin}.local.md"
        if project_config.exists():
            config.update(parse_frontmatter(project_config))

    return config
```

### Frontmatter Parsing

```python
import yaml
import re

def parse_frontmatter(file_path: Path) -> dict:
    """Parse YAML frontmatter from .local.md file."""
    content = file_path.read_text()

    # Match frontmatter between --- markers
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    return yaml.safe_load(match.group(1)) or {}
```

## Migration from Legacy Formats

### TaskFlow JSON → .local.md

```bash
# Old format: ~/.claude/task-config.json
# New format: ~/.gsc-plugins/taskflow.local.md

/task-migrate-config
```

### Docs ENV vars → .local.md

```bash
# Old format: DOCS_ROOT, KNOWLEDGE_BASE environment variables
# New format: ~/.gsc-plugins/docs.local.md

/docs-init
```

## Validation

### Required Fields

| Plugin | Required Fields |
|--------|-----------------|
| appgen | version |
| webgen | version |
| taskflow | version |
| worklog | version, backend |
| docs | version, docs_root |

### Type Validation

```yaml
# String enums
knowledge_storage: [sqlite, markdown, worklog]
backend: [sqlite, postgresql]
hooks: [off, remind, light, full, aggressive]

# Booleans
sync_todowrite: boolean
auto_docs: boolean
typescript: boolean

# Arrays
checkpoints: array<string>

# Objects
preferences: object
plane: object
gitea: object
```

## Best Practices

1. **Start with global config**: Set up `~/.gsc-plugins/{plugin}.local.md` with your defaults
2. **Override per-project**: Use `.{plugin}.local.md` for project-specific needs
3. **Document in markdown body**: Use the markdown section for notes and context
4. **Version your configs**: Include `version` field for future migrations
5. **Use worklog when available**: Enables cross-project learning

## Examples

### Minimal AppGen Config

```yaml
---
version: "1.0"
knowledge_storage: sqlite
---
```

### Full WebGen Config with Notes

```yaml
---
version: "1.0"
knowledge_storage: worklog

preferences:
  framework: nextjs
  styling: tailwind
  components: shadcn
  deployment: vercel

design:
  color_scheme: dark
  font_primary: geist
  border_radius: 0.75rem
---

# My WebGen Preferences

## Design Philosophy
I prefer minimal, functional designs with:
- Dark mode by default
- Generous whitespace
- Subtle animations

## Common Components
- Use shadcn/ui for all form elements
- Prefer server components where possible
- Always include loading states
```

---

**Schema Version:** 1.0
**Last Updated:** 2026-01-11
**Related:** INFA-635, unified-humming-dawn.md
