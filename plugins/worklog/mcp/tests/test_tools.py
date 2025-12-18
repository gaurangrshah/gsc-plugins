"""Tests for worklog-mcp tools."""

import pytest
from worklog_mcp.config import get_database_path, TABLES, MEMORY_TYPES


def test_database_path_exists():
    """Test that we can find the database."""
    try:
        path = get_database_path()
        assert path.exists(), f"Database not found at {path}"
    except FileNotFoundError as e:
        pytest.skip(f"Database not available: {e}")


def test_tables_defined():
    """Test that all expected tables are defined."""
    expected = ["memories", "knowledge_base", "entries", "research"]
    assert TABLES == expected


def test_memory_types_defined():
    """Test that memory types are defined."""
    expected = ["fact", "entity", "preference", "context"]
    assert MEMORY_TYPES == expected


@pytest.mark.asyncio
async def test_list_tables():
    """Test listing tables."""
    from worklog_mcp.server import list_tables

    try:
        # FastMCP wraps functions - call the underlying fn
        result = await list_tables.fn()
        assert "tables" in result
        for table in TABLES:
            assert table in result["tables"]
    except FileNotFoundError:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_query_table_invalid():
    """Test querying invalid table returns error."""
    from worklog_mcp.server import query_table

    result = await query_table.fn(table="invalid_table")
    assert "error" in result


@pytest.mark.asyncio
async def test_query_table_memories():
    """Test querying memories table."""
    from worklog_mcp.server import query_table

    try:
        result = await query_table.fn(table="memories", limit=5)
        assert "rows" in result
        assert "total" in result
        assert isinstance(result["rows"], list)
    except FileNotFoundError:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_search_knowledge():
    """Test searching across tables."""
    from worklog_mcp.server import search_knowledge

    try:
        result = await search_knowledge.fn(query="test", limit=5)
        assert "results" in result
        assert "tables_searched" in result
    except FileNotFoundError:
        pytest.skip("Database not available")
