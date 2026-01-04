"""Database abstraction layer for SQLite and PostgreSQL backends.

Provides a unified interface for both databases, handling:
- Connection management
- SQL dialect differences (placeholders, functions)
- Error handling
"""

import asyncio
import os
import sys
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional, Sequence

from worklog_mcp.config import Backend, get_backend, get_sqlite_path, get_postgresql_params


class DatabaseError(Exception):
    """Base database error."""
    pass


class UniqueViolationError(DatabaseError):
    """Raised when a unique constraint is violated."""
    pass


class DatabaseBackend(ABC):
    """Abstract base class for database backends."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the database."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    async def execute(self, query: str, *args: Any) -> str:
        """Execute a query without returning rows."""
        pass

    @abstractmethod
    async def fetchone(self, query: str, *args: Any) -> Optional[dict]:
        """Execute a query and return one row."""
        pass

    @abstractmethod
    async def fetchall(self, query: str, *args: Any) -> list[dict]:
        """Execute a query and return all rows."""
        pass

    @abstractmethod
    def placeholder(self, index: int) -> str:
        """Get the placeholder for parameterized queries (? or $N)."""
        pass

    @abstractmethod
    def interval_days(self, days: int) -> str:
        """Get SQL for 'N days ago' comparison."""
        pass

    @abstractmethod
    def ilike(self, column: str, placeholder: str) -> str:
        """Get SQL for case-insensitive LIKE."""
        pass

    @abstractmethod
    def array_contains(self, column: str, placeholder: str) -> str:
        """Get SQL for checking if column value is in array parameter."""
        pass


class SQLiteBackend(DatabaseBackend):
    """SQLite backend using aiosqlite."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn = None

    async def connect(self) -> None:
        import aiosqlite

        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row

        # Initialize schema if needed
        await self._init_schema()

    async def _init_schema(self) -> None:
        """Initialize database schema if tables don't exist."""
        schema_sql = """
        -- Core tables
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            summary TEXT,
            memory_type TEXT DEFAULT 'fact',
            importance INTEGER DEFAULT 5,
            status TEXT DEFAULT 'staging',
            tags TEXT,
            source_agent TEXT,
            system TEXT,
            access_count INTEGER DEFAULT 0,
            last_accessed TIMESTAMP,
            promoted_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT,
            source_agent TEXT,
            system TEXT DEFAULT 'shared',
            is_protocol INTEGER DEFAULT 0,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category, title)
        );

        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            agent TEXT DEFAULT 'claude',
            task_type TEXT NOT NULL,
            title TEXT NOT NULL,
            details TEXT,
            decision_rationale TEXT,
            outcome TEXT,
            tags TEXT,
            related_files TEXT
        );

        CREATE TABLE IF NOT EXISTS research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            key_points TEXT,
            relevance_score INTEGER DEFAULT 5,
            tags TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS agent_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_agent TEXT NOT NULL,
            to_agent TEXT NOT NULL,
            message TEXT NOT NULL,
            context TEXT,
            priority TEXT DEFAULT 'normal',
            status TEXT DEFAULT 'pending',
            parent_id INTEGER,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            resolved_at TIMESTAMP
        );

        -- NOTE: sot_issues removed in INFA-614

        CREATE TABLE IF NOT EXISTS error_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_signature TEXT,
            error_message TEXT,
            platform TEXT,
            language TEXT,
            root_cause TEXT,
            resolution TEXT,
            prevention_tip TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes for common queries
        CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
        CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
        CREATE INDEX IF NOT EXISTS idx_entries_timestamp ON entries(timestamp);
        CREATE INDEX IF NOT EXISTS idx_entries_agent ON entries(agent);
        CREATE INDEX IF NOT EXISTS idx_kb_category ON knowledge_base(category);
        CREATE INDEX IF NOT EXISTS idx_chat_to_agent ON agent_chat(to_agent);
        """
        await self._conn.executescript(schema_sql)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def execute(self, query: str, *args: Any) -> str:
        cursor = await self._conn.execute(query, args)
        await self._conn.commit()
        return f"OK {cursor.rowcount}"

    async def fetchone(self, query: str, *args: Any) -> Optional[dict]:
        cursor = await self._conn.execute(query, args)
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

    async def fetchall(self, query: str, *args: Any) -> list[dict]:
        cursor = await self._conn.execute(query, args)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    def placeholder(self, index: int) -> str:
        return "?"

    def interval_days(self, days: int) -> str:
        return f"datetime('now', '-{days} days')"

    def ilike(self, column: str, placeholder: str) -> str:
        # E1 fix: Use LOWER() for consistent case-insensitive matching
        # SQLite's default LIKE behavior varies with collation settings
        return f"LOWER({column}) LIKE LOWER({placeholder})"

    def array_contains(self, column: str, placeholder: str) -> str:
        # SQLite doesn't have array types, so we'll handle this differently
        # The caller needs to expand the array into multiple placeholders
        return f"{column} IN ({placeholder})"


