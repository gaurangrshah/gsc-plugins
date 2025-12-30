"""Worklog MCP Server - Structured access to shared knowledge base.

Provides tools for querying and storing data in the worklog database.
Supports both SQLite (default) and PostgreSQL (optional) backends.

Backend selection:
- SQLite: Default, no configuration needed
- PostgreSQL: Set DATABASE_URL or PGHOST environment variables
"""

import json
import re
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
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
    RELATIONSHIP_TYPES,
    ENTRY_TABLES,
    CURATION_OPERATIONS,
)
from worklog_mcp.database import get_db, close_db, UniqueViolationError


# Column whitelist per table - prevents SQL injection via column names
# Using frozenset for immutability (security: prevents runtime modification)
TABLE_COLUMNS: dict[str, frozenset[str]] = {
    "memories": frozenset({
        "id", "key", "content", "summary", "memory_type", "importance",
        "status", "tags", "source_agent", "system", "access_count",
        "last_accessed", "promoted_at", "created_at"
    }),
    "knowledge_base": frozenset({
        "id", "category", "title", "content", "tags", "source_agent",
        "system", "is_protocol", "created_at", "updated_at", "source_url"
    }),
    "entries": frozenset({
        "id", "timestamp", "agent", "task_type", "title", "details",
        "decision_rationale", "outcome", "tags", "related_files"
    }),
    "research": frozenset({
        "id", "source_type", "title", "summary", "key_points",
        "relevance_score", "tags", "status", "created_at"
    }),
    "agent_chat": frozenset({
        "id", "from_agent", "to_agent", "message", "context", "priority",
        "status", "parent_id", "response", "created_at", "read_at", "resolved_at"
    }),
    "issues": frozenset({
        "id", "project", "title", "description", "status", "tags",
        "source_agent", "created_at"
    }),
    "error_patterns": frozenset({
        "id", "error_signature", "error_message", "platform", "language",
        "root_cause", "resolution", "prevention_tip", "tags", "created_at"
    }),
    # Curation tables (INFA-291)
    "tag_taxonomy": frozenset({
        "id", "canonical_tag", "aliases", "category", "description",
        "usage_count", "created_at", "updated_at"
    }),
    "relationships": frozenset({
        "id", "source_table", "source_id", "target_table", "target_id",
        "relationship_type", "confidence", "bidirectional", "created_by", "created_at"
    }),
    "topic_index": frozenset({
        "id", "topic_name", "summary", "full_summary", "key_terms",
        "content_size", "entry_count", "last_curated", "created_at", "updated_at"
    }),
    "topic_entries": frozenset({
        "id", "topic_id", "entry_table", "entry_id", "relevance_score", "added_at"
    }),
    "duplicate_candidates": frozenset({
        "id", "entry1_table", "entry1_id", "entry2_table", "entry2_id",
        "similarity_score", "detection_method", "status", "reviewed_by",
        "reviewed_at", "merge_target_id", "created_at"
    }),
    "promotion_history": frozenset({
        "id", "memory_id", "from_status", "to_status", "reason",
        "score_snapshot", "promoted_by", "created_at"
    }),
    "curation_history": frozenset({
        "id", "run_at", "operation", "agent", "stats",
        "duration_seconds", "success", "error_message"
    }),
}

# Valid table names (immutable for security)
VALID_TABLES: frozenset[str] = frozenset(TABLE_COLUMNS.keys())

# Input length limits
MAX_SEARCH_QUERY_LENGTH = 500
MAX_FILTER_VALUE_LENGTH = 1000
MAX_COLUMN_SPEC_LENGTH = 500


