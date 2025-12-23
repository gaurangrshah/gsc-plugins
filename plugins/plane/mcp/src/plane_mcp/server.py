"""Plane MCP Server - Project management and knowledge base access.

Provides tools for interacting with Plane.so:
- Workspaces and projects
- Issues (tasks, bugs, features)
- Pages (knowledge base, documentation) - via direct DB access
- Cycles and modules
"""

from typing import Optional
from fastmcp import FastMCP

from plane_mcp.client import get_client
from plane_mcp.db_client import get_db_client

mcp = FastMCP(
    "plane-mcp",
    instructions="""MCP server for Plane.so project management.

Use list_workspaces to discover available workspaces.
Use list_projects to see projects in a workspace.
Use list_pages/get_page for knowledge base access.
Use list_issues/create_issue for task management.

Required: PLANE_API_URL and PLANE_API_KEY environment variables.
""",
)


# =============================================================================
# WORKSPACE TOOLS (Direct Database Access)
# =============================================================================
# Note: Workspace list is not exposed in Plane's public API.
# Uses direct PostgreSQL access instead.


@mcp.tool()
async def list_workspaces() -> dict:
    """List all accessible Plane workspaces.

    Uses direct database access since workspace list is not in public API.

    Returns:
        dict with 'results' containing workspace list with slug, name, etc.
    """
    db = await get_db_client()
    workspaces = await db.list_workspaces()
    return {"results": workspaces, "count": len(workspaces)}


# =============================================================================
# PROJECT TOOLS
# =============================================================================


@mcp.tool()
async def list_projects(workspace_slug: str) -> dict:
    """List all projects in a workspace.

    Args:
        workspace_slug: The workspace slug (e.g., 'my-workspace')

    Returns:
        dict with 'results' containing project list
    """
    client = await get_client()
    return await client.list_projects(workspace_slug)


@mcp.tool()
async def get_project(workspace_slug: str, project_id: str) -> dict:
    """Get details of a specific project.

    Args:
        workspace_slug: The workspace slug
        project_id: The project ID

    Returns:
        Project details including name, description, settings
    """
    client = await get_client()
    return await client.get_project(workspace_slug, project_id)


# =============================================================================
# ISSUE TOOLS
# =============================================================================


@mcp.tool()
async def list_issues(
    workspace_slug: str,
    project_id: str,
    state: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
) -> dict:
    """List issues in a project with optional filtering.

    Args:
        workspace_slug: The workspace slug
        project_id: The project ID
        state: Filter by state (e.g., 'backlog', 'in_progress', 'done')
        priority: Filter by priority ('urgent', 'high', 'medium', 'low', 'none')
        limit: Maximum number of issues to return

    Returns:
        dict with 'results' containing issue list
    """
    client = await get_client()
    params = {"per_page": limit}
    if state:
        params["state"] = state
    if priority:
        params["priority"] = priority
    return await client.list_issues(workspace_slug, project_id, params)


@mcp.tool()
async def get_issue(
    workspace_slug: str, project_id: str, issue_id: str
) -> dict:
    """Get details of a specific issue.

    Args:
        workspace_slug: The workspace slug
        project_id: The project ID
        issue_id: The issue ID

    Returns:
        Issue details including name, description, state, priority, assignees
    """
    client = await get_client()
    return await client.get_issue(workspace_slug, project_id, issue_id)


@mcp.tool()
async def create_issue(
    workspace_slug: str,
    project_id: str,
    name: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
) -> dict:
    """Create a new issue in a project.

    Args:
        workspace_slug: The workspace slug
        project_id: The project ID
        name: Issue title/name
        description: Issue description (plain text, will be converted to HTML)
        priority: Priority level ('urgent', 'high', 'medium', 'low', 'none')

    Returns:
        Created issue details
    """
    client = await get_client()
    return await client.create_issue(
        workspace_slug, project_id, name, description, priority
    )


@mcp.tool()
async def update_issue(
    workspace_slug: str,
    project_id: str,
    issue_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    state_id: Optional[str] = None,
) -> dict:
    """Update an existing issue.

    Args:
        workspace_slug: The workspace slug
        project_id: The project ID
        issue_id: The issue ID to update
        name: New issue title (optional)
        description: New description (optional)
        priority: New priority (optional)
        state_id: New state ID (optional)

    Returns:
        Updated issue details
    """
    client = await get_client()
    updates = {}
    if name:
        updates["name"] = name
    if description:
        updates["description_html"] = f"<p>{description}</p>"
    if priority:
        updates["priority"] = priority
    if state_id:
        updates["state"] = state_id

    if not updates:
        return {"error": "No updates provided"}

    return await client.update_issue(
        workspace_slug, project_id, issue_id, **updates
    )


