# Plane MCP Server

MCP (Model Context Protocol) server for [Plane.so](https://plane.so/) project management integration with Claude Code.

## Features

Provides **14 tools** for interacting with Plane:

| Tool | Access | Description |
|------|--------|-------------|
| `list_workspaces` | DB | List all accessible workspaces |
| `list_projects` | API | List projects in a workspace |
| `get_project` | API | Get project details |
| `list_issues` | API | List issues with filtering |
| `get_issue` | API | Get issue details |
| `create_issue` | API | Create new issue |
| `update_issue` | API | Update existing issue |
| `list_pages` | DB | List knowledge base pages |
| `get_page` | DB | Get page content |
| `create_page` | DB | Create new page |
| `update_page` | DB | Update page content |
| `delete_page` | DB | Soft-delete a page |
| `list_cycles` | API | List sprints/cycles |
| `list_modules` | API | List feature modules |

## Why Two Access Methods?

Plane's public API (`/api/v1/`) uses API key authentication but **does not expose all features**:

| Feature | Public API | This MCP |
|---------|------------|----------|
| Projects | Yes | API |
| Issues | Yes | API |
| Cycles | Yes | API |
| Modules | Yes | API |
| **Pages** | **No** | Direct DB |
| **Workspaces list** | **No** | Direct DB |

This MCP uses direct PostgreSQL access via SSH for Pages and Workspaces.

## Installation

### 1. Create Virtual Environment

```bash
cd /volume2/dev-env/workspace/gsc-plugins/plugins/plane/mcp
python3 -m venv .venv
.venv/bin/pip install fastmcp httpx
```

### 2. Configure Claude Code

Add to project MCP config (`~/.claude.json`):

```json
{
  "projects": {
    "/home/gs": {
      "mcpServers": {
        "plane": {
          "type": "stdio",
          "command": "python",
          "args": ["-m", "plane_mcp"],
          "cwd": "/volume2/dev-env/workspace/gsc-plugins/plugins/plane/mcp",
          "env": {
            "PYTHONPATH": "/volume2/dev-env/workspace/gsc-plugins/plugins/plane/mcp/src",
            "PLANE_API_URL": "http://192.168.1.199:3080",
            "PLANE_API_KEY": "plane_api_xxx",
            "PLANE_WORKSPACE_SLUG": "gsdev",
            "PLANE_DB_SSH_HOST": "ubuntu-mini",
            "PLANE_DB_CONTAINER": "plane-app-plane-db-1",
            "PLANE_DB_USER": "plane",
            "PLANE_DB_PASSWORD": "xxx",
            "PLANE_DB_NAME": "plane"
          }
        }
      }
    }
  }
}
```

### 3. Get Credentials

**API Key:**
1. Log into Plane web UI
2. Profile Settings → Personal Access Tokens
3. Add token, copy `plane_api_xxxxx`
4. Stored in: Bitwarden → Infra folder

**DB Password:**
```bash
ssh ubuntu-mini "docker exec plane-app-api-1 env | grep POSTGRES_PASSWORD"
```

## Environment Variables

### API Access
| Variable | Required | Description |
|----------|----------|-------------|
| `PLANE_API_URL` | Yes | Plane instance URL |
| `PLANE_API_KEY` | Yes | API key from settings |
| `PLANE_WORKSPACE_SLUG` | No | Default workspace |

### Database Access (for Pages)
| Variable | Required | Description |
|----------|----------|-------------|
| `PLANE_DB_SSH_HOST` | Yes | SSH host with Docker |
| `PLANE_DB_CONTAINER` | Yes | PostgreSQL container name |
| `PLANE_DB_USER` | Yes | Database username |
| `PLANE_DB_PASSWORD` | Yes | Database password |
| `PLANE_DB_NAME` | Yes | Database name |

## Tool Reference

### Workspace Tools

```python
# List all workspaces (via DB)
list_workspaces()
# Returns: {"results": [{"id": "uuid", "slug": "gsdev", "name": "gsdev"}], "count": 1}
```

### Project Tools

```python
# List projects
list_projects(workspace_slug="gsdev")
# Returns: {"results": [...], "total_count": 2}

# Get project details
get_project(workspace_slug="gsdev", project_id="uuid")
# Returns: {"id": "uuid", "name": "infa", "page_view": true, ...}
```

### Issue Tools

```python
# List issues with filtering
list_issues(workspace_slug="gsdev", project_id="uuid",
            state="backlog", priority="high", limit=10)

# Create issue
create_issue(workspace_slug="gsdev", project_id="uuid",
             name="Bug: Login fails",
             description="Users cannot login after password reset",
             priority="high")  # urgent, high, medium, low, none

# Get issue
get_issue(workspace_slug="gsdev", project_id="uuid", issue_id="uuid")

# Update issue
update_issue(workspace_slug="gsdev", project_id="uuid", issue_id="uuid",
             name="Bug: Login fails (Fixed)",
             priority="medium",
             state_id="completed-state-uuid")
```

### Page Tools (Knowledge Base)

```python
# List all workspace pages
list_pages(workspace_slug="gsdev")

# List project-specific pages
list_pages(workspace_slug="gsdev", project_id="uuid")
# Returns: {"results": [{"id": "uuid", "name": "API Docs", ...}], "count": 5}

# Get page with full content
get_page(page_id="uuid")
# Returns: {"id": "uuid", "name": "API Docs", "description_html": "<h1>...</h1>", ...}

# Create page
create_page(workspace_slug="gsdev", project_id="uuid",
            name="Architecture Guide",
            description="<h1>System Architecture</h1><p>Overview...</p>",
            external_source="claude-mcp")  # Optional: for sync tracking

# Update page
update_page(page_id="uuid",
            name="Architecture Guide v2",
            description="<h1>Updated Content</h1>")

# Delete page (soft delete)
delete_page(page_id="uuid")
# Returns: {"success": true, "deleted_id": "uuid"}
```

### Cycle & Module Tools

```python
# List sprints/cycles
list_cycles(workspace_slug="gsdev", project_id="uuid")

# List feature modules
list_modules(workspace_slug="gsdev", project_id="uuid")
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code (atlas NAS)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Plane MCP Server                   │   │
│  │                                                       │   │
│  │  ┌─────────────────┐    ┌─────────────────────────┐  │   │
│  │  │   API Client    │    │     DB Client           │  │   │
│  │  │   (httpx)       │    │ (SSH + docker exec)     │  │   │
│  │  └────────┬────────┘    └───────────┬─────────────┘  │   │
│  └───────────┼─────────────────────────┼────────────────┘   │
└──────────────┼─────────────────────────┼────────────────────┘
               │                         │
               │ HTTP                    │ SSH
               ▼                         ▼
┌──────────────────────────────────────────────────────────────┐
│                     ubuntu-mini (Docker host)                 │
│                                                               │
│  ┌─────────────────────┐    ┌─────────────────────────────┐  │
│  │   plane-app-api-1   │    │   plane-app-plane-db-1      │  │
│  │   (HTTP :3080)      │    │   (PostgreSQL :5432)        │  │
│  │                     │    │                             │  │
│  │   /api/v1/...       │    │   pages, project_pages,     │  │
│  │   - projects ✓      │    │   workspaces tables         │  │
│  │   - issues ✓        │    │                             │  │
│  │   - cycles ✓        │    │                             │  │
│  │   - modules ✓       │    │                             │  │
│  │   - pages ✗         │    │                             │  │
│  └─────────────────────┘    └─────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Database Schema (Pages)

```sql
-- Main pages table
pages (
  id UUID PRIMARY KEY,
  name TEXT,
  description_html TEXT,
  description_stripped TEXT,
  workspace_id UUID,
  owned_by_id UUID,
  parent_id UUID,          -- For nested pages
  external_id VARCHAR,     -- For sync tracking
  external_source VARCHAR, -- e.g., "gitea", "claude-mcp"
  access SMALLINT,
  is_locked BOOLEAN,
  deleted_at TIMESTAMP     -- Soft delete
)

-- Link pages to projects (many-to-many)
project_pages (
  page_id UUID,
  project_id UUID,
  workspace_id UUID
)
```

## Testing

```bash
cd /volume2/dev-env/workspace/gsc-plugins/plugins/plane/mcp
.venv/bin/python /tmp/plane-mcp-test-v2.py
```

Test results (2025-12-22):
- 15/15 tools tested
- All passing

## Limitations

1. **Pages not in public API** - Uses direct DB (may break with schema changes)
2. **Workspaces list not in public API** - Uses direct DB
3. **DB access requires SSH** - Must have SSH access to Docker host
4. **No issue deletion** - Plane API doesn't expose issue deletion
5. **Rate limit** - 60 requests/minute per API key

## Related

- [Plane API Docs](https://developers.plane.so/api-reference/introduction)
- [Task 003: Pages API Blocker](~/workspace/infra/tasks/003-plane-pages-api-access.md)
- Plane instance: http://192.168.1.199:3080 (ubuntu-mini, Coolify)

---
*Created: 2025-12-22 | Updated: 2025-12-22*
