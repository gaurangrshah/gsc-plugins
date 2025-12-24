# GSC Plugins - Development Guide

**This file provides context for Claude Code agents working on this repository.**

## CRITICAL: This is a PUBLIC Package

**This package is distributed via claude-plugins.dev to users worldwide.**

### Agnosticism Rules (Non-Negotiable)

Before making ANY changes, verify:

| Check | Violation Example | Correct |
|-------|------------------|---------|
| No absolute user paths | `/home/gs/workspace/` | `~/projects/` |
| No internal domains | `git.internal.muhaha.dev` | `${GITEA_URL}` or `example.com` |
| No hardcoded hostnames | `ubuntu-mini`, `atlas` | Environment variables |
| No personal agent names | `jarvis`, `alfred` | `claude` or configurable |

**Pre-commit check:**
```bash
grep -rE "/home/\w+|\.internal\.|ubuntu-mini|atlas" plugins/
# Must return NO matches
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## Repository Purpose

This is a **Claude Code plugin marketplace** - a collection of plugins distributed via GitHub.

- **NOT a central npm registry** - plugins are installed via `claude plugin marketplace add`
- **Each plugin is standalone** - they work independently but can integrate when co-installed
- **Source of truth for plugin code** - changes here propagate to all users via marketplace updates

## Development Workflow

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feat/plugin-name-feature-description
   ```

2. **Make changes to plugins in `plugins/` directory**

3. **Update version in plugin.json AND README.md:**
   ```bash
   # Example for worklog plugin
   # plugins/worklog/.claude-plugin/plugin.json -> update "version"
   # plugins/worklog/README.md -> update version number
   # README.md (root) -> update version in plugins table
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat(plugin-name): description"
   git push -u origin HEAD
   ```

5. **Merge to main** (after review if applicable)

### Version Sync Requirements

When updating any plugin version, you MUST update ALL of these locations:

| Location | What to Update |
|----------|----------------|
| `plugins/{name}/.claude-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `plugins/{name}/README.md` | Version number in header |
| `README.md` (root) | Plugins table, Integration Matrix versions |

**The Integration Matrix in root README.md shows version numbers - keep these in sync!**

## Plugin Structure

Each plugin MUST follow this structure:

```
plugins/{plugin-name}/
├── .claude-plugin/
│   └── plugin.json          # REQUIRED: Name, version, description
├── commands/                 # Slash commands (/command-name)
│   └── command-name.md
├── skills/                   # Skills (agent-invocable capabilities)
│   └── skill-name/
│       └── skill.md
├── hooks/                    # Optional: Claude Code hooks
├── mcp/                      # Optional: MCP server
└── README.md                 # REQUIRED: Full documentation
```

### plugin.json Schema

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Brief description",
  "author": { "name": "author" },
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "commands": ["command1", "command2"],
  "skills": ["skill1", "skill2"]
}
```

## Sync with local-plugins

### How Installation Works

```
GitHub repo (gsc-plugins)
    ↓
claude plugin marketplace add https://github.com/gaurangrshah/gsc-plugins.git
    ↓
~/.claude/plugins/marketplaces/gsc-plugins/  (cached)
    ↓
claude plugin install worklog@gsc-plugins
    ↓
~/.claude/plugins/local-plugins/worklog/     (active)
```

### Local Development Workflow

For local testing during development:
- Develop in this repo's `plugins/` directory
- Test by copying to `~/.claude/plugins/local-plugins/`
- Commit and push to GitHub
- Other machines update via marketplace

### Propagating Updates to Other Machines

After pushing to GitHub, other machines update via:

```bash
# Update marketplace index
claude plugin marketplace update gsc-plugins

# Reinstall specific plugin (--force overwrites)
claude plugin install worklog@gsc-plugins --force
```

## Plugins Overview

| Plugin | Purpose | Key Files |
|--------|---------|-----------|
| **webgen** | Website generation | 5-checkpoint workflow |
| **appgen** | Full-stack app generation | 8-phase workflow |
| **worklog** | Cross-session persistence | SQLite/PostgreSQL, MCP server |
| **taskflow** | Task management | PRD parsing, deps |
| **docs** | Documentation management | Validation, reconciliation |

## Testing Changes

Before committing:

1. **Validate plugin.json is valid JSON**
2. **Verify version numbers are consistent**
3. **Test commands/skills work in Claude Code session**
4. **Check README documentation is accurate**

## Common Issues

### "Plugin not found" after marketplace add

```bash
# Ensure marketplace was added correctly
claude plugin marketplace list

# Update the marketplace
claude plugin marketplace update gsc-plugins
```

### Changes not reflecting after push

Other machines need to:
1. `claude plugin marketplace update gsc-plugins`
2. `claude plugin install {plugin}@gsc-plugins --force`

### Version mismatch between local-plugins and repo

Always check both locations have the same version when debugging.

## Integration Notes

### Plugin Detection

Plugins detect each other by checking for skill/command availability:
- WebGen checks for TaskFlow commands before offering task tracking
- Worklog hooks run regardless of other plugins

### Cross-Plugin Communication

- Use worklog's `agent_chat` table for async agent messaging
- MCP tools available when worklog MCP server is installed

## File Ownership

| File/Directory | Owner | Notes |
|----------------|-------|-------|
| `plugins/*/` | This repo | Source of truth |
| `README.md` | This repo | Keep versions in sync |
| `.claude-plugin/` | This repo | Marketplace metadata |

## Do NOT Modify

- `.git/` - Git internals
- `LICENSE` - MIT license, no changes needed

## Questions?

See individual plugin READMEs for detailed documentation:
- [webgen](plugins/webgen/README.md)
- [appgen](plugins/appgen/README.md)
- [worklog](plugins/worklog/README.md)
- [taskflow](plugins/taskflow/README.md)
- [docs](plugins/docs/README.md)