# =============================================================================
# PAGE TOOLS (Knowledge Base) - Direct Database Access
# =============================================================================
# Note: Pages are not exposed in Plane's public API (/api/v1/).
# These tools use direct PostgreSQL access instead.
# See: ~/workspace/infra/tasks/003-plane-pages-api-access.md


async def _check_pages_enabled(
    workspace_slug: str, project_id: str
) -> dict | None:
    """Check if pages are enabled for a project.

    Returns None if enabled, or an error dict if disabled.
    """
    client = await get_client()
    project = await client.get_project(workspace_slug, project_id)
    if "error" in project:
        return project
    if not project.get("page_view", False):
        return {
            "error": "Pages are not enabled for this project",
            "hint": "Enable page_view in project settings first",
        }
    return None


@mcp.tool()
async def list_pages(
    workspace_slug: str,
    project_id: Optional[str] = None,
    limit: int = 50,
) -> dict:
    """List pages (knowledge base entries) in a workspace or project.

    Uses direct database access since Pages API is not in Plane public API.

    Args:
        workspace_slug: The workspace slug
        project_id: The project ID (optional - if omitted, lists all workspace pages)
        limit: Maximum number of pages to return

    Returns:
        dict with 'results' containing page list, or error if pages disabled
    """
    # Check if pages are enabled for this project (if project specified)
    if project_id:
        check = await _check_pages_enabled(workspace_slug, project_id)
        if check:
            return check

    db = await get_db_client()
    pages = await db.list_pages(workspace_slug, project_id, limit)
    return {"results": pages, "count": len(pages)}


@mcp.tool()
async def get_page(page_id: str) -> dict:
    """Get details of a specific page including content.

    Uses direct database access since Pages API is not in Plane public API.

    Args:
        page_id: The page ID (UUID)

    Returns:
        Page details including name, description_html content
    """
    db = await get_db_client()
    page = await db.get_page(page_id)
    if not page:
        return {"error": "Page not found"}
    return page


@mcp.tool()
async def create_page(
    workspace_slug: str,
    project_id: str,
    name: str,
    description: Optional[str] = None,
    parent_id: Optional[str] = None,
    external_id: Optional[str] = None,
    external_source: Optional[str] = None,
) -> dict:
    """Create a new page in a project's knowledge base.

    Uses direct database access since Pages API is not in Plane public API.

    Args:
        workspace_slug: The workspace slug
        project_id: The project ID
        name: Page title
        description: Page content (plain text or HTML)
        parent_id: Parent page ID for nested pages (optional)
        external_id: External reference ID for sync (optional)
        external_source: External source name, e.g. 'gitea' (optional)

    Returns:
        Created page details
    """
    # Check if pages are enabled for this project
    check = await _check_pages_enabled(workspace_slug, project_id)
    if check:
        return check

    description_html = ""
    if description:
        # Wrap plain text in paragraph if not already HTML
        if not description.strip().startswith("<"):
            description_html = f"<p>{description}</p>"
        else:
            description_html = description

    db = await get_db_client()
    return await db.create_page(
        workspace_slug=workspace_slug,
        project_id=project_id,
        name=name,
        description_html=description_html,
        parent_id=parent_id,
        external_id=external_id,
        external_source=external_source,
    )


@mcp.tool()
async def update_page(
    page_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """Update an existing page.

    Uses direct database access since Pages API is not in Plane public API.

    Args:
        page_id: The page ID to update
        name: New page title (optional)
        description: New content (optional, plain text or HTML)

    Returns:
        Updated page details
    """
    description_html = None
    if description:
        # Wrap plain text in paragraph if not already HTML
        if not description.strip().startswith("<"):
            description_html = f"<p>{description}</p>"
        else:
            description_html = description

    db = await get_db_client()
    return await db.update_page(page_id, name, description_html)


@mcp.tool()
async def delete_page(page_id: str) -> dict:
    """Delete a page (soft delete).

    Uses direct database access since Pages API is not in Plane public API.

    Args:
        page_id: The page ID to delete

    Returns:
        Success status
    """
    db = await get_db_client()
    return await db.delete_page(page_id)


# =============================================================================
# CYCLE & MODULE TOOLS
# =============================================================================


@mcp.tool()
async def list_cycles(workspace_slug: str, project_id: str) -> dict:
    """List cycles (sprints) in a project.

    Args:
        workspace_slug: The workspace slug
        project_id: The project ID

    Returns:
        dict with 'results' containing cycle list
    """
    client = await get_client()
    return await client.list_cycles(workspace_slug, project_id)


@mcp.tool()
async def list_modules(workspace_slug: str, project_id: str) -> dict:
    """List modules (feature groups) in a project.

    Args:
        workspace_slug: The workspace slug
        project_id: The project ID

    Returns:
        dict with 'results' containing module list
    """
    client = await get_client()
    return await client.list_modules(workspace_slug, project_id)


# =============================================================================
# ENTRY POINT
# =============================================================================


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
