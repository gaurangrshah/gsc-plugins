"""Worklog MCP Server - Structured access to shared knowledge base.

Provides tools for querying and storing data in the shared worklog.db database
used across all Claude Code instances (atlas, m4-mini-work, ubuntu-mini).
"""

import json
import aiosqlite
from datetime import datetime
from typing import Optional
from fastmcp import FastMCP

from worklog_mcp.config import (
    get_database_path,
    TABLES,
    MEMORY_TYPES,
    MEMORY_STATUSES,
    TASK_TYPES,
    KB_CATEGORIES,
)

mcp = FastMCP(
    "worklog-mcp",
    instructions="MCP server for structured access to the shared worklog knowledge base. "
    "Use query_table for flexible queries, search_knowledge for full-text search, "
    "recall_context at task start to load relevant context, store_memory for facts, "
    "and log_entry for work tracking.",
)


async def get_db() -> aiosqlite.Connection:
    """Get database connection with row factory."""
    db_path = get_database_path()
    db = await aiosqlite.connect(str(db_path))
    db.row_factory = aiosqlite.Row
    return db


# =============================================================================
# QUERY TOOLS
# =============================================================================


@mcp.tool()
async def query_table(
    table: str,
    columns: str = "*",
    where: Optional[str] = None,
    order_by: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """Query any table in the worklog database with filtering and pagination.

    Args:
        table: Table name (memories, knowledge_base, entries, research)
        columns: Comma-separated column names or * for all
        where: SQL WHERE clause (without 'WHERE' keyword), e.g. "status='promoted'"
        order_by: Column to order by, e.g. "created_at DESC"
        limit: Maximum rows to return (default 20, max 100)
        offset: Number of rows to skip for pagination

    Returns:
        dict with 'rows' list and 'count' of total matching rows
    """
    if table not in TABLES:
        return {"error": f"Invalid table. Must be one of: {TABLES}"}

    limit = min(limit, 100)

    # Build query
    query = f"SELECT {columns} FROM {table}"
    count_query = f"SELECT COUNT(*) as total FROM {table}"

    if where:
        query += f" WHERE {where}"
        count_query += f" WHERE {where}"

    if order_by:
        query += f" ORDER BY {order_by}"

    query += f" LIMIT {limit} OFFSET {offset}"

    async with await get_db() as db:
        # Get total count
        async with db.execute(count_query) as cursor:
            count_row = await cursor.fetchone()
            total = count_row["total"] if count_row else 0

        # Get rows
        async with db.execute(query) as cursor:
            rows = await cursor.fetchall()
            results = [dict(row) for row in rows]

    return {
        "rows": results,
        "count": len(results),
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

    async with await get_db() as db:
        for table in search_tables:
            # Build search based on table schema
            if table == "memories":
                sql = """
                    SELECT id, key, summary, memory_type, importance, tags, created_at
                    FROM memories
                    WHERE content LIKE ? OR summary LIKE ? OR key LIKE ? OR tags LIKE ?
                    ORDER BY importance DESC, created_at DESC
                    LIMIT ?
                """
            elif table == "knowledge_base":
                sql = """
                    SELECT id, category, title, tags, created_at, updated_at
                    FROM knowledge_base
                    WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? OR category LIKE ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                """
            elif table == "entries":
                sql = """
                    SELECT id, timestamp, agent, task_type, title, outcome, tags
                    FROM entries
                    WHERE title LIKE ? OR details LIKE ? OR outcome LIKE ? OR tags LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
            elif table == "research":
                sql = """
                    SELECT id, source_type, title, summary, relevance_score, tags, status
                    FROM research
                    WHERE title LIKE ? OR summary LIKE ? OR key_points LIKE ? OR tags LIKE ?
                    ORDER BY relevance_score DESC, created_at DESC
                    LIMIT ?
                """
            else:
                continue

            async with db.execute(sql, (search_term, search_term, search_term, search_term, limit)) as cursor:
                rows = await cursor.fetchall()
                results[table] = [dict(row) for row in rows]

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

    async with await get_db() as db:
        # Get relevant memories
        type_placeholders = ",".join(["?" for _ in types])
        memory_sql = f"""
            SELECT id, key, content, summary, memory_type, importance, tags, created_at
            FROM memories
            WHERE memory_type IN ({type_placeholders})
              AND importance >= ?
              AND status != 'archived'
              AND (content LIKE ? OR summary LIKE ? OR key LIKE ? OR tags LIKE ?)
            ORDER BY importance DESC, last_accessed DESC
            LIMIT ?
        """
        params = types + [min_importance, search_term, search_term, search_term, search_term, limit]

        async with db.execute(memory_sql, params) as cursor:
            rows = await cursor.fetchall()
            results["memories"] = [dict(row) for row in rows]

        # Get relevant knowledge base entries
        kb_sql = """
            SELECT id, category, title, content, tags, updated_at
            FROM knowledge_base
            WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
            ORDER BY updated_at DESC
            LIMIT ?
        """
        async with db.execute(kb_sql, (search_term, search_term, search_term, limit // 2)) as cursor:
            rows = await cursor.fetchall()
            results["knowledge"] = [dict(row) for row in rows]

        # Get recent work entries if requested
        if include_recent:
            recent_sql = """
                SELECT id, timestamp, agent, task_type, title, outcome, tags
                FROM entries
                WHERE timestamp > datetime('now', '-7 days')
                  AND (title LIKE ? OR tags LIKE ?)
                ORDER BY timestamp DESC
                LIMIT ?
            """
            async with db.execute(recent_sql, (search_term, search_term, limit // 2)) as cursor:
                rows = await cursor.fetchall()
                results["recent_work"] = [dict(row) for row in rows]

    return results


@mcp.tool()
async def get_knowledge_entry(id: int) -> dict:
    """Get a full knowledge base entry by ID.

    Args:
        id: The knowledge base entry ID

    Returns:
        Full entry with all fields
    """
    async with await get_db() as db:
        async with db.execute(
            "SELECT * FROM knowledge_base WHERE id = ?", (id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"entry": dict(row)}
            return {"error": f"No knowledge base entry with id {id}"}


@mcp.tool()
async def get_memory(key: str) -> dict:
    """Get a memory by its unique key.

    Args:
        key: The memory key (e.g., 'ctx_jarvis_20251215_ssh-setup')

    Returns:
        Full memory with all fields
    """
    async with await get_db() as db:
        # Update access count and timestamp
        await db.execute(
            """UPDATE memories SET
               access_count = access_count + 1,
               last_accessed = CURRENT_TIMESTAMP
               WHERE key = ?""",
            (key,)
        )
        await db.commit()

        async with db.execute(
            "SELECT * FROM memories WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"memory": dict(row)}
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

    async with await get_db() as db:
        try:
            cursor = await db.execute(
                """INSERT INTO memories
                   (key, content, summary, memory_type, importance, tags, source_agent, system)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (key, content, summary, memory_type, importance, tags, source_agent, system)
            )
            await db.commit()
            return {
                "success": True,
                "id": cursor.lastrowid,
                "key": key,
            }
        except aiosqlite.IntegrityError:
            return {"error": f"Memory with key '{key}' already exists. Use update_memory instead."}


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

    updates = []
    params = []

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

    async with await get_db() as db:
        cursor = await db.execute(
            f"UPDATE memories SET {', '.join(updates)} WHERE key = ?",
            params
        )
        await db.commit()

        if cursor.rowcount == 0:
            return {"error": f"No memory found with key '{key}'"}

        return {"success": True, "key": key, "updated_fields": len(updates)}


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

    async with await get_db() as db:
        cursor = await db.execute(
            """INSERT INTO entries
               (agent, task_type, title, details, decision_rationale, outcome, tags, related_files)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (agent, task_type, title, details, decision_rationale, outcome, tags, related_files)
        )
        await db.commit()
        return {
            "success": True,
            "id": cursor.lastrowid,
            "title": title,
        }


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

    async with await get_db() as db:
        try:
            cursor = await db.execute(
                """INSERT INTO knowledge_base
                   (category, title, content, tags, source_agent, system, is_protocol)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (category, title, content, tags, source_agent, system, 1 if is_protocol else 0)
            )
            await db.commit()
            return {
                "success": True,
                "id": cursor.lastrowid,
                "title": title,
            }
        except aiosqlite.IntegrityError:
            return {"error": f"Knowledge entry with category '{category}' and title '{title}' already exists."}


# =============================================================================
# UTILITY TOOLS
# =============================================================================


@mcp.tool()
async def list_tables() -> dict:
    """List all available tables and their row counts.

    Returns:
        dict with table names and counts
    """
    async with await get_db() as db:
        tables = {}
        for table in TABLES:
            async with db.execute(f"SELECT COUNT(*) as count FROM {table}") as cursor:
                row = await cursor.fetchone()
                tables[table] = row["count"] if row else 0

    return {"tables": tables}


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
    async with await get_db() as db:
        if agent:
            sql = """
                SELECT id, timestamp, agent, task_type, title, outcome, tags
                FROM entries
                WHERE agent = ? AND timestamp > datetime('now', ?)
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params = (agent, f"-{days} days", limit)
        else:
            sql = """
                SELECT id, timestamp, agent, task_type, title, outcome, tags
                FROM entries
                WHERE timestamp > datetime('now', ?)
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params = (f"-{days} days", limit)

        async with db.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return {
                "entries": [dict(row) for row in rows],
                "count": len(rows),
                "days": days,
            }


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
