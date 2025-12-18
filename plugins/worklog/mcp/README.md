# worklog-mcp

MCP server providing programmatic access to the worklog database.

## Overview

This MCP server complements the worklog plugin's skills and commands by providing direct tool access for automated workflows and agent-to-agent communication.

## When to Use

| Approach | Use Case |
|----------|----------|
| **Skills** (`memory-store`, `memory-recall`) | Human-guided workflows with context and validation |
| **Commands** (`/worklog-*`) | Configuration and status |
| **MCP Tools** | Programmatic access, automation, agent tasks |

## Installation

The MCP server is automatically available when the worklog plugin is enabled.

### Manual Installation (Development)

```bash
cd plugins/worklog/mcp
pip install -e ".[dev]"
```

## Tools

### Query Tools
| Tool | Description |
|------|-------------|
| `query_table` | Query any table with filtering, pagination |
| `search_knowledge` | Full-text search across tables |
| `recall_context` | Smart context retrieval for agent sessions |
| `get_knowledge_entry` | Get KB entry by ID |
| `get_memory` | Get memory by key |

### Storage Tools
| Tool | Description |
|------|-------------|
| `store_memory` | Store new memories |
| `update_memory` | Update existing memories |
| `log_entry` | Log work entries |
| `store_knowledge` | Add to knowledge base |

### Utility Tools
| Tool | Description |
|------|-------------|
| `list_tables` | List tables with counts |
| `get_recent_entries` | Recent work by agent |

## Configuration

Database path auto-detected by hostname, or set via environment:

```bash
export WORKLOG_DB=/path/to/worklog.db
```

## Development

```bash
# Run server directly
python -m worklog_mcp

# Test with MCP Inspector
mcp-inspector python -m worklog_mcp

# Run tests
pytest -v
```

## Integration with Skills

Skills can optionally use MCP tools instead of raw SQL:

```markdown
# Instead of direct SQL in skills:
sqlite3 $WORKLOG_DB "INSERT INTO memories..."

# Skills could call:
mcp__worklog__store_memory(key="...", content="...")
```

This provides validation and consistent behavior across all access methods.
