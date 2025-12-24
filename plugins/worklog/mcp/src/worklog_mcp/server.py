"""Worklog MCP Server - Structured access to shared knowledge base.

Provides tools for querying and storing data in the worklog database.
Supports both SQLite (default) and PostgreSQL (optional) backends.

Backend selection:
- SQLite: Default, no configuration needed
- PostgreSQL: Set DATABASE_URL or PGHOST environment variables
"""

import re
from contextlib import asynccontextmanager
from typing import Optional
from fastmcp import FastMCP

from worklog_mcp.config import (
    get_backend,
    Backend,
    TABLES,
    MEMORY_TYPES,
    MEMORY_STATUSES,
    TASK_TYPES,
    KB_CATEGORIES,
)
from worklog_mcp.database import get_db, close_db, UniqueViolationError


# Column whitelist per table - prevents SQL injection via column names
TABLE_COLUMNS = {
    "memories": {
        "id", "key", "content", "summary", "memory_type", "importance",
        "status", "tags", "source_agent", "system", "access_count",
        "last_accessed", "promoted_at", "created_at"
    },
    "knowledge_base": {
        "id", "category", "title", "content", "tags", "source_agent",
        "system", "is_protocol", "created_at", "updated_at"
    },
    "entries": {
        "id", "timestamp", "agent", "task_type", "title", "details",
        "decision_rationale", "outcome", "tags", "related_files"
    },
    "research": {
        "id", "source_type", "title", "summary", "key_points",
        "relevance_score", "tags", "status", "created_at"
    },
    "agent_chat": {
        "id", "from_agent", "to_agent", "message", "context", "priority",
        "status", "parent_id", "response", "created_at", "read_at", "resolved_at"
    },
    "issues": {
        "id", "project", "title", "description", "status", "tags",
        "source_agent", "created_at"
    },
    "error_patterns": {
        "id", "error_signature", "error_message", "platform", "language",
        "root_cause", "resolution", "prevention_tip", "tags", "created_at"
    },
}


def _validate_columns(columns: str, table: str) -> tuple[bool, str]:
    """Validate column names against whitelist.

    Args:
        columns: Comma-separated column names or "*"
        table: Table name to validate against

    Returns:
        Tuple of (is_valid, error_message_or_sanitized_columns)
    """
    if columns.strip() == "*":
        return True, "*"

    allowed = TABLE_COLUMNS.get(table, set())
    requested = [c.strip().lower() for c in columns.split(",")]

    invalid = [c for c in requested if c not in allowed]
    if invalid:
        return False, f"Invalid columns: {invalid}. Allowed: {sorted(allowed)}"

    return True, ", ".join(requested)


def _validate_order_by(order_by: str, table: str) -> tuple[bool, str]:
    """Validate ORDER BY clause against whitelist.

    Args:
        order_by: Column name with optional ASC/DESC
        table: Table name to validate against

    Returns:
        Tuple of (is_valid, error_message_or_sanitized_order_by)
    """
    if not order_by:
        return True, ""

    # Parse "column_name DESC" or "column_name ASC" or just "column_name"
    parts = order_by.strip().split()
    if len(parts) > 2:
        return False, "Invalid order_by format. Use 'column' or 'column ASC/DESC'"

    column = parts[0].lower()
    direction = parts[1].upper() if len(parts) == 2 else "ASC"

    if direction not in ("ASC", "DESC"):
        return False, f"Invalid sort direction: {direction}. Use ASC or DESC"

    allowed = TABLE_COLUMNS.get(table, set())
    if column not in allowed:
        return False, f"Invalid order_by column: {column}. Allowed: {sorted(allowed)}"

    return True, f"{column} {direction}"


