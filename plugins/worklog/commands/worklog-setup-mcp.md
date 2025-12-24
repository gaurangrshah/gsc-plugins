---
description: Set up Python environment for worklog MCP server (cross-platform)
arguments: []
---

# Worklog Setup MCP

Set up the Python virtual environment for the worklog MCP server with intelligent cross-platform detection.

## What This Command Does

1. **Detects Python Environment** - Checks for existing version managers in order:
   - pyenv (if installed, respects user's explicit choice)
   - mise (if installed)
   - Homebrew Python (macOS only)
   - System Python

2. **Creates Virtual Environment** - Isolated venv for MCP dependencies

3. **Installs Dependencies** - fastmcp, aiosqlite, and plugin code

4. **Outputs Configuration** - Shows .mcp.json settings to use

## Workflow

### Step 1: Run Detection

Execute the detection script to find suitable Python:

```bash
PLUGIN_DIR=$(dirname $(dirname $(realpath ~/.claude/plugins.json 2>/dev/null || echo ~/.claude)))/gsc-plugins/plugins/worklog

# Or use known paths
if [[ -d /volume2/dev-env/workspace/gsc-plugins ]]; then
    PLUGIN_DIR="/volume2/dev-env/workspace/gsc-plugins/plugins/worklog"
elif [[ -d /Volumes/dev-env/workspace/gsc-plugins ]]; then
    PLUGIN_DIR="/Volumes/dev-env/workspace/gsc-plugins/plugins/worklog"
elif [[ -d /mnt/nasdevenv/workspace/gsc-plugins ]]; then
    PLUGIN_DIR="/mnt/nasdevenv/workspace/gsc-plugins/plugins/worklog"
elif [[ -d ~/workspace/gsc-plugins ]]; then
    PLUGIN_DIR="$HOME/workspace/gsc-plugins/plugins/worklog"
fi

# Run detection
source "$PLUGIN_DIR/scripts/detect-python-env.sh"
```

Show the user the detection results:

```
Python Environment Detection
==============================
OS: {macos|linux}

{If PYTHON_OK == "yes":}
✓ Found suitable Python
  Command: {PYTHON_CMD}
  Version: {PYTHON_VERSION}
  Source:  {PYTHON_SOURCE}

{If PYTHON_OK == "no":}
✗ No suitable Python found
  Required: Python >= 3.10

Recommendation:
  {PYTHON_RECOMMENDATION}
```

### Step 2: Handle Missing Python

If `PYTHON_OK` is "no", present the recommendation and ask:

> "Python 3.10+ is required for the MCP server. Would you like me to help install it?"
>
> **Recommendation:** `{PYTHON_RECOMMENDATION}`
>
> Options:
> - [A] Run the recommended command
> - [B] I'll install Python myself, then re-run this command
> - [C] Cancel setup

**If user chooses A:**

Execute the recommendation command. For example:
- macOS with brew: `brew install python@3.12`
- Linux with apt: `sudo apt-get install python3.12 python3.12-venv`
- mise: `mise use python@3.12`
- pyenv: `pyenv install 3.12 && pyenv global 3.12`

After installation, re-run detection to verify.

### Step 3: Create Virtual Environment

Once Python is available:

```bash
"$PLUGIN_DIR/scripts/setup-mcp-venv.sh"
```

This creates the venv at `$PLUGIN_DIR/mcp/.venv` and installs dependencies.

### Step 4: Configure MCP

Read the Python path from the setup output and help configure `.mcp.json`:

```bash
VENV_PYTHON=$(cat "$PLUGIN_DIR/mcp/.python-path")
```

Determine the correct database path based on your setup:

| Setup | Database Path |
|-------|---------------|
| Local (default) | ~/.claude/worklog/worklog.db |
| Shared (network mount) | /path/to/shared/worklog.db |
| PostgreSQL | Set via DATABASE_URL environment variable |

Create or update `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "worklog": {
      "type": "stdio",
      "command": "{VENV_PYTHON}",
      "args": ["-m", "worklog_mcp"],
      "env": {
        "WORKLOG_DB": "{DB_PATH}"
      }
    }
  }
}
```

### Step 5: Verify Setup

Test the MCP server:

```bash
$VENV_PYTHON -m worklog_mcp --help
```

Or run a quick tool test:

```bash
$VENV_PYTHON -c "from worklog_mcp import server; print('MCP server loads OK')"
```

### Step 6: Restart Claude Code

Inform the user:

> "Setup complete! Restart Claude Code to load the MCP server."
>
> After restart, verify with: `claude mcp list`
>
> You should see `worklog` with tools like:
> - query_table
> - search_knowledge
> - store_memory
> - log_entry

## Error Handling

**Python version too old:**
- Show current version and required version
- Provide upgrade instructions for the detected source

**venv creation fails:**
- Check disk space
- Check write permissions
- Try alternative venv location: `~/.local/share/gsc-plugins-venv`

**pip install fails:**
- Check network connectivity
- Try: `pip install --upgrade pip` first
- Check if behind proxy (offer to set PIP_PROXY)

**Database not found:**
- Verify NAS mount (network drive paths)
- Check if database was initialized with /worklog-init
- Offer to create new database or set custom WORKLOG_DB path

## Notes

- This command is idempotent - safe to run multiple times
- Existing venv will prompt before recreation
- The detection prioritizes user-managed tools (pyenv) over system Python
- On macOS, prefers Homebrew Python over the ancient system Python (3.9.6)