def _escape_search_wildcards(term: str) -> str:
    """Escape SQL wildcards in search terms to prevent wildcard injection.

    Args:
        term: Raw search term from user

    Returns:
        Escaped term safe for LIKE queries
    """
    # Escape backslash first, then wildcards
    term = term.replace("\\", "\\\\")
    term = term.replace("%", "\\%")
    term = term.replace("_", "\\_")
    return f"%{term}%"


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
        offset: Number of rows to skip for pagination (must be >= 0)

    Returns:
        dict with 'rows' list and 'count' of total matching rows
    """
    # Validate table name against immutable whitelist
    if table not in VALID_TABLES:
        return {"error": "Invalid table name"}

    # Validate bounds (M1 fix: prevent negative values)
    if limit < 0 or limit > 100:
        limit = min(max(limit, 1), 100)
    if offset < 0:
        offset = 0

    # Validate input lengths (M4 fix: prevent resource exhaustion)
    if len(columns) > MAX_COLUMN_SPEC_LENGTH:
        return {"error": "Column specification too long"}
    if filter_value and len(filter_value) > MAX_FILTER_VALUE_LENGTH:
        return {"error": "Filter value too long"}

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
    allowed_ops = frozenset({"=", "!=", ">", "<", ">=", "<=", "LIKE", "ILIKE"})
    if filter_column:
        allowed = TABLE_COLUMNS.get(table, frozenset())
        if filter_column.lower() not in allowed:
            return {"error": "Invalid filter column"}
        if filter_op.upper() not in allowed_ops:
            return {"error": "Invalid filter operator"}

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
        limit: Maximum results per table (default 10, max 100)

    Returns:
        dict with results grouped by table
    """
    # Validate input length
    if len(query) > MAX_SEARCH_QUERY_LENGTH:
        return {"error": "Search query too long"}

    # Validate and bound limit
    limit = min(max(limit, 1), 100)

    search_tables = tables.split(",") if tables else list(VALID_TABLES)
    search_tables = [t.strip() for t in search_tables if t.strip() in VALID_TABLES]

    if not search_tables:
        return {"error": "No valid tables specified"}

    results = {}
    # E2 fix: Escape SQL wildcards to prevent wildcard injection
    search_term = _escape_search_wildcards(query)
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
        limit: Maximum results to return (max 100)

    Returns:
        dict with categorized context (memories, knowledge, recent_work)
    """
    # Validate input length
    if len(topic) > MAX_SEARCH_QUERY_LENGTH:
        return {"error": "Topic too long"}

    # Validate and bound inputs
    limit = min(max(limit, 1), 100)
    min_importance = min(max(min_importance, 1), 10)

    types = memory_types.split(",") if memory_types else ["fact", "context"]
    types = [t.strip() for t in types if t.strip() in MEMORY_TYPES]

    # E2 fix: Escape SQL wildcards
    search_term = _escape_search_wildcards(topic)
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
        key: The memory key (e.g., 'ctx_claude_20251215_ssh-setup')

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
    """Auto-detect agent name from environment or hostname.

    Priority:
    1. WORKLOG_AGENT_NAME environment variable (explicit override)
    2. Hostname-based detection (configurable)
    3. Default: "claude"
    """
    import os

    # Priority 1: Explicit environment variable
    agent_name = os.environ.get("WORKLOG_AGENT_NAME")
    if agent_name:
        return agent_name.lower()

    # Priority 2: Hostname-based (for multi-agent setups)
    hostname = os.uname().nodename.lower()

    # Check for custom hostname mapping via env (format: "hostname1:agent1,hostname2:agent2")
    hostname_map = os.environ.get("WORKLOG_HOSTNAME_MAP", "")
    if hostname_map:
        for mapping in hostname_map.split(","):
            if ":" in mapping:
                host_pattern, agent = mapping.split(":", 1)
                if host_pattern.lower() in hostname:
                    return agent.lower()

    # Priority 3: Default
    return "claude"


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
        to_agent: Target agent name or 'all' for broadcast.
                  Custom agents can be added via WORKLOG_AGENTS env var.
        message: The message/question to send
        from_agent: Sender agent name (auto-detected if not provided)
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


# =============================================================================
# CURATION TOOLS - INFA-291
# =============================================================================

@mcp.tool()
async def normalize_tag(tag: str) -> dict:
    """Normalize a tag to its canonical form using tag_taxonomy.

    Args:
        tag: The tag to normalize

    Returns:
        dict with canonical_tag, was_alias, and taxonomy entry if found
    """
    db = await get_db()
    backend = get_backend()

    tag_lower = tag.lower().strip()

    # First check if it's a canonical tag
    p1 = db.placeholder(1)
    row = await db.fetchone(
        f"SELECT * FROM tag_taxonomy WHERE LOWER(canonical_tag) = {p1}",
        tag_lower
    )

    if row:
        return {
            "found": True,
            "canonical_tag": row["canonical_tag"],
            "was_alias": False,
            "category": row.get("category"),
            "description": row.get("description"),
        }

    # Check if it's an alias
    if backend == Backend.SQLITE:
        # SQLite: Check if tag is in comma-separated aliases or JSON array
        rows = await db.fetchall("SELECT * FROM tag_taxonomy")
        for r in rows:
            aliases = r.get("aliases", [])
            if isinstance(aliases, str):
                alias_list = [a.strip().lower() for a in aliases.split(",")]
            else:
                alias_list = [a.lower() for a in (aliases or [])]
            if tag_lower in alias_list:
                return {
                    "found": True,
                    "canonical_tag": r["canonical_tag"],
                    "was_alias": True,
                    "original_tag": tag,
                    "category": r.get("category"),
                }
    else:
        # PostgreSQL: Use array contains operator
        row = await db.fetchone(
            f"SELECT * FROM tag_taxonomy WHERE {p1} = ANY(LOWER(aliases::text)::text[])",
            tag_lower
        )
        if row:
            return {
                "found": True,
                "canonical_tag": row["canonical_tag"],
                "was_alias": True,
                "original_tag": tag,
                "category": row.get("category"),
            }

    return {
        "found": False,
        "original_tag": tag,
        "suggestion": "Consider adding this tag to tag_taxonomy"
    }


@mcp.tool()
async def normalize_tags(tags: str) -> dict:
    """Normalize multiple comma-separated tags to canonical forms.

    Args:
        tags: Comma-separated list of tags to normalize

    Returns:
        dict with normalized tags, mappings, and unknown tags
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    normalized = []
    mappings = {}
    unknown = []

    for tag in tag_list:
        result = await normalize_tag(tag)
        if result.get("found"):
            canonical = result["canonical_tag"]
            normalized.append(canonical)
            if result.get("was_alias"):
                mappings[tag] = canonical
        else:
            unknown.append(tag)
            normalized.append(tag)  # Keep original if not found

    # Remove duplicates while preserving order
    seen = set()
    unique_normalized = []
    for t in normalized:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique_normalized.append(t)

    return {
        "normalized_tags": ",".join(unique_normalized),
        "original_tags": tags,
        "mappings": mappings,
        "unknown_tags": unknown,
        "tags_normalized": len(mappings),
        "tags_unknown": len(unknown),
    }


