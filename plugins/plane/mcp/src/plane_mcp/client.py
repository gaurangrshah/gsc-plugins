"""Plane API client for MCP server."""

from typing import Any, Optional
import httpx

from plane_mcp.config import PlaneConfig, ENDPOINTS


class PlaneClient:
    """Async HTTP client for Plane API."""

    def __init__(self, config: PlaneConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.api_url,
                headers={
                    "X-API-Key": self.config.api_key,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _build_url(self, endpoint: str, **kwargs) -> str:
        """Build URL from endpoint template and parameters."""
        template = ENDPOINTS.get(endpoint, endpoint)
        return template.format(**kwargs)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        **url_kwargs,
    ) -> dict[str, Any]:
        """Make an API request."""
        client = await self._get_client()
        url = self._build_url(endpoint, **url_kwargs)

        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "status_code": e.response.status_code,
            }
        except httpx.RequestError as e:
            return {"error": f"Request failed: {str(e)}"}

    # =========================================================================
    # Workspace Operations
    # =========================================================================

    async def list_workspaces(self) -> dict[str, Any]:
        """List all accessible workspaces."""
        return await self._request("GET", "workspaces")

    # =========================================================================
    # Project Operations
    # =========================================================================

    async def list_projects(self, workspace_slug: str) -> dict[str, Any]:
        """List projects in a workspace."""
        return await self._request(
            "GET", "projects", workspace_slug=workspace_slug
        )

    async def get_project(
        self, workspace_slug: str, project_id: str
    ) -> dict[str, Any]:
        """Get project details."""
        return await self._request(
            "GET", "project", workspace_slug=workspace_slug, project_id=project_id
        )

    # =========================================================================
    # Issue Operations
    # =========================================================================

    async def list_issues(
        self,
        workspace_slug: str,
        project_id: str,
        params: Optional[dict] = None,
    ) -> dict[str, Any]:
        """List issues in a project."""
        return await self._request(
            "GET",
            "issues",
            params=params,
            workspace_slug=workspace_slug,
            project_id=project_id,
        )

    async def get_issue(
        self, workspace_slug: str, project_id: str, issue_id: str
    ) -> dict[str, Any]:
        """Get issue details."""
        return await self._request(
            "GET",
            "issue",
            workspace_slug=workspace_slug,
            project_id=project_id,
            issue_id=issue_id,
        )

    async def create_issue(
        self,
        workspace_slug: str,
        project_id: str,
        name: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        state_id: Optional[str] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Create a new issue."""
        data = {"name": name}
        if description:
            data["description_html"] = f"<p>{description}</p>"
        if priority:
            data["priority"] = priority
        if state_id:
            data["state"] = state_id
        data.update(kwargs)

        return await self._request(
            "POST",
            "issues",
            json=data,
            workspace_slug=workspace_slug,
            project_id=project_id,
        )

    async def update_issue(
        self,
        workspace_slug: str,
        project_id: str,
        issue_id: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Update an issue."""
        return await self._request(
            "PATCH",
            "issue",
            json=kwargs,
            workspace_slug=workspace_slug,
            project_id=project_id,
            issue_id=issue_id,
        )

    # =========================================================================
    # Page Operations (Knowledge Base)
    # =========================================================================

    async def list_pages(
        self,
        workspace_slug: str,
        project_id: str,
        params: Optional[dict] = None,
    ) -> dict[str, Any]:
        """List pages in a project."""
        return await self._request(
            "GET",
            "pages",
            params=params,
            workspace_slug=workspace_slug,
            project_id=project_id,
        )

    async def get_page(
        self, workspace_slug: str, project_id: str, page_id: str
    ) -> dict[str, Any]:
        """Get page details."""
        return await self._request(
            "GET",
            "page",
            workspace_slug=workspace_slug,
            project_id=project_id,
            page_id=page_id,
        )

    async def create_page(
        self,
        workspace_slug: str,
        project_id: str,
        name: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Create a new page."""
        data = {"name": name}
        if description:
            data["description_html"] = f"<p>{description}</p>"
        data.update(kwargs)

        return await self._request(
            "POST",
            "pages",
            json=data,
            workspace_slug=workspace_slug,
            project_id=project_id,
        )

    async def update_page(
        self,
        workspace_slug: str,
        project_id: str,
        page_id: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Update a page."""
        return await self._request(
            "PATCH",
            "page",
            json=kwargs,
            workspace_slug=workspace_slug,
            project_id=project_id,
            page_id=page_id,
        )

    # =========================================================================
    # Cycle Operations
    # =========================================================================

    async def list_cycles(
        self, workspace_slug: str, project_id: str
    ) -> dict[str, Any]:
        """List cycles in a project."""
        return await self._request(
            "GET", "cycles", workspace_slug=workspace_slug, project_id=project_id
        )

    # =========================================================================
    # Module Operations
    # =========================================================================

    async def list_modules(
        self, workspace_slug: str, project_id: str
    ) -> dict[str, Any]:
        """List modules in a project."""
        return await self._request(
            "GET", "modules", workspace_slug=workspace_slug, project_id=project_id
        )


# Global client instance
_client: Optional[PlaneClient] = None


async def get_client() -> PlaneClient:
    """Get or create the global Plane client."""
    global _client
    if _client is None:
        from plane_mcp.config import get_config

        _client = PlaneClient(get_config())
    return _client
