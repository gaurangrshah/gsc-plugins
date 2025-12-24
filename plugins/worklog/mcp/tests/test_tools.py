"""Tests for worklog-mcp tools."""

import pytest
from worklog_mcp.config import get_sqlite_path, TABLES, MEMORY_TYPES
from worklog_mcp.server import _validate_columns, _validate_order_by, TABLE_COLUMNS


def test_database_path_exists():
    """Test that we can find the database path (not necessarily existing)."""
    path = get_sqlite_path()
    # Just verify we get a valid path object
    assert path is not None
    assert str(path).endswith("worklog.db")


def test_tables_defined():
    """Test that all expected tables are defined."""
    expected = ["memories", "knowledge_base", "entries", "research", "agent_chat",
                "issues", "error_patterns"]
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


# =============================================================================
# SECURITY VALIDATION TESTS
# =============================================================================


def test_validate_columns_star():
    """Test that * is accepted for all columns."""
    valid, result = _validate_columns("*", "memories")
    assert valid is True
    assert result == "*"


def test_validate_columns_valid():
    """Test that valid columns are accepted."""
    valid, result = _validate_columns("id, key, content", "memories")
    assert valid is True
    assert result == "id, key, content"


def test_validate_columns_invalid():
    """Test that invalid columns are rejected."""
    valid, result = _validate_columns("id, evil_column", "memories")
    assert valid is False
    assert "Invalid columns" in result
    assert "evil_column" in result


def test_validate_columns_sql_injection():
    """Test that SQL injection attempts are rejected."""
    # Try to inject SQL via column name
    valid, result = _validate_columns("id; DROP TABLE memories;--", "memories")
    assert valid is False
    assert "Invalid columns" in result


def test_validate_order_by_valid():
    """Test that valid order_by is accepted."""
    valid, result = _validate_order_by("created_at DESC", "memories")
    assert valid is True
    assert result == "created_at DESC"


def test_validate_order_by_valid_asc():
    """Test that ASC direction is accepted."""
    valid, result = _validate_order_by("id ASC", "memories")
    assert valid is True
    assert result == "id ASC"


def test_validate_order_by_column_only():
    """Test that column without direction defaults to ASC."""
    valid, result = _validate_order_by("importance", "memories")
    assert valid is True
    assert result == "importance ASC"


def test_validate_order_by_invalid_column():
    """Test that invalid columns are rejected."""
    valid, result = _validate_order_by("evil_column DESC", "memories")
    assert valid is False
    assert "Invalid order_by column" in result


def test_validate_order_by_invalid_direction():
    """Test that invalid directions are rejected."""
    valid, result = _validate_order_by("id EVIL", "memories")
    assert valid is False
    assert "Invalid sort direction" in result


def test_validate_order_by_sql_injection():
    """Test that SQL injection via order_by is rejected."""
    valid, result = _validate_order_by("id; DROP TABLE memories;--", "memories")
    assert valid is False


def test_table_columns_defined():
    """Test that column whitelists are defined for all tables."""
    for table in TABLES:
        assert table in TABLE_COLUMNS, f"Missing column whitelist for {table}"
        assert len(TABLE_COLUMNS[table]) > 0, f"Empty column whitelist for {table}"


@pytest.mark.asyncio
async def test_query_table_with_filter():
    """Test query_table with parameterized filter."""
    from worklog_mcp.server import query_table

    try:
        result = await query_table.fn(
            table="memories",
            filter_column="status",
            filter_op="=",
            filter_value="promoted",
            limit=5
        )
        assert "rows" in result
        assert "error" not in result
    except FileNotFoundError:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_query_table_invalid_filter_column():
    """Test that invalid filter columns are rejected."""
    from worklog_mcp.server import query_table

    result = await query_table.fn(
        table="memories",
        filter_column="evil_column",
        filter_op="=",
        filter_value="test"
    )
    assert "error" in result
    assert "Invalid filter_column" in result["error"]


@pytest.mark.asyncio
async def test_query_table_invalid_filter_op():
    """Test that invalid filter operators are rejected."""
    from worklog_mcp.server import query_table

    result = await query_table.fn(
        table="memories",
        filter_column="status",
        filter_op="EVIL",
        filter_value="test"
    )
    assert "error" in result
    assert "Invalid filter_op" in result["error"]