@mcp.tool()
async def add_tag_taxonomy(
    canonical_tag: str,
    aliases: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """Add a new canonical tag to the taxonomy.

    Args:
        canonical_tag: The canonical (official) tag name
        aliases: Comma-separated list of alternative spellings/names
        category: Tag category for grouping
        description: Description of what this tag represents

    Returns:
        dict with success status and tag id
    """
    db = await get_db()
    backend = get_backend()

    alias_list = [a.strip() for a in (aliases or "").split(",") if a.strip()]

    try:
        if backend == Backend.SQLITE:
            sql = """INSERT INTO tag_taxonomy
                   (canonical_tag, aliases, category, description)
                   VALUES (?, ?, ?, ?)"""
            await db.execute(sql, canonical_tag, ",".join(alias_list), category, description)
            row = await db.fetchone("SELECT last_insert_rowid() as id")
            return {"success": True, "id": row["id"], "canonical_tag": canonical_tag}
        else:
            sql = """INSERT INTO tag_taxonomy
                   (canonical_tag, aliases, category, description)
                   VALUES ($1, $2::text[], $3, $4)
                   RETURNING id"""
            row = await db.fetchone(sql, canonical_tag, alias_list, category, description)
            return {"success": True, "id": row["id"], "canonical_tag": canonical_tag}
    except Exception as e:
        if "unique" in str(e).lower():
            return {"error": f"Tag '{canonical_tag}' already exists in taxonomy"}
        raise


@mcp.tool()
async def add_relationship(
    source_table: str,
    source_id: int,
    target_table: str,
    target_id: int,
    relationship_type: str,
    confidence: float = 1.0,
    bidirectional: bool = True,
    created_by: Optional[str] = None,
) -> dict:
    """Add a relationship between two entries.

    Args:
        source_table: Source table name (memories, knowledge_base, entries)
        source_id: Source entry ID
        target_table: Target table name (memories, knowledge_base, entries)
        target_id: Target entry ID
        relationship_type: Type of relationship (relates_to, supersedes, implements, etc.)
        confidence: Confidence score 0.0-1.0 (default 1.0)
        bidirectional: Whether relationship goes both ways (default True)
        created_by: Agent or user who created this relationship

    Returns:
        dict with success status and relationship id
    """
    # Validate table names
    if source_table not in ENTRY_TABLES:
        return {"error": f"Invalid source_table. Must be one of: {ENTRY_TABLES}"}
    if target_table not in ENTRY_TABLES:
        return {"error": f"Invalid target_table. Must be one of: {ENTRY_TABLES}"}

    # Validate relationship type
    if relationship_type not in RELATIONSHIP_TYPES:
        return {"error": f"Invalid relationship_type. Must be one of: {RELATIONSHIP_TYPES}"}

    # Validate confidence
    confidence = max(0.0, min(1.0, confidence))

    db = await get_db()
    backend = get_backend()

    try:
        if backend == Backend.SQLITE:
            sql = """INSERT INTO relationships
                   (source_table, source_id, target_table, target_id,
                    relationship_type, confidence, bidirectional, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            await db.execute(sql, source_table, source_id, target_table, target_id,
                           relationship_type, confidence, bidirectional, created_by)
            row = await db.fetchone("SELECT last_insert_rowid() as id")
            return {"success": True, "id": row["id"]}
        else:
            sql = """INSERT INTO relationships
                   (source_table, source_id, target_table, target_id,
                    relationship_type, confidence, bidirectional, created_by)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                   RETURNING id"""
            row = await db.fetchone(sql, source_table, source_id, target_table, target_id,
                                   relationship_type, confidence, bidirectional, created_by)
            return {"success": True, "id": row["id"]}
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            return {"error": "This relationship already exists"}
        if "Invalid source reference" in str(e) or "Invalid target reference" in str(e):
            return {"error": str(e)}
        raise


@mcp.tool()
async def get_relationships(
    entry_table: str,
    entry_id: int,
    relationship_type: Optional[str] = None,
    direction: str = "both",
) -> dict:
    """Get relationships for an entry.

    Args:
        entry_table: Table name of the entry (memories, knowledge_base, entries)
        entry_id: Entry ID
        relationship_type: Filter by relationship type (optional)
        direction: "outgoing", "incoming", or "both" (default)

    Returns:
        dict with outgoing and incoming relationships
    """
    if entry_table not in ENTRY_TABLES:
        return {"error": f"Invalid entry_table. Must be one of: {ENTRY_TABLES}"}

    db = await get_db()
    backend = get_backend()

    results = {"outgoing": [], "incoming": [], "entry_table": entry_table, "entry_id": entry_id}

    # Build base queries
    if backend == Backend.SQLITE:
        out_sql = """SELECT * FROM relationships
                    WHERE source_table = ? AND source_id = ?"""
        in_sql = """SELECT * FROM relationships
                   WHERE target_table = ? AND target_id = ?"""
        params = [entry_table, entry_id]

        if relationship_type:
            out_sql += " AND relationship_type = ?"
            in_sql += " AND relationship_type = ?"
            params.append(relationship_type)

        if direction in ("outgoing", "both"):
            if relationship_type:
                results["outgoing"] = await db.fetchall(out_sql, entry_table, entry_id, relationship_type)
            else:
                results["outgoing"] = await db.fetchall(out_sql, entry_table, entry_id)

        if direction in ("incoming", "both"):
            if relationship_type:
                results["incoming"] = await db.fetchall(in_sql, entry_table, entry_id, relationship_type)
            else:
                results["incoming"] = await db.fetchall(in_sql, entry_table, entry_id)
    else:
        out_sql = """SELECT * FROM relationships
                    WHERE source_table = $1 AND source_id = $2"""
        in_sql = """SELECT * FROM relationships
                   WHERE target_table = $1 AND target_id = $2"""

        if relationship_type:
            out_sql += " AND relationship_type = $3"
            in_sql += " AND relationship_type = $3"

        if direction in ("outgoing", "both"):
            if relationship_type:
                results["outgoing"] = await db.fetchall(out_sql, entry_table, entry_id, relationship_type)
            else:
                results["outgoing"] = await db.fetchall(out_sql, entry_table, entry_id)

        if direction in ("incoming", "both"):
            if relationship_type:
                results["incoming"] = await db.fetchall(in_sql, entry_table, entry_id, relationship_type)
            else:
                results["incoming"] = await db.fetchall(in_sql, entry_table, entry_id)

    results["total"] = len(results["outgoing"]) + len(results["incoming"])
    return results


@mcp.tool()
async def create_topic(
    topic_name: str,
    summary: Optional[str] = None,
    key_terms: Optional[str] = None,
) -> dict:
    """Create a new topic in the topic index.

    Args:
        topic_name: Unique name for the topic
        summary: Brief TLDR summary of the topic
        key_terms: Comma-separated key terms for this topic

    Returns:
        dict with success status and topic id
    """
    db = await get_db()
    backend = get_backend()

    term_list = [t.strip() for t in (key_terms or "").split(",") if t.strip()]

    try:
        if backend == Backend.SQLITE:
            sql = """INSERT INTO topic_index (topic_name, summary, key_terms)
                   VALUES (?, ?, ?)"""
            await db.execute(sql, topic_name, summary, ",".join(term_list))
            row = await db.fetchone("SELECT last_insert_rowid() as id")
            return {"success": True, "id": row["id"], "topic_name": topic_name}
        else:
            sql = """INSERT INTO topic_index (topic_name, summary, key_terms)
                   VALUES ($1, $2, $3::text[])
                   RETURNING id"""
            row = await db.fetchone(sql, topic_name, summary, term_list)
            return {"success": True, "id": row["id"], "topic_name": topic_name}
    except Exception as e:
        if "unique" in str(e).lower():
            return {"error": f"Topic '{topic_name}' already exists"}
        raise


@mcp.tool()
async def add_topic_entry(
    topic_name: str,
    entry_table: str,
    entry_id: int,
    relevance_score: float = 1.0,
) -> dict:
    """Add an entry to a topic.

    Args:
        topic_name: Name of the topic
        entry_table: Table of the entry (memories, knowledge_base, entries)
        entry_id: ID of the entry
        relevance_score: How relevant this entry is to the topic (0.0-1.0)

    Returns:
        dict with success status
    """
    if entry_table not in ENTRY_TABLES:
        return {"error": f"Invalid entry_table. Must be one of: {ENTRY_TABLES}"}

    relevance_score = max(0.0, min(1.0, relevance_score))

    db = await get_db()
    backend = get_backend()

    # Get topic ID
    p1 = db.placeholder(1)
    topic = await db.fetchone(f"SELECT id FROM topic_index WHERE topic_name = {p1}", topic_name)
    if not topic:
        return {"error": f"Topic '{topic_name}' not found. Create it first with create_topic."}

    topic_id = topic["id"]

    try:
        if backend == Backend.SQLITE:
            sql = """INSERT INTO topic_entries (topic_id, entry_table, entry_id, relevance_score)
                   VALUES (?, ?, ?, ?)"""
            await db.execute(sql, topic_id, entry_table, entry_id, relevance_score)
            return {"success": True, "topic_name": topic_name, "entry_added": f"{entry_table}.{entry_id}"}
        else:
            sql = """INSERT INTO topic_entries (topic_id, entry_table, entry_id, relevance_score)
                   VALUES ($1, $2, $3, $4)
                   RETURNING id"""
            row = await db.fetchone(sql, topic_id, entry_table, entry_id, relevance_score)
            return {"success": True, "id": row["id"], "topic_name": topic_name}
    except Exception as e:
        if "unique" in str(e).lower():
            return {"error": "This entry is already in the topic"}
        if "Invalid entry reference" in str(e):
            return {"error": str(e)}
        raise


@mcp.tool()
async def get_topic_entries(
    topic_name: str,
    entry_table: Optional[str] = None,
    min_relevance: float = 0.0,
    limit: int = 50,
) -> dict:
    """Get all entries for a topic.

    Args:
        topic_name: Name of the topic
        entry_table: Filter by table (optional)
        min_relevance: Minimum relevance score (0.0-1.0)
        limit: Maximum entries to return

    Returns:
        dict with topic info and entries
    """
    db = await get_db()
    backend = get_backend()

    # Get topic
    p1 = db.placeholder(1)
    topic = await db.fetchone(
        f"SELECT * FROM topic_index WHERE topic_name = {p1}",
        topic_name
    )
    if not topic:
        return {"error": f"Topic '{topic_name}' not found"}

    # Get entries
    if backend == Backend.SQLITE:
        sql = """SELECT te.*,
                 CASE te.entry_table
                   WHEN 'memories' THEN (SELECT key FROM memories WHERE id = te.entry_id)
                   WHEN 'knowledge_base' THEN (SELECT title FROM knowledge_base WHERE id = te.entry_id)
                   WHEN 'entries' THEN (SELECT title FROM entries WHERE id = te.entry_id)
                 END as entry_title
                 FROM topic_entries te
                 WHERE te.topic_id = ? AND te.relevance_score >= ?"""
        params = [topic["id"], min_relevance]

        if entry_table:
            sql += " AND te.entry_table = ?"
            params.append(entry_table)

        sql += " ORDER BY te.relevance_score DESC LIMIT ?"
        params.append(limit)

        entries = await db.fetchall(sql, *params)
    else:
        sql = """SELECT te.*,
                 CASE te.entry_table
                   WHEN 'memories' THEN (SELECT key FROM memories WHERE id = te.entry_id)
                   WHEN 'knowledge_base' THEN (SELECT title FROM knowledge_base WHERE id = te.entry_id)
                   WHEN 'entries' THEN (SELECT title FROM entries WHERE id = te.entry_id)
                 END as entry_title
                 FROM topic_entries te
                 WHERE te.topic_id = $1 AND te.relevance_score >= $2"""
        params = [topic["id"], min_relevance]

        if entry_table:
            sql += " AND te.entry_table = $3"
            params.append(entry_table)
            sql += " ORDER BY te.relevance_score DESC LIMIT $4"
            params.append(limit)
        else:
            sql += " ORDER BY te.relevance_score DESC LIMIT $3"
            params.append(limit)

        entries = await db.fetchall(sql, *params)

    return {
        "topic": dict(topic),
        "entries": entries,
        "count": len(entries),
    }


@mcp.tool()
async def update_topic_summary(
    topic_name: str,
    summary: Optional[str] = None,
    full_summary: Optional[str] = None,
    key_terms: Optional[str] = None,
) -> dict:
    """Update a topic's summary and metadata.

    Args:
        topic_name: Name of the topic to update
        summary: Brief TLDR summary
        full_summary: Longer summary with anchor links
        key_terms: Comma-separated key terms

    Returns:
        dict with success status
    """
    db = await get_db()
    backend = get_backend()

    updates = []
    params = []

    if backend == Backend.SQLITE:
        if summary is not None:
            updates.append("summary = ?")
            params.append(summary)
        if full_summary is not None:
            updates.append("full_summary = ?")
            params.append(full_summary)
        if key_terms is not None:
            updates.append("key_terms = ?")
            params.append(key_terms)

        updates.append("last_curated = CURRENT_TIMESTAMP")

        if not params:
            return {"error": "No fields to update"}

        params.append(topic_name)
        sql = f"UPDATE topic_index SET {', '.join(updates)} WHERE topic_name = ?"
    else:
        idx = 1
        if summary is not None:
            updates.append(f"summary = ${idx}")
            params.append(summary)
            idx += 1
        if full_summary is not None:
            updates.append(f"full_summary = ${idx}")
            params.append(full_summary)
            idx += 1
        if key_terms is not None:
            term_list = [t.strip() for t in key_terms.split(",") if t.strip()]
            updates.append(f"key_terms = ${idx}::text[]")
            params.append(term_list)
            idx += 1

        updates.append("last_curated = CURRENT_TIMESTAMP")

        if not params:
            return {"error": "No fields to update"}

        params.append(topic_name)
        sql = f"UPDATE topic_index SET {', '.join(updates)} WHERE topic_name = ${idx}"

    result = await db.execute(sql, *params)

    if "0" in result or result.endswith(" 0"):
        return {"error": f"Topic '{topic_name}' not found"}

    return {"success": True, "topic_name": topic_name}


@mcp.tool()
async def log_curation_run(
    operation: str,
    agent: Optional[str] = None,
    stats: Optional[str] = None,
    duration_seconds: Optional[float] = None,
    success: bool = True,
    error_message: Optional[str] = None,
) -> dict:
    """Log a curation operation to curation_history.

    Args:
        operation: Type of operation (tag_normalization, relationship_discovery, etc.)
        agent: Agent that performed the curation
        stats: JSON string with operation statistics
        duration_seconds: How long the operation took
        success: Whether the operation succeeded
        error_message: Error message if operation failed

    Returns:
        dict with success status and entry id
    """

    db = await get_db()
    backend = get_backend()

    # Parse stats JSON if provided
    stats_json = {}
    if stats:
        try:
            stats_json = json.loads(stats)
        except json.JSONDecodeError:
            stats_json = {"raw": stats}

    if backend == Backend.SQLITE:
        sql = """INSERT INTO curation_history
               (operation, agent, stats, duration_seconds, success, error_message)
               VALUES (?, ?, ?, ?, ?, ?)"""
        await db.execute(sql, operation, agent, json.dumps(stats_json),
                        duration_seconds, 1 if success else 0, error_message)
        row = await db.fetchone("SELECT last_insert_rowid() as id")
        return {"success": True, "id": row["id"]}
    else:
        sql = """INSERT INTO curation_history
               (operation, agent, stats, duration_seconds, success, error_message)
               VALUES ($1, $2, $3::jsonb, $4, $5, $6)
               RETURNING id"""
        row = await db.fetchone(sql, operation, agent, json.dumps(stats_json),
                               duration_seconds, success, error_message)
        return {"success": True, "id": row["id"]}



# =============================================================================
# ENHANCED RETRIEVAL TOOLS - INFA-294
# =============================================================================

@mcp.tool()
async def recall_topic(
    topic_name: str,
    include_entries: bool = True,
    max_entries: int = 20,
) -> dict:
    """Recall a topic with its pre-computed summary and optionally linked entries.

    This provides efficient context loading by returning curated topic summaries
    instead of raw entry content, reducing token usage.

    Args:
        topic_name: Name of the topic to recall
        include_entries: Whether to include linked entries (default True)
        max_entries: Maximum entries to return if include_entries is True

    Returns:
        dict with topic summary, key terms, and optionally linked entries
    """
    db = await get_db()
    backend = get_backend()
    p1 = db.placeholder(1)

    # Get topic
    topic = await db.fetchone(
        f"SELECT * FROM topic_index WHERE topic_name = {p1}",
        topic_name
    )

    if not topic:
        # Try partial match
        if backend == Backend.SQLITE:
            topic = await db.fetchone(
                "SELECT * FROM topic_index WHERE topic_name LIKE ? ORDER BY entry_count DESC LIMIT 1",
                f"%{topic_name}%"
            )
        else:
            topic = await db.fetchone(
                "SELECT * FROM topic_index WHERE topic_name ILIKE $1 ORDER BY entry_count DESC LIMIT 1",
                f"%{topic_name}%"
            )

    if not topic:
        return {"error": f"Topic '{topic_name}' not found", "suggestion": "Use create_topic to create it"}

    result = {
        "topic_name": topic["topic_name"],
        "summary": topic.get("summary"),
        "full_summary": topic.get("full_summary"),
        "key_terms": topic.get("key_terms", []),
        "entry_count": topic.get("entry_count", 0),
        "last_curated": str(topic.get("last_curated")) if topic.get("last_curated") else None,
    }

    if include_entries and topic.get("entry_count", 0) > 0:
        # Get linked entries with titles
        if backend == Backend.SQLITE:
            entries = await db.fetchall(
                """SELECT te.entry_table, te.entry_id, te.relevance_score,
                   CASE te.entry_table
                     WHEN 'memories' THEN (SELECT key FROM memories WHERE id = te.entry_id)
                     WHEN 'knowledge_base' THEN (SELECT title FROM knowledge_base WHERE id = te.entry_id)
                     WHEN 'entries' THEN (SELECT title FROM entries WHERE id = te.entry_id)
                   END as entry_title
                   FROM topic_entries te
                   WHERE te.topic_id = ?
                   ORDER BY te.relevance_score DESC
                   LIMIT ?""",
                topic["id"], max_entries
            )
        else:
            entries = await db.fetchall(
                """SELECT te.entry_table, te.entry_id, te.relevance_score,
                   CASE te.entry_table
                     WHEN 'memories' THEN (SELECT key FROM memories WHERE id = te.entry_id)
                     WHEN 'knowledge_base' THEN (SELECT title FROM knowledge_base WHERE id = te.entry_id)
                     WHEN 'entries' THEN (SELECT title FROM entries WHERE id = te.entry_id)
                   END as entry_title
                   FROM topic_entries te
                   WHERE te.topic_id = $1
                   ORDER BY te.relevance_score DESC
                   LIMIT $2""",
                topic["id"], max_entries
            )
        result["entries"] = entries

    return result


@mcp.tool()
async def find_related(
    entry_table: str,
    entry_id: int,
    depth: int = 1,
    relationship_types: Optional[str] = None,
) -> dict:
    """Traverse the relationship graph to find related entries.

    Args:
        entry_table: Source table (memories, knowledge_base, entries)
        entry_id: Source entry ID
        depth: How many hops to traverse (1-3, default 1)
        relationship_types: Comma-separated types to filter (optional)

    Returns:
        dict with related entries organized by depth level
    """
    if entry_table not in ENTRY_TABLES:
        return {"error": f"Invalid entry_table. Must be one of: {ENTRY_TABLES}"}

    depth = max(1, min(3, depth))  # Clamp to 1-3
    type_filter = [t.strip() for t in (relationship_types or "").split(",") if t.strip()]

    db = await get_db()
    backend = get_backend()

    results = {"source": {"table": entry_table, "id": entry_id}, "levels": {}}
    visited = {(entry_table, entry_id)}
    current_level = [(entry_table, entry_id)]

    for level in range(1, depth + 1):
        next_level = []
        level_results = []

        for table, eid in current_level:
            # Get outgoing relationships
            if backend == Backend.SQLITE:
                out_sql = """SELECT target_table, target_id, relationship_type, confidence
                            FROM relationships
                            WHERE source_table = ? AND source_id = ?"""
                in_sql = """SELECT source_table, source_id, relationship_type, confidence
                           FROM relationships
                           WHERE target_table = ? AND target_id = ? AND bidirectional = 1"""
                params = [table, eid]

                if type_filter:
                    placeholders = ",".join(["?" for _ in type_filter])
                    out_sql += f" AND relationship_type IN ({placeholders})"
                    in_sql += f" AND relationship_type IN ({placeholders})"
                    params.extend(type_filter)

                outgoing = await db.fetchall(out_sql, *params)
                incoming = await db.fetchall(in_sql, *params)
            else:
                out_sql = """SELECT target_table, target_id, relationship_type, confidence
                            FROM relationships
                            WHERE source_table = $1 AND source_id = $2"""
                in_sql = """SELECT source_table, source_id, relationship_type, confidence
                           FROM relationships
                           WHERE target_table = $1 AND target_id = $2 AND bidirectional = true"""

                if type_filter:
                    out_sql += " AND relationship_type = ANY($3)"
                    in_sql += " AND relationship_type = ANY($3)"
                    outgoing = await db.fetchall(out_sql, table, eid, type_filter)
                    incoming = await db.fetchall(in_sql, table, eid, type_filter)
                else:
                    outgoing = await db.fetchall(out_sql, table, eid)
                    incoming = await db.fetchall(in_sql, table, eid)

            # Process outgoing
            for row in outgoing:
                target = (row["target_table"], row["target_id"])
                if target not in visited:
                    visited.add(target)
                    next_level.append(target)
                    level_results.append({
                        "table": row["target_table"],
                        "id": row["target_id"],
                        "relationship": row["relationship_type"],
                        "confidence": row["confidence"],
                        "direction": "outgoing",
                    })

            # Process incoming (bidirectional)
            for row in incoming:
                source = (row["source_table"], row["source_id"])
                if source not in visited:
                    visited.add(source)
                    next_level.append(source)
                    level_results.append({
                        "table": row["source_table"],
                        "id": row["source_id"],
                        "relationship": row["relationship_type"],
                        "confidence": row["confidence"],
                        "direction": "incoming",
                    })

        if level_results:
            results["levels"][f"depth_{level}"] = level_results

        current_level = next_level
        if not current_level:
            break

    results["total_related"] = len(visited) - 1  # Exclude source
    return results


@mcp.tool()
async def search_by_taxonomy(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    include_aliases: bool = True,
    limit: int = 20,
) -> dict:
    """Search entries using the tag taxonomy for hierarchical tag matching.

    Args:
        category: Tag category to filter by (optional)
        tag: Specific tag to search for (will match canonical and aliases)
        include_aliases: Whether to match tag aliases (default True)
        limit: Maximum entries to return

    Returns:
        dict with matching entries grouped by table
    """
    db = await get_db()
    backend = get_backend()

    # First, resolve the tag to its canonical form and get aliases
    tags_to_match = []

    if tag:
        p1 = db.placeholder(1)
        tag_lower = tag.lower().strip()

        # Check if it's a canonical tag
        taxonomy = await db.fetchone(
            f"SELECT * FROM tag_taxonomy WHERE LOWER(canonical_tag) = {p1}",
            tag_lower
        )

        if not taxonomy and backend == Backend.POSTGRESQL:
            # Check aliases
            taxonomy = await db.fetchone(
                "SELECT * FROM tag_taxonomy WHERE $1 = ANY(LOWER(aliases::text)::text[])",
                tag_lower
            )

        if taxonomy:
            tags_to_match.append(taxonomy["canonical_tag"])
            if include_aliases and taxonomy.get("aliases"):
                aliases = taxonomy["aliases"]
                if isinstance(aliases, str):
                    tags_to_match.extend([a.strip() for a in aliases.split(",")])
                else:
                    tags_to_match.extend(aliases)
        else:
            tags_to_match.append(tag)  # Use original if not in taxonomy

    elif category:
        # Get all tags in this category
        if backend == Backend.SQLITE:
            rows = await db.fetchall(
                "SELECT canonical_tag, aliases FROM tag_taxonomy WHERE category = ?",
                category
            )
        else:
            rows = await db.fetchall(
                "SELECT canonical_tag, aliases FROM tag_taxonomy WHERE category = $1",
                category
            )

        for row in rows:
            tags_to_match.append(row["canonical_tag"])
            if include_aliases and row.get("aliases"):
                aliases = row["aliases"]
                if isinstance(aliases, str):
                    tags_to_match.extend([a.strip() for a in aliases.split(",")])
                else:
                    tags_to_match.extend(aliases)

    if not tags_to_match:
        return {"error": "Must specify either category or tag", "tags_to_match": []}

    results = {"tags_matched": tags_to_match, "memories": [], "knowledge_base": []}

    # Build tag matching conditions
    if backend == Backend.SQLITE:
        conditions = " OR ".join([
            f"tags = ? OR tags LIKE ? OR tags LIKE ? OR tags LIKE ?"
            for _ in tags_to_match
        ])
        params = []
        for t in tags_to_match:
            params.extend([t, f"{t},%", f"%,{t},%", f"%,{t}"])

        # Search memories
        mem_sql = f"""SELECT id, key, summary, tags, importance
                     FROM memories WHERE ({conditions})
                     ORDER BY importance DESC LIMIT ?"""
        params_mem = params + [limit]
        results["memories"] = await db.fetchall(mem_sql, *params_mem)

        # Search knowledge_base
        kb_sql = f"""SELECT id, title, category, tags
                    FROM knowledge_base WHERE ({conditions})
                    ORDER BY updated_at DESC LIMIT ?"""
        params_kb = params + [limit]
        results["knowledge_base"] = await db.fetchall(kb_sql, *params_kb)
    else:
        # PostgreSQL - use ANY with array
        mem_sql = """SELECT id, key, summary, tags, importance
                    FROM memories
                    WHERE EXISTS (
                        SELECT 1 FROM unnest(string_to_array(tags, ',')) AS t
                        WHERE LOWER(TRIM(t)) = ANY($1)
                    )
                    ORDER BY importance DESC LIMIT $2"""
        results["memories"] = await db.fetchall(
            mem_sql, [t.lower() for t in tags_to_match], limit
        )

        kb_sql = """SELECT id, title, category, tags
                   FROM knowledge_base
                   WHERE EXISTS (
                       SELECT 1 FROM unnest(string_to_array(tags, ',')) AS t
                       WHERE LOWER(TRIM(t)) = ANY($1)
                   )
                   ORDER BY updated_at DESC LIMIT $2"""
        results["knowledge_base"] = await db.fetchall(
            kb_sql, [t.lower() for t in tags_to_match], limit
        )

    results["total"] = len(results["memories"]) + len(results["knowledge_base"])
    return results


@mcp.tool()
async def get_topic_hierarchy(
    root_topic: Optional[str] = None,
) -> dict:
    """Get the topic hierarchy showing all topics and their entry counts.

    Args:
        root_topic: Optional root topic to start from (returns full tree if None)

    Returns:
        dict with topic tree structure and statistics
    """
    db = await get_db()
    backend = get_backend()

    # Get all topics
    if backend == Backend.SQLITE:
        topics = await db.fetchall(
            "SELECT id, topic_name, summary, entry_count, key_terms FROM topic_index ORDER BY entry_count DESC"
        )
    else:
        topics = await db.fetchall(
            "SELECT id, topic_name, summary, entry_count, key_terms FROM topic_index ORDER BY entry_count DESC"
        )

    if root_topic:
        # Filter to specific topic and its related topics
        root = next((t for t in topics if t["topic_name"].lower() == root_topic.lower()), None)
        if not root:
            return {"error": f"Topic '{root_topic}' not found"}

        # Find topics that share entries with root topic
        if backend == Backend.SQLITE:
            related_ids = await db.fetchall(
                """SELECT DISTINCT te2.topic_id
                   FROM topic_entries te1
                   JOIN topic_entries te2 ON te1.entry_table = te2.entry_table
                                          AND te1.entry_id = te2.entry_id
                   WHERE te1.topic_id = ? AND te2.topic_id != ?""",
                root["id"], root["id"]
            )
        else:
            related_ids = await db.fetchall(
                """SELECT DISTINCT te2.topic_id
                   FROM topic_entries te1
                   JOIN topic_entries te2 ON te1.entry_table = te2.entry_table
                                          AND te1.entry_id = te2.entry_id
                   WHERE te1.topic_id = $1 AND te2.topic_id != $1""",
                root["id"]
            )

        related_topic_ids = {row["topic_id"] for row in related_ids}
        related_topic_ids.add(root["id"])

        topics = [t for t in topics if t["id"] in related_topic_ids]

    # Build hierarchy structure
    hierarchy = {
        "topics": [
            {
                "name": t["topic_name"],
                "summary": t.get("summary"),
                "entry_count": t.get("entry_count", 0),
                "key_terms": t.get("key_terms", []),
            }
            for t in topics
        ],
        "total_topics": len(topics),
        "total_entries": sum(t.get("entry_count", 0) for t in topics),
    }

    if root_topic:
        hierarchy["root_topic"] = root_topic

    return hierarchy



# =============================================================================
# CURATION AUTOMATION TOOLS - INFA-295
# =============================================================================

@mcp.tool()
async def get_curation_metrics(
    days: int = 7,
) -> dict:
    """Get curation quality metrics and health indicators.

    Returns dashboard data for monitoring curation health including:
    - Recent curation activity
    - Data quality indicators
    - Alert thresholds
    - Recommendations

    Args:
        days: Number of days to analyze (default 7)

    Returns:
        dict with metrics, alerts, and recommendations
    """

    db = await get_db()
    backend = get_backend()

    metrics = {
        "generated_at": datetime.now().isoformat(),
        "period_days": days,
        "table_counts": {},
        "curation_activity": {},
        "quality_indicators": {},
        "alerts": [],
        "recommendations": [],
    }

    # Table counts
    tables = [
        "memories", "knowledge_base", "entries",
        "tag_taxonomy", "relationships", "topic_index",
        "topic_entries", "duplicate_candidates", "curation_history"
    ]

    for table in tables:
        try:
            result = await db.fetchone(f"SELECT COUNT(*) as cnt FROM {table}")
            metrics["table_counts"][table] = result["cnt"] if result else 0
        except Exception:
            metrics["table_counts"][table] = -1  # Table doesn't exist

    # Curation activity (last N days)
    if backend == Backend.SQLITE:
        activity = await db.fetchall(
            """SELECT operation, COUNT(*) as runs,
                      SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
               FROM curation_history
               WHERE run_at > datetime('now', ?)
               GROUP BY operation""",
            f"-{days} days"
        )
        last_run = await db.fetchone(
            "SELECT run_at, operation, success FROM curation_history ORDER BY run_at DESC LIMIT 1"
        )
    else:
        activity = await db.fetchall(
            """SELECT operation, COUNT(*) as runs,
                      SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
               FROM curation_history
               WHERE run_at > NOW() - INTERVAL '%s days'
               GROUP BY operation""" % days
        )
        last_run = await db.fetchone(
            "SELECT run_at, operation, success FROM curation_history ORDER BY run_at DESC LIMIT 1"
        )

    metrics["curation_activity"] = {
        "operations": [dict(a) for a in activity] if activity else [],
        "last_run": {
            "timestamp": str(last_run["run_at"]) if last_run else None,
            "operation": last_run["operation"] if last_run else None,
            "success": last_run["success"] if last_run else None,
        } if last_run else None,
    }

    # Quality indicators
    # 1. Orphan rate (entries without topics or relationships)
    if backend == Backend.SQLITE:
        orphan_memories = await db.fetchone(
            """SELECT COUNT(*) as cnt FROM memories m
               WHERE importance >= 5
               AND NOT EXISTS (SELECT 1 FROM topic_entries te
                              WHERE te.entry_table = 'memories' AND te.entry_id = m.id)
               AND NOT EXISTS (SELECT 1 FROM relationships r
                              WHERE (r.source_table = 'memories' AND r.source_id = m.id)
                                 OR (r.target_table = 'memories' AND r.target_id = m.id))"""
        )
        total_important = await db.fetchone(
            "SELECT COUNT(*) as cnt FROM memories WHERE importance >= 5"
        )
    else:
        orphan_memories = await db.fetchone(
            """SELECT COUNT(*) as cnt FROM memories m
               WHERE importance >= 5
               AND NOT EXISTS (SELECT 1 FROM topic_entries te
                              WHERE te.entry_table = 'memories' AND te.entry_id = m.id)
               AND NOT EXISTS (SELECT 1 FROM relationships r
                              WHERE (r.source_table = 'memories' AND r.source_id = m.id)
                                 OR (r.target_table = 'memories' AND r.target_id = m.id))"""
        )
        total_important = await db.fetchone(
            "SELECT COUNT(*) as cnt FROM memories WHERE importance >= 5"
        )

    orphan_count = orphan_memories["cnt"] if orphan_memories else 0
    total_count = total_important["cnt"] if total_important else 1
    orphan_rate = round(orphan_count / max(total_count, 1) * 100, 1)

    # 2. Pending duplicates
    if backend == Backend.SQLITE:
        pending_dupes = await db.fetchone(
            "SELECT COUNT(*) as cnt FROM duplicate_candidates WHERE status = 'pending'"
        )
    else:
        pending_dupes = await db.fetchone(
            "SELECT COUNT(*) as cnt FROM duplicate_candidates WHERE status = 'pending'"
        )

    # 3. Tag coverage (entries with vs without tags)
    if backend == Backend.SQLITE:
        tagged = await db.fetchone(
            "SELECT COUNT(*) as cnt FROM memories WHERE tags IS NOT NULL AND tags != ''"
        )
        untagged = await db.fetchone(
            "SELECT COUNT(*) as cnt FROM memories WHERE tags IS NULL OR tags = ''"
        )
    else:
        tagged = await db.fetchone(
            "SELECT COUNT(*) as cnt FROM memories WHERE tags IS NOT NULL AND tags != ''"
        )
        untagged = await db.fetchone(
            "SELECT COUNT(*) as cnt FROM memories WHERE tags IS NULL OR tags = ''"
        )

    tagged_count = tagged["cnt"] if tagged else 0
    untagged_count = untagged["cnt"] if untagged else 0
    tag_coverage = round(tagged_count / max(tagged_count + untagged_count, 1) * 100, 1)

    # 4. Staging memories awaiting promotion
    if backend == Backend.SQLITE:
        staging = await db.fetchone(
            """SELECT COUNT(*) as cnt FROM memories
               WHERE status = 'staging' AND importance >= 6
               AND created_at < datetime('now', '-2 days')"""
        )
    else:
        staging = await db.fetchone(
            """SELECT COUNT(*) as cnt FROM memories
               WHERE status = 'staging' AND importance >= 6
               AND created_at < NOW() - INTERVAL '2 days'"""
        )

    metrics["quality_indicators"] = {
        "orphan_rate_pct": orphan_rate,
        "orphan_count": orphan_count,
        "pending_duplicates": pending_dupes["cnt"] if pending_dupes else 0,
        "tag_coverage_pct": tag_coverage,
        "untagged_entries": untagged_count,
        "staging_awaiting_promotion": staging["cnt"] if staging else 0,
        "topic_count": metrics["table_counts"].get("topic_index", 0),
        "relationship_count": metrics["table_counts"].get("relationships", 0),
    }

    # Generate alerts
    if orphan_rate > 30:
        metrics["alerts"].append({
            "severity": "warning",
            "message": f"High orphan rate: {orphan_rate}% of important memories unlinked",
            "action": "Run /curate orphans",
        })

    pending_dupe_count = pending_dupes["cnt"] if pending_dupes else 0
    if pending_dupe_count > 10:
        metrics["alerts"].append({
            "severity": "warning",
            "message": f"{pending_dupe_count} duplicate candidates pending review",
            "action": "Run /curate duplicates",
        })

    staging_count = staging["cnt"] if staging else 0
    if staging_count > 20:
        metrics["alerts"].append({
            "severity": "info",
            "message": f"{staging_count} memories awaiting promotion",
            "action": "Run /curate promote",
        })

    if tag_coverage < 50:
        metrics["alerts"].append({
            "severity": "warning",
            "message": f"Low tag coverage: {tag_coverage}%",
            "action": "Run /curate taxonomy",
        })

    # Check for stale curation
    if metrics["curation_activity"]["last_run"]:
        last_ts = metrics["curation_activity"]["last_run"]["timestamp"]
        if last_ts:
            # Simple staleness check
            metrics["alerts"].append({
                "severity": "info",
                "message": f"Last curation: {last_ts}",
                "action": "Consider scheduling regular curation",
            })
    else:
        metrics["alerts"].append({
            "severity": "warning",
            "message": "No curation history found",
            "action": "Run initial curation with /curate",
        })

    # Generate recommendations
    if orphan_rate > 20:
        metrics["recommendations"].append("Focus on linking orphan entries to topics")

    if pending_dupe_count > 0:
        metrics["recommendations"].append("Review and resolve duplicate candidates")

    if tag_coverage < 70:
        metrics["recommendations"].append("Improve tag coverage for better searchability")

    if metrics["table_counts"].get("topic_index", 0) < 5:
        metrics["recommendations"].append("Create more topics to organize knowledge")

    return metrics


@mcp.tool()
async def get_curation_schedule() -> dict:
    """Get recommended curation schedule based on current data volume.

    Returns recommended frequencies for each curation operation
    based on table sizes and activity levels.

    Returns:
        dict with schedule recommendations and cron expressions
    """
    db = await get_db()

    # Get table counts for sizing
    counts = {}
    for table in ["memories", "knowledge_base", "entries"]:
        try:
            result = await db.fetchone(f"SELECT COUNT(*) as cnt FROM {table}")
            counts[table] = result["cnt"] if result else 0
        except Exception:
            counts[table] = 0

    total_entries = sum(counts.values())

    # Determine frequency based on volume
    if total_entries < 100:
        frequency = "weekly"
        cron = "0 2 * * 0"  # Sunday 2am
    elif total_entries < 500:
        frequency = "twice-weekly"
        cron = "0 2 * * 0,3"  # Sunday and Wednesday 2am
    elif total_entries < 2000:
        frequency = "daily"
        cron = "0 2 * * *"  # Daily 2am
    else:
        frequency = "twice-daily"
        cron = "0 2,14 * * *"  # 2am and 2pm

    schedule = {
        "data_volume": {
            "total_entries": total_entries,
            "breakdown": counts,
        },
        "recommended_frequency": frequency,
        "operations": {
            "full_curation": {
                "frequency": frequency,
                "cron": cron,
                "description": "Complete curation cycle (all phases)",
            },
            "tag_normalization": {
                "frequency": "with_full" if total_entries < 500 else "daily",
                "cron": "0 3 * * *" if total_entries >= 500 else None,
                "description": "Normalize tags and update taxonomy",
            },
            "duplicate_detection": {
                "frequency": "weekly",
                "cron": "0 4 * * 0",
                "description": "Scan for potential duplicates",
            },
            "memory_promotion": {
                "frequency": "daily" if total_entries >= 200 else "weekly",
                "cron": "0 5 * * *" if total_entries >= 200 else "0 5 * * 0",
                "description": "Evaluate staging memories for promotion",
            },
        },
        "setup_instructions": {
            "systemd_timer": f"""# /etc/systemd/system/kb-curator.timer
[Unit]
Description=Knowledge Base Curation Timer

[Timer]
OnCalendar={cron.replace('0 ', '').replace(' * * ', ':00 ')}
Persistent=true

[Install]
WantedBy=timers.target""",
            "cron_entry": f"{cron} /path/to/curator-runner.sh >> /var/log/kb-curator.log 2>&1",
        },
    }

    return schedule



def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