class PostgreSQLBackend(DatabaseBackend):
    """PostgreSQL backend using asyncpg."""

    def __init__(self, params: dict):
        self.params = params
        self._pool = None

    async def connect(self) -> None:
        import asyncpg

        self._pool = await asyncpg.create_pool(
            host=self.params["host"],
            port=self.params["port"],
            database=self.params["database"],
            user=self.params["user"],
            password=self.params["password"],
            min_size=1,
            max_size=10,
            timeout=30,  # Connection timeout in seconds
            command_timeout=60,  # Query timeout in seconds
        )

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def execute(self, query: str, *args: Any) -> str:
        # P2 fix: Add timeout to prevent indefinite wait on pool exhaustion
        try:
            async with asyncio.timeout(5):  # 5 second timeout to acquire connection
                async with self._pool.acquire() as conn:
                    return await conn.execute(query, *args)
        except asyncio.TimeoutError:
            raise DatabaseError("Database connection pool exhausted, please retry")

    async def fetchone(self, query: str, *args: Any) -> Optional[dict]:
        try:
            async with asyncio.timeout(5):
                async with self._pool.acquire() as conn:
                    row = await conn.fetchrow(query, *args)
                    if row:
                        return dict(row)
                    return None
        except asyncio.TimeoutError:
            raise DatabaseError("Database connection pool exhausted, please retry")

    async def fetchall(self, query: str, *args: Any) -> list[dict]:
        try:
            async with asyncio.timeout(5):
                async with self._pool.acquire() as conn:
                    rows = await conn.fetch(query, *args)
                    return [dict(row) for row in rows]
        except asyncio.TimeoutError:
            raise DatabaseError("Database connection pool exhausted, please retry")

    def placeholder(self, index: int) -> str:
        return f"${index}"

    def interval_days(self, days: int) -> str:
        return f"NOW() - INTERVAL '{days} days'"

    def ilike(self, column: str, placeholder: str) -> str:
        return f"{column} ILIKE {placeholder}"

    def array_contains(self, column: str, placeholder: str) -> str:
        return f"{column} = ANY({placeholder}::text[])"


# Global database instance with lock for thread-safe initialization
_db: Optional[DatabaseBackend] = None
_db_lock = asyncio.Lock()


async def get_db() -> DatabaseBackend:
    """Get or initialize the database backend.

    Uses double-checked locking pattern to prevent race conditions
    during initialization while minimizing lock contention.
    """
    global _db

    # Fast path: already initialized
    if _db is not None:
        return _db

    # Slow path: acquire lock and initialize
    async with _db_lock:
        # Double-check after acquiring lock
        if _db is not None:
            return _db

        backend = get_backend()

        if backend == Backend.SQLITE:
            db_path = get_sqlite_path()
            _db = SQLiteBackend(db_path)
        else:
            try:
                params = get_postgresql_params()
                _db = PostgreSQLBackend(params)
            except ValueError as e:
                # Only fall back to SQLite if explicitly allowed
                allow_fallback = os.environ.get("WORKLOG_ALLOW_FALLBACK", "").lower() in ("1", "true", "yes")
                if allow_fallback:
                    print(f"WARNING: PostgreSQL not configured, falling back to SQLite: {e}", file=sys.stderr)
                    _db = SQLiteBackend(get_sqlite_path())
                else:
                    raise ValueError(
                        f"PostgreSQL configuration error: {e}\n"
                        "Set WORKLOG_ALLOW_FALLBACK=1 to allow SQLite fallback, "
                        "or fix PostgreSQL configuration."
                    )

        await _db.connect()

    return _db


async def close_db() -> None:
    """Close the database connection.

    M5 fix: Uses lock to prevent race condition with get_db().
    """
    global _db
    async with _db_lock:
        if _db:
            await _db.close()
            _db = None


def get_unique_violation_error():
    """Get the appropriate unique violation error class for the current backend."""
    backend = get_backend()
    if backend == Backend.POSTGRESQL:
        try:
            import asyncpg
            return asyncpg.UniqueViolationError
        except ImportError:
            pass
    # SQLite or fallback
    import sqlite3
    return sqlite3.IntegrityError