@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for connection pool cleanup."""
    yield
    await close_db()


mcp = FastMCP(
    "worklog-mcp",
    instructions="MCP server for structured access to the worklog knowledge base. "
    "Use query_table for flexible queries, search_knowledge for full-text search, "
    "recall_context at task start to load relevant context, store_memory for facts, "
    "and log_entry for work tracking. Supports SQLite (default) and PostgreSQL.",
    lifespan=lifespan,
)


def _build_placeholders(count: int, backend: Backend) -> list[str]:
    """Build list of placeholders for the given backend."""
    if backend == Backend.SQLITE:
        return ["?" for _ in range(count)]
    else:
        return [f"${i+1}" for i in range(count)]


# =============================================================================
# QUERY TOOLS
# =============================================================================


@mcp.tool()
async def query_table(
    table: str,
    columns: str = "*",
    filter_column: Optional[str] = None,
    filter_op: str = "=",
    filter_value: Optional[str] = None,
    order_by: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """Query any table in the worklog database with filtering and pagination.

    Args:
        table: Table name (memories, knowledge_base, entries, research, agent_chat, issues, error_patterns)
        columns: Comma-separated column names or * for all
        filter_column: Column to filter on (validated against whitelist)
        filter_op: Filter operator (=, !=, >, <, >=, <=, LIKE, ILIKE)
        filter_value: Value to filter by (safely parameterized)
        order_by: Column to order by with direction, e.g. "created_at DESC"
        limit: Maximum rows to return (default 20, max 100)
        offset: Number of rows to skip for pagination

    Returns:
        dict with 'rows' list and 'count' of total matching rows
    """
    if table not in TABLES:
        return {"error": f"Invalid table. Must be one of: {TABLES}"}

    # Validate columns
    valid, result = _validate_columns(columns, table)
    if not valid:
        return {"error": result}
    safe_columns = result

    # Validate order_by
    valid, result = _validate_order_by(order_by or "", table)
    if not valid:
        return {"error": result}
    safe_order_by = result

    # Validate filter_column if provided
    allowed_ops = {"=", "!=", ">", "<", ">=", "<=", "LIKE", "ILIKE"}
    if filter_column:
        allowed = TABLE_COLUMNS.get(table, set())
        if filter_column.lower() not in allowed:
            return {"error": f"Invalid filter_column: {filter_column}. Allowed: {sorted(allowed)}"}
        if filter_op.upper() not in allowed_ops:
            return {"error": f"Invalid filter_op: {filter_op}. Allowed: {sorted(allowed_ops)}"}

    limit = min(limit, 100)
    db = await get_db()
    backend = get_backend()

    # Build parameterized query
    query = f"SELECT {safe_columns} FROM {table}"
    count_query = f"SELECT COUNT(*) as total FROM {table}"
    params = []

    if filter_column and filter_value is not None:
        p1 = db.placeholder(1)
        op = filter_op.upper()
        col = filter_column.lower()

        if op == "ILIKE":
            where_clause = db.ilike(col, p1)
        else:
            where_clause = f"{col} {op} {p1}"

        query += f" WHERE {where_clause}"
        count_query += f" WHERE {where_clause}"
        params.append(filter_value)

    if safe_order_by:
        query += f" ORDER BY {safe_order_by}"

    query += f" LIMIT {limit} OFFSET {offset}"

    # Get total count
    count_row = await db.fetchone(count_query, *params) if params else await db.fetchone(count_query)
    total = count_row["total"] if count_row else 0

    # Get rows
    rows = await db.fetchall(query, *params) if params else await db.fetchall(query)

    return {
        "rows": rows,
        "count": len(rows),
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@mcp.tool()
async def search_knowledge(
    query: str,
    tables: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """Full-text search across knowledge base tables.

    Searches title, content, summary, and tags fields for the query string.

    Args:
        query: Search term to find
        tables: Comma-separated table names to search (default: all)
        limit: Maximum results per table (default 10)

    Returns:
        dict with results grouped by table
    """
    search_tables = tables.split(",") if tables else TABLES
    search_tables = [t.strip() for t in search_tables if t.strip() in TABLES]

    if not search_tables:
        return {"error": f"No valid tables. Options: {TABLES}"}

    results = {}
    search_term = f"%{query}%"
    db = await get_db()
    backend = get_backend()

    for table in search_tables:
        p1 = db.placeholder(1)
        p2 = db.placeholder(2)

        if table == "memories":
            like1 = db.ilike("content", p1)
            like2 = db.ilike("summary", p1)
            like3 = db.ilike("key", p1)
            like4 = db.ilike("tags", p1)
            sql = f"""
                SELECT id, key, summary, memory_type, importance, tags, created_at
                FROM memories
                WHERE {like1} OR {like2} OR {like3} OR {like4}
                ORDER BY importance DESC, created_at DESC
                LIMIT {p2}
            """
        elif table == "knowledge_base":
            like1 = db.ilike("title", p1)
            like2 = db.ilike("content", p1)
            like3 = db.ilike("tags", p1)
            like4 = db.ilike("category", p1)
            sql = f"""
                SELECT id, category, title, tags, created_at, updated_at
                FROM knowledge_base
                WHERE {like1} OR {like2} OR {like3} OR {like4}
                ORDER BY updated_at DESC
                LIMIT {p2}
            """
        elif table == "entries":
            like1 = db.ilike("title", p1)
            like2 = db.ilike("details", p1)
            like3 = db.ilike("outcome", p1)
            like4 = db.ilike("tags", p1)
            sql = f"""
                SELECT id, timestamp, agent, task_type, title, outcome, tags
                FROM entries
                WHERE {like1} OR {like2} OR {like3} OR {like4}
                ORDER BY timestamp DESC
                LIMIT {p2}
            """
        elif table == "research":
            like1 = db.ilike("title", p1)
            like2 = db.ilike("summary", p1)
            like3 = db.ilike("key_points", p1)
            like4 = db.ilike("tags", p1)
            sql = f"""
                SELECT id, source_type, title, summary, relevance_score, tags, status
                FROM research
                WHERE {like1} OR {like2} OR {like3} OR {like4}
                ORDER BY relevance_score DESC, created_at DESC
                LIMIT {p2}
            """
        else:
            continue

        # SQLite uses positional placeholders, so we need to pass search_term 4 times
        # (once for each LIKE clause) plus limit
        if backend == Backend.SQLITE:
            rows = await db.fetchall(sql, search_term, search_term, search_term, search_term, limit)
        else:
            # PostgreSQL can reuse $1 placeholder
            rows = await db.fetchall(sql, search_term, limit)
        results[table] = rows

    return {
        "query": query,
        "results": results,
        "tables_searched": search_tables,
    }


@mcp.tool()
async def recall_context(
    topic: str,
    memory_types: Optional[str] = None,
    min_importance: int = 5,
    include_recent: bool = True,
    limit: int = 15,
) -> dict:
    """Smart retrieval of context for agent work sessions.

    Combines recent context memories with relevant facts and knowledge.
    Designed to be called at the start of tasks to load relevant context.

    Args:
        topic: Topic or keywords to retrieve context for
        memory_types: Comma-separated types (fact, entity, preference, context)
        min_importance: Minimum importance score (1-10, default 5)
        include_recent: Include recent context entries regardless of topic match
        limit: Maximum results to return

    Returns:
        dict with categorized context (memories, knowledge, recent_work)
    """
    types = memory_types.split(",") if memory_types else ["fact", "context"]
    types = [t.strip() for t in types if t.strip() in MEMORY_TYPES]

    search_term = f"%{topic}%"
    results = {
        "topic": topic,
        "memories": [],
        "knowledge": [],
        "recent_work": [],
    }

    db = await get_db()
    backend = get_backend()

    # Get relevant memories
    p1, p2, p3, p4 = [db.placeholder(i) for i in range(1, 5)]

    if backend == Backend.SQLITE:
        # SQLite: Use IN clause with expanded values
        type_placeholders = ", ".join(["?" for _ in types])
        like1 = db.ilike("content", "?")
        like2 = db.ilike("summary", "?")
        like3 = db.ilike("key", "?")
        like4 = db.ilike("tags", "?")
        memory_sql = f"""
            SELECT id, key, content, summary, memory_type, importance, tags, created_at
            FROM memories
            WHERE memory_type IN ({type_placeholders})
              AND importance >= ?
              AND status != 'archived'
              AND ({like1} OR {like2} OR {like3} OR {like4})
            ORDER BY importance DESC, last_accessed DESC
            LIMIT ?
        """
        # Args: types..., min_importance, search_term x4, limit
        args = (*types, min_importance, search_term, search_term, search_term, search_term, limit)
        rows = await db.fetchall(memory_sql, *args)
    else:
        # PostgreSQL: Use ANY for array
        like1 = db.ilike("content", "$3")
        like2 = db.ilike("summary", "$3")
        like3 = db.ilike("key", "$3")
        like4 = db.ilike("tags", "$3")
        memory_sql = f"""
            SELECT id, key, content, summary, memory_type, importance, tags, created_at
            FROM memories
            WHERE memory_type = ANY($1::text[])
              AND importance >= $2
              AND status != 'archived'
              AND ({like1} OR {like2} OR {like3} OR {like4})
            ORDER BY importance DESC, last_accessed DESC
            LIMIT $4
        """
        rows = await db.fetchall(memory_sql, types, min_importance, search_term, limit)

    results["memories"] = rows

    # Get relevant knowledge base entries
    p1, p2 = db.placeholder(1), db.placeholder(2)
    like1 = db.ilike("title", p1)
    like2 = db.ilike("content", p1)
    like3 = db.ilike("tags", p1)
    kb_sql = f"""
        SELECT id, category, title, content, tags, updated_at
        FROM knowledge_base
        WHERE {like1} OR {like2} OR {like3}
        ORDER BY updated_at DESC
        LIMIT {p2}
    """
    rows = await db.fetchall(kb_sql, search_term, limit // 2)
    results["knowledge"] = rows

    # Get recent work entries if requested
    if include_recent:
        interval = db.interval_days(7)
        like1 = db.ilike("title", p1)
        like2 = db.ilike("tags", p1)
        recent_sql = f"""
            SELECT id, timestamp, agent, task_type, title, outcome, tags
            FROM entries
            WHERE timestamp > {interval}
              AND ({like1} OR {like2})
            ORDER BY timestamp DESC
            LIMIT {p2}
        """
        rows = await db.fetchall(recent_sql, search_term, limit // 2)
        results["recent_work"] = rows

    return results


@mcp.tool()
async def get_knowledge_entry(id: int) -> dict:
    """Get a full knowledge base entry by ID.

    Args:
        id: The knowledge base entry ID

    Returns:
        Full entry with all fields
    """
    db = await get_db()
    p1 = db.placeholder(1)
    row = await db.fetchone(f"SELECT * FROM knowledge_base WHERE id = {p1}", id)
    if row:
        return {"entry": row}
    return {"error": f"No knowledge base entry with id {id}"}


@mcp.tool()
async def get_memory(key: str) -> dict:
    """Get a memory by its unique key.

    Args:
        key: The memory key (e.g., 'ctx_jarvis_20251215_ssh-setup')

    Returns:
        Full memory with all fields
    """
    db = await get_db()
    p1 = db.placeholder(1)

    # Update access count and timestamp
    await db.execute(
        f"""UPDATE memories SET
           access_count = access_count + 1,
           last_accessed = CURRENT_TIMESTAMP
           WHERE key = {p1}""",
        key,
    )

    row = await db.fetchone(f"SELECT * FROM memories WHERE key = {p1}", key)
    if row:
        return {"memory": row}
    return {"error": f"No memory with key '{key}'"}


# =============================================================================
# STORAGE TOOLS
# =============================================================================


@mcp.tool()
async def store_memory(
    key: str,
    content: str,
    summary: Optional[str] = None,
    memory_type: str = "fact",
    importance: int = 5,
    tags: Optional[str] = None,
    source_agent: Optional[str] = None,
    system: Optional[str] = None,
) -> dict:
    """Store a new memory in the memories table.

    Args:
        key: Unique key for the memory (e.g., 'ctx_agent_date_slug')
        content: Full content of the memory
        summary: Brief summary (optional, for quick scanning)
        memory_type: Type of memory (fact, entity, preference, context)
        importance: Importance score 1-10 (default 5)
        tags: Comma-separated tags for categorization
        source_agent: Agent that created this memory
        system: System where memory was created

    Returns:
        dict with success status and memory id
    """
    if memory_type not in MEMORY_TYPES:
        return {"error": f"Invalid memory_type. Must be one of: {MEMORY_TYPES}"}

    importance = max(1, min(10, importance))
    db = await get_db()
    backend = get_backend()

    try:
        if backend == Backend.SQLITE:
            sql = """INSERT INTO memories
                   (key, content, summary, memory_type, importance, tags, source_agent, system)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            await db.execute(sql, key, content, summary, memory_type, importance, tags, source_agent, system)
            # Get last inserted ID
            row = await db.fetchone("SELECT last_insert_rowid() as id")
            return {"success": True, "id": row["id"], "key": key}
        else:
            sql = """INSERT INTO memories
                   (key, content, summary, memory_type, importance, tags, source_agent, system)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                   RETURNING id"""
            row = await db.fetchone(sql, key, content, summary, memory_type, importance, tags, source_agent, system)
            return {"success": True, "id": row["id"], "key": key}
    except Exception as e:
        if "UNIQUE constraint" in str(e) or "unique" in str(e).lower():
            return {"error": f"Memory with key '{key}' already exists. Use update_memory instead."}
        raise


