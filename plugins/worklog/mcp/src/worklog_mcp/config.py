"""Configuration for worklog-mcp server."""

import os
from pathlib import Path

# Database paths by system
DB_PATHS = {
    "atlas": "/volume2/dev-env/workspace/logs/worklog.db",
    "m4-mini-work": "/Volumes/dev-env/workspace/logs/worklog.db",
    "ubuntu-mini": "/mnt/nasdevenv/workspace/logs/worklog.db",
}

def get_database_path() -> Path:
    """Get the database path for the current system.

    Checks WORKLOG_DB environment variable first, then tries system-specific paths.
    """
    # Environment variable takes precedence
    if env_path := os.environ.get("WORKLOG_DB"):
        return Path(env_path)

    # Try system-specific paths
    hostname = os.uname().nodename.lower()

    for system, path in DB_PATHS.items():
        if system in hostname:
            db_path = Path(path)
            if db_path.exists():
                return db_path

    # Try all known paths
    for path in DB_PATHS.values():
        db_path = Path(path)
        if db_path.exists():
            return db_path

    raise FileNotFoundError(
        f"Could not find worklog.db. Set WORKLOG_DB environment variable or "
        f"ensure one of these paths exists: {list(DB_PATHS.values())}"
    )

# Tables available in the database
TABLES = ["memories", "knowledge_base", "entries", "research", "agent_chat"]

# Valid agent names for chat
AGENTS = ["alfred", "macadmin", "jarvis", "all"]

# Chat message statuses
CHAT_STATUSES = ["pending", "read", "replied", "resolved"]

# Chat priority levels
CHAT_PRIORITIES = ["low", "normal", "urgent"]

# Memory types
MEMORY_TYPES = ["fact", "entity", "preference", "context"]

# Memory statuses
MEMORY_STATUSES = ["staging", "promoted", "archived"]

# Task types for entries
TASK_TYPES = [
    "configuration", "deployment", "debugging",
    "documentation", "research", "maintenance", "handoff"
]

# Knowledge base categories
KB_CATEGORIES = [
    "system-administration", "development", "infrastructure",
    "decisions", "projects", "protocols"
]
