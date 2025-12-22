"""Configuration for worklog-mcp server.

Supports two backends:
- SQLite (default): Simple, no external dependencies
- PostgreSQL (optional): For multi-system access

Backend is auto-detected:
- If DATABASE_URL is set → PostgreSQL
- If WORKLOG_BACKEND=postgresql → PostgreSQL
- Otherwise → SQLite
"""

import os
from pathlib import Path
from urllib.parse import urlparse
from enum import Enum


class Backend(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


# Default SQLite path
DEFAULT_SQLITE_PATH = Path.home() / ".claude" / "worklog" / "worklog.db"


def get_backend() -> Backend:
    """Detect which backend to use.

    Priority:
    1. DATABASE_URL env var → PostgreSQL
    2. WORKLOG_BACKEND env var → specified backend
    3. PGHOST env var → PostgreSQL
    4. Default → SQLite
    """
    # Explicit DATABASE_URL means PostgreSQL
    if os.environ.get("DATABASE_URL"):
        return Backend.POSTGRESQL

    # Explicit backend selection
    backend_env = os.environ.get("WORKLOG_BACKEND", "").lower()
    if backend_env == "postgresql":
        return Backend.POSTGRESQL
    if backend_env == "sqlite":
        return Backend.SQLITE

    # PGHOST set suggests PostgreSQL intent
    if os.environ.get("PGHOST"):
        return Backend.POSTGRESQL

    # Default to SQLite
    return Backend.SQLITE


def get_sqlite_path() -> Path:
    """Get SQLite database path.

    Priority:
    1. WORKLOG_DB_PATH env var
    2. Default: ~/.claude/worklog/worklog.db
    """
    if db_path := os.environ.get("WORKLOG_DB_PATH"):
        return Path(db_path)
    return DEFAULT_SQLITE_PATH


def get_postgresql_params() -> dict:
    """Get PostgreSQL connection parameters for asyncpg.

    Priority:
    1. DATABASE_URL environment variable
    2. Individual PG* environment variables

    Raises ValueError if PostgreSQL is selected but not configured.
    """
    # Check for DATABASE_URL first
    if database_url := os.environ.get("DATABASE_URL"):
        return _parse_database_url(database_url)

    # Fall back to individual env vars
    host = os.environ.get("PGHOST")
    if not host:
        raise ValueError(
            "PostgreSQL selected but not configured.\n"
            "Options:\n"
            "  1. Set DATABASE_URL environment variable\n"
            "  2. Set PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD\n"
            "  3. Use SQLite instead (default, no config needed)"
        )

    password = os.environ.get("PGPASSWORD", "")
    if not password:
        raise ValueError(
            "PostgreSQL password not configured.\n"
            "Set PGPASSWORD or include password in DATABASE_URL."
        )

    return {
        "host": host,
        "port": int(os.environ.get("PGPORT", "5432")),
        "database": os.environ.get("PGDATABASE", "worklog"),
        "user": os.environ.get("PGUSER", "worklog"),
        "password": password,
    }


def _parse_database_url(url: str) -> dict:
    """Parse DATABASE_URL into connection parameters.

    Supports: postgresql://user:password@host:port/database
    """
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/") or "worklog",
        "user": parsed.username or "worklog",
        "password": parsed.password or "",
    }


def get_dsn() -> str:
    """Get PostgreSQL connection string (DSN)."""
    params = get_postgresql_params()
    return (
        f"postgresql://{params['user']}:{params['password']}"
        f"@{params['host']}:{params['port']}/{params['database']}"
    )


# Tables available in the database
TABLES = ["memories", "knowledge_base", "entries", "research", "agent_chat",
          "issues", "error_patterns"]

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