@mcp.tool()
async def update_memory(
    key: str,
    content: Optional[str] = None,
    summary: Optional[str] = None,
    importance: Optional[int] = None,
    tags: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    """Update an existing memory by key.

    Args:
        key: The memory key to update
        content: New content (optional)
        summary: New summary (optional)
        importance: New importance 1-10 (optional)
        tags: New tags (optional)
        status: New status (staging, promoted, archived) (optional)

    Returns:
        dict with success status
    """
    if status and status not in MEMORY_STATUSES:
        return {"error": f"Invalid status. Must be one of: {MEMORY_STATUSES}"}

    db = await get_db()
    backend = get_backend()

    updates = []
    params = []

    if backend == Backend.SQLITE:
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if summary is not None:
            updates.append("summary = ?")
            params.append(summary)
        if importance is not None:
            updates.append("importance = ?")
            params.append(max(1, min(10, importance)))
        if tags is not None:
            updates.append("tags = ?")
            params.append(tags)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
            if status == "promoted":
                updates.append("promoted_at = CURRENT_TIMESTAMP")

        if not updates:
            return {"error": "No fields to update"}

        params.append(key)
        sql = f"UPDATE memories SET {', '.join(updates)} WHERE key = ?"
    else:
        param_idx = 1
        if content is not None:
            updates.append(f"content = ${param_idx}")
            params.append(content)
            param_idx += 1
        if summary is not None:
            updates.append(f"summary = ${param_idx}")
            params.append(summary)
            param_idx += 1
        if importance is not None:
            updates.append(f"importance = ${param_idx}")
            params.append(max(1, min(10, importance)))
            param_idx += 1
        if tags is not None:
            updates.append(f"tags = ${param_idx}")
            params.append(tags)
            param_idx += 1
        if status is not None:
            updates.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1
            if status == "promoted":
                updates.append("promoted_at = CURRENT_TIMESTAMP")

        if not updates:
            return {"error": "No fields to update"}

        params.append(key)
        sql = f"UPDATE memories SET {', '.join(updates)} WHERE key = ${param_idx}"

    result = await db.execute(sql, *params)

    # Check if any rows were updated
    if "0" in result or result.endswith(" 0"):
        return {"error": f"No memory found with key '{key}'"}

    return {"success": True, "key": key, "updated_fields": len([u for u in updates if "=" in u])}


@mcp.tool()
async def log_entry(
    title: str,
    task_type: str,
    details: Optional[str] = None,
    decision_rationale: Optional[str] = None,
    outcome: Optional[str] = None,
    tags: Optional[str] = None,
    related_files: Optional[str] = None,
    agent: str = "claude",
) -> dict:
    """Log a work entry to the entries table.

    Args:
        title: Brief title of the work done
        task_type: Type of task (configuration, deployment, debugging, etc.)
        details: Detailed description of what was done
        decision_rationale: Why this approach was chosen
        outcome: Result or outcome of the work
        tags: Comma-separated tags
        related_files: Comma-separated list of related file paths
        agent: Agent name (default: claude)

    Returns:
        dict with success status and entry id
    """
    if task_type not in TASK_TYPES:
        return {"error": f"Invalid task_type. Must be one of: {TASK_TYPES}"}

    db = await get_db()
    backend = get_backend()

    if backend == Backend.SQLITE:
        sql = """INSERT INTO entries
               (agent, task_type, title, details, decision_rationale, outcome, tags, related_files)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        await db.execute(sql, agent, task_type, title, details, decision_rationale, outcome, tags, related_files)
        row = await db.fetchone("SELECT last_insert_rowid() as id")
        return {"success": True, "id": row["id"], "title": title}
    else:
        sql = """INSERT INTO entries
               (agent, task_type, title, details, decision_rationale, outcome, tags, related_files)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
               RETURNING id"""
        row = await db.fetchone(sql, agent, task_type, title, details, decision_rationale, outcome, tags, related_files)
        return {"success": True, "id": row["id"], "title": title}


@mcp.tool()
async def store_knowledge(
    category: str,
    title: str,
    content: str,
    tags: Optional[str] = None,
    source_agent: Optional[str] = None,
    system: str = "shared",
    is_protocol: bool = False,
) -> dict:
    """Store a new knowledge base entry.

    Args:
        category: Category (system-administration, development, infrastructure, etc.)
        title: Title of the knowledge entry
        content: Full content with examples, commands, notes
        tags: Comma-separated tags
        source_agent: Agent that created this entry
        system: System context (default: shared)
        is_protocol: Whether this is a protocol document

    Returns:
        dict with success status and entry id
    """
    if category not in KB_CATEGORIES:
        return {"error": f"Invalid category. Must be one of: {KB_CATEGORIES}"}

    db = await get_db()
    backend = get_backend()

    try:
        if backend == Backend.SQLITE:
            sql = """INSERT INTO knowledge_base
                   (category, title, content, tags, source_agent, system, is_protocol)
                   VALUES (?, ?, ?, ?, ?, ?, ?)"""
            await db.execute(sql, category, title, content, tags, source_agent, system, 1 if is_protocol else 0)
            row = await db.fetchone("SELECT last_insert_rowid() as id")
            return {"success": True, "id": row["id"], "title": title}
        else:
            sql = """INSERT INTO knowledge_base
                   (category, title, content, tags, source_agent, system, is_protocol)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)
                   RETURNING id"""
            row = await db.fetchone(sql, category, title, content, tags, source_agent, system, is_protocol)
            return {"success": True, "id": row["id"], "title": title}
    except Exception as e:
        if "UNIQUE constraint" in str(e) or "unique" in str(e).lower():
            return {"error": f"Knowledge entry with category '{category}' and title '{title}' already exists."}
        raise


# =============================================================================
# UTILITY TOOLS
# =============================================================================


@mcp.tool()
async def list_tables() -> dict:
    """List all available tables and their row counts.

    Returns:
        dict with table names and counts
    """
    db = await get_db()
    tables = {}

    for table in TABLES:
        row = await db.fetchone(f"SELECT COUNT(*) as count FROM {table}")
        tables[table] = row["count"] if row else 0

    return {"tables": tables, "backend": get_backend().value}


@mcp.tool()
async def get_recent_entries(
    agent: Optional[str] = None,
    days: int = 7,
    limit: int = 20,
) -> dict:
    """Get recent work entries, optionally filtered by agent.

    Args:
        agent: Filter by agent name (optional)
        days: Number of days to look back (default 7)
        limit: Maximum entries to return (default 20)

    Returns:
        dict with recent entries
    """
    db = await get_db()
    backend = get_backend()
    interval = db.interval_days(days)

    if agent:
        p1, p2 = db.placeholder(1), db.placeholder(2)
        sql = f"""
            SELECT id, timestamp, agent, task_type, title, outcome, tags
            FROM entries
            WHERE agent = {p1} AND timestamp > {interval}
            ORDER BY timestamp DESC
            LIMIT {p2}
        """
        rows = await db.fetchall(sql, agent, limit)
    else:
        p1 = db.placeholder(1)
        sql = f"""
            SELECT id, timestamp, agent, task_type, title, outcome, tags
            FROM entries
            WHERE timestamp > {interval}
            ORDER BY timestamp DESC
            LIMIT {p1}
        """
        rows = await db.fetchall(sql, limit)

    return {
        "entries": rows,
        "count": len(rows),
        "days": days,
    }


# =============================================================================
# AGENT CHAT TOOLS
# =============================================================================


def _detect_agent() -> str:
    """Auto-detect agent name from hostname."""
    import os
    hostname = os.uname().nodename.lower()
    if "atlas" in hostname:
        return "alfred"
    elif "m4" in hostname or "mac" in hostname:
        return "macadmin"
    elif "ubuntu" in hostname or "mini" in hostname:
        return "jarvis"
    return "unknown"


@mcp.tool()
async def send_message(
    to_agent: str,
    message: str,
    from_agent: Optional[str] = None,
    context: Optional[str] = None,
    priority: str = "normal",
) -> dict:
    """Send a message to another agent for quick help mid-task.

    Args:
        to_agent: Target agent (alfred, macadmin, jarvis, or 'all' for broadcast)
        message: The message/question to send
        from_agent: Sender agent name (auto-detected from hostname if not provided)
        context: Optional context about current task
        priority: Message priority (low, normal, urgent)

    Returns:
        dict with message_id and status
    """
    from worklog_mcp.config import AGENTS, CHAT_PRIORITIES

    if to_agent not in AGENTS:
        return {"error": f"Invalid agent. Must be one of: {AGENTS}"}

    if priority not in CHAT_PRIORITIES:
        return {"error": f"Invalid priority. Must be one of: {CHAT_PRIORITIES}"}

    if not from_agent:
        from_agent = _detect_agent()

    db = await get_db()
    backend = get_backend()

    if backend == Backend.SQLITE:
        sql = """INSERT INTO agent_chat
               (from_agent, to_agent, message, context, priority)
               VALUES (?, ?, ?, ?, ?)"""
        await db.execute(sql, from_agent, to_agent, message, context, priority)
        row = await db.fetchone("SELECT last_insert_rowid() as id")
        message_id = row["id"]
    else:
        sql = """INSERT INTO agent_chat
               (from_agent, to_agent, message, context, priority)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING id"""
        row = await db.fetchone(sql, from_agent, to_agent, message, context, priority)
        message_id = row["id"]

    return {
        "message_id": message_id,
        "status": "sent",
        "to": to_agent,
        "from": from_agent,
        "priority": priority,
    }


@mcp.tool()
async def check_messages(
    agent: Optional[str] = None,
    include_read: bool = False,
) -> dict:
    """Check for incoming messages. Call this periodically when expecting replies.

    Args:
        agent: Your agent name (auto-detected if not provided)
        include_read: Include already-read messages (default False)

    Returns:
        dict with pending messages
    """
    if not agent:
        agent = _detect_agent()

    db = await get_db()
    backend = get_backend()

    statuses = ["pending", "read"] if include_read else ["pending"]

    if backend == Backend.SQLITE:
        status_placeholders = ", ".join(["?" for _ in statuses])
        sql = f"""
            SELECT id, from_agent, to_agent, message, context, priority,
                   status, parent_id, response, created_at, read_at
            FROM agent_chat
            WHERE (to_agent = ? OR to_agent = 'all')
              AND from_agent != ?
              AND status IN ({status_placeholders})
            ORDER BY
                CASE priority WHEN 'urgent' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END,
                created_at DESC
        """
        rows = await db.fetchall(sql, agent, agent, *statuses)
    else:
        sql = """
            SELECT id, from_agent, to_agent, message, context, priority,
                   status, parent_id, response, created_at, read_at
            FROM agent_chat
            WHERE (to_agent = $1 OR to_agent = 'all')
              AND from_agent != $1
              AND status = ANY($2::text[])
            ORDER BY
                CASE priority WHEN 'urgent' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END,
                created_at DESC
        """
        rows = await db.fetchall(sql, agent, statuses)

    messages = rows

    # Mark pending messages as read
    if messages:
        pending_ids = [m["id"] for m in messages if m["status"] == "pending"]
        if pending_ids:
            if backend == Backend.SQLITE:
                id_placeholders = ", ".join(["?" for _ in pending_ids])
                await db.execute(
                    f"""UPDATE agent_chat
                       SET status = 'read', read_at = CURRENT_TIMESTAMP
                       WHERE id IN ({id_placeholders})""",
                    *pending_ids,
                )
            else:
                await db.execute(
                    """UPDATE agent_chat
                       SET status = 'read', read_at = CURRENT_TIMESTAMP
                       WHERE id = ANY($1::int[])""",
                    pending_ids,
                )

    return {
        "messages": messages,
        "count": len(messages),
        "agent": agent,
    }


@mcp.tool()
async def reply_message(
    message_id: int,
    response: str,
    from_agent: Optional[str] = None,
    resolve: bool = True,
) -> dict:
    """Reply to a message from another agent.

    Args:
        message_id: ID of the message to reply to
        response: Your response text
        from_agent: Your agent name (auto-detected if not provided)
        resolve: Mark the conversation as resolved (default True)

    Returns:
        dict with reply status
    """
    if not from_agent:
        from_agent = _detect_agent()

    db = await get_db()
    backend = get_backend()
    p1 = db.placeholder(1)

    # Get the original message
    original = await db.fetchone(f"SELECT * FROM agent_chat WHERE id = {p1}", message_id)

    if not original:
        return {"error": f"Message {message_id} not found"}

    new_status = "resolved" if resolve else "replied"

    # Update original message with response
    if backend == Backend.SQLITE:
        await db.execute(
            """UPDATE agent_chat
               SET response = ?, status = ?, resolved_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            response, new_status, message_id,
        )
    else:
        await db.execute(
            """UPDATE agent_chat
               SET response = $1, status = $2, resolved_at = CURRENT_TIMESTAMP
               WHERE id = $3""",
            response, new_status, message_id,
        )

    return {
        "status": "replied",
        "message_id": message_id,
        "original_from": original["from_agent"],
        "resolved": resolve,
    }


@mcp.tool()
async def check_replies(
    agent: Optional[str] = None,
) -> dict:
    """Check for replies to messages you sent.

    Args:
        agent: Your agent name (auto-detected if not provided)

    Returns:
        dict with replied/resolved messages you sent
    """
    if not agent:
        agent = _detect_agent()

    db = await get_db()
    p1 = db.placeholder(1)

    sql = f"""
        SELECT id, from_agent, to_agent, message, context, priority,
               status, response, created_at, resolved_at
        FROM agent_chat
        WHERE from_agent = {p1}
          AND status IN ('replied', 'resolved')
          AND response IS NOT NULL
        ORDER BY resolved_at DESC
        LIMIT 20
    """

    rows = await db.fetchall(sql, agent)
    return {
        "replies": rows,
        "count": len(rows),
        "agent": agent,
    }


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
