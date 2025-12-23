"""Direct PostgreSQL database client for Plane pages.

Provides direct database access for pages since they're not exposed
in the public API (/api/v1/). Uses SSH + docker exec to reach the
containerized PostgreSQL since it's not exposed externally.

Schema reference (from Plane database):
- pages: id, name, description, description_html, workspace_id, owned_by_id, etc.
- project_pages: Links pages to projects (page_id, project_id, workspace_id)
"""

import asyncio
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

# Import config to trigger .env loading
from plane_mcp.config import _load_dotenv
_load_dotenv()  # Ensure env is loaded


@dataclass
class PlaneDBConfig:
    """Database configuration for Plane PostgreSQL via SSH/Docker."""

    ssh_host: str
    container_name: str
    db_user: str
    db_password: str
    db_name: str

    @classmethod
    def from_env(cls) -> "PlaneDBConfig":
        """Load config from environment variables."""
        return cls(
            ssh_host=os.getenv("PLANE_DB_SSH_HOST", "ubuntu-mini"),
            container_name=os.getenv("PLANE_DB_CONTAINER", "plane-app-plane-db-1"),
            db_user=os.getenv("PLANE_DB_USER", "plane"),
            db_password=os.getenv("PLANE_DB_PASSWORD", ""),
            db_name=os.getenv("PLANE_DB_NAME", "plane"),
        )


class PlaneDBClient:
    """Direct database client for Plane pages via SSH/Docker."""

    def __init__(self, config: PlaneDBConfig):
        self.config = config

    async def _run_query(self, query: str) -> str:
        """Run a SQL query via SSH + docker exec + psql.

        Returns raw output as string.
        """
        # Use base64 encoding to avoid shell escaping issues
        import base64
        query_b64 = base64.b64encode(query.encode()).decode()

        # Build command that decodes and executes
        cmd = [
            "ssh", self.config.ssh_host,
            f"echo {query_b64} | base64 -d | "
            f"docker exec -i -e PGPASSWORD='{self.config.db_password}' "
            f"{self.config.container_name} "
            f"psql -U {self.config.db_user} -d {self.config.db_name} -t -A"
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode().strip() if stderr else "Unknown error"
            raise RuntimeError(f"Database query failed: {error_msg}")

        return stdout.decode().strip()

    async def _run_query_json(self, query: str) -> list[dict]:
        """Run a SQL query and return results as JSON.

        Wraps the query in row_to_json for structured output.
        """
        json_query = f"SELECT json_agg(t) FROM ({query}) t"
        result = await self._run_query(json_query)

        if not result or result == "null":
            return []

        return json.loads(result)

    async def _run_insert(self, query: str) -> Optional[str]:
        """Run an INSERT query and return the inserted ID."""
        result = await self._run_query(query)
        return result.strip() if result else None

    # =========================================================================
    # WORKSPACE TOOLS
    # =========================================================================

    async def list_workspaces(self) -> list[dict]:
        """List all workspaces."""
        query = """
            SELECT id::text, slug, name, created_at, updated_at
            FROM workspaces
            WHERE deleted_at IS NULL
            ORDER BY name
        """
        return await self._run_query_json(query)

    async def get_workspace_id(self, workspace_slug: str) -> Optional[str]:
        """Get workspace UUID by slug."""
        query = f"SELECT id::text FROM workspaces WHERE slug = '{workspace_slug}' AND deleted_at IS NULL"
        result = await self._run_query(query)
        return result if result else None

    async def get_user_id(self, workspace_slug: str) -> Optional[str]:
        """Get first user ID in workspace (for owned_by)."""
        query = f"""
            SELECT u.id::text FROM users u
            JOIN workspace_members wm ON u.id = wm.member_id
            JOIN workspaces w ON wm.workspace_id = w.id
            WHERE w.slug = '{workspace_slug}' AND w.deleted_at IS NULL
            LIMIT 1
        """
        result = await self._run_query(query)
        return result if result else None

    # =========================================================================
    # PAGE READ OPERATIONS
    # =========================================================================

    async def list_pages(
        self,
        workspace_slug: str,
        project_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """List pages in a workspace, optionally filtered by project."""
        if project_id:
            query = f"""
                SELECT p.id::text, p.name, p.description_stripped,
                       p.access, p.is_locked, p.is_global, p.parent_id::text,
                       p.created_at, p.updated_at, p.archived_at,
                       p.external_id, p.external_source,
                       pr.id::text as project_id, pr.name as project_name
                FROM pages p
                JOIN project_pages pp ON p.id = pp.page_id
                JOIN projects pr ON pp.project_id = pr.id
                JOIN workspaces w ON p.workspace_id = w.id
                WHERE w.slug = '{workspace_slug}'
                  AND pr.id = '{project_id}'
                  AND p.deleted_at IS NULL
                  AND pp.deleted_at IS NULL
                ORDER BY p.updated_at DESC
                LIMIT {limit}
            """
        else:
            query = f"""
                SELECT p.id::text, p.name, p.description_stripped,
                       p.access, p.is_locked, p.is_global, p.parent_id::text,
                       p.created_at, p.updated_at, p.archived_at,
                       p.external_id, p.external_source
                FROM pages p
                JOIN workspaces w ON p.workspace_id = w.id
                WHERE w.slug = '{workspace_slug}' AND p.deleted_at IS NULL
                ORDER BY p.updated_at DESC
                LIMIT {limit}
            """

        return await self._run_query_json(query)

    async def get_page(self, page_id: str) -> Optional[dict]:
        """Get a specific page by ID with full content."""
        query = f"""
            SELECT p.id::text, p.name, p.description_html,
                   p.description_stripped, p.access, p.is_locked, p.is_global,
                   p.parent_id::text, p.created_at, p.updated_at, p.archived_at,
                   p.external_id, p.external_source, p.workspace_id::text,
                   w.slug as workspace_slug
            FROM pages p
            JOIN workspaces w ON p.workspace_id = w.id
            WHERE p.id = '{page_id}' AND p.deleted_at IS NULL
        """
        results = await self._run_query_json(query)
        return results[0] if results else None

    # =========================================================================
    # PAGE WRITE OPERATIONS
    # =========================================================================

    async def create_page(
        self,
        workspace_slug: str,
        project_id: str,
        name: str,
        description_html: str = "",
        parent_id: Optional[str] = None,
        external_id: Optional[str] = None,
        external_source: Optional[str] = None,
    ) -> dict:
        """Create a new page and link it to a project."""
        # Get workspace ID and user ID
        workspace_id = await self.get_workspace_id(workspace_slug)
        if not workspace_id:
            return {"error": f"Workspace '{workspace_slug}' not found"}

        user_id = await self.get_user_id(workspace_slug)
        if not user_id:
            return {"error": f"No user found in workspace '{workspace_slug}'"}

        now = datetime.now(timezone.utc).isoformat()
        page_id = str(uuid.uuid4())
        project_page_id = str(uuid.uuid4())

        # Strip HTML for plain text version
        description_stripped = self._strip_html(description_html)

        # Escape strings for SQL
        name_escaped = name.replace("'", "''")
        desc_html_escaped = description_html.replace("'", "''")
        desc_stripped_escaped = description_stripped.replace("'", "''")

        parent_clause = f"'{parent_id}'" if parent_id else "NULL"
        ext_id_clause = f"'{external_id}'" if external_id else "NULL"
        ext_src_clause = f"'{external_source}'" if external_source else "NULL"

        # Create the page
        insert_page = f"""
            INSERT INTO pages (
                id, name, description, description_html, description_stripped,
                access, is_locked, is_global, workspace_id, owned_by_id,
                created_by_id, updated_by_id, parent_id,
                external_id, external_source,
                color, view_props, logo_props, sort_order,
                created_at, updated_at
            ) VALUES (
                '{page_id}', '{name_escaped}', '{{}}'::jsonb, '{desc_html_escaped}', '{desc_stripped_escaped}',
                0, false, false, '{workspace_id}', '{user_id}',
                '{user_id}', '{user_id}', {parent_clause},
                {ext_id_clause}, {ext_src_clause},
                '', '{{}}'::jsonb, '{{}}'::jsonb, 65535,
                '{now}', '{now}'
            )
        """
        await self._run_query(insert_page)

        # Link page to project
        insert_link = f"""
            INSERT INTO project_pages (
                id, page_id, project_id, workspace_id,
                created_by_id, updated_by_id, created_at, updated_at
            ) VALUES (
                '{project_page_id}', '{page_id}', '{project_id}', '{workspace_id}',
                '{user_id}', '{user_id}', '{now}', '{now}'
            )
        """
        await self._run_query(insert_link)

        return await self.get_page(page_id)

    async def update_page(
        self,
        page_id: str,
        name: Optional[str] = None,
        description_html: Optional[str] = None,
    ) -> dict:
        """Update an existing page."""
        updates = []
        now = datetime.now(timezone.utc).isoformat()

        if name:
            name_escaped = name.replace("'", "''")
            updates.append(f"name = '{name_escaped}'")

        if description_html is not None:
            desc_html_escaped = description_html.replace("'", "''")
            desc_stripped = self._strip_html(description_html).replace("'", "''")
            updates.append(f"description_html = '{desc_html_escaped}'")
            updates.append(f"description_stripped = '{desc_stripped}'")

        if not updates:
            return {"error": "No updates provided"}

        updates.append(f"updated_at = '{now}'")

        query = f"UPDATE pages SET {', '.join(updates)} WHERE id = '{page_id}' AND deleted_at IS NULL"
        await self._run_query(query)

        return await self.get_page(page_id)

    async def delete_page(self, page_id: str) -> dict:
        """Soft-delete a page."""
        now = datetime.now(timezone.utc).isoformat()

        await self._run_query(
            f"UPDATE pages SET deleted_at = '{now}' WHERE id = '{page_id}' AND deleted_at IS NULL"
        )

        await self._run_query(
            f"UPDATE project_pages SET deleted_at = '{now}' WHERE page_id = '{page_id}' AND deleted_at IS NULL"
        )

        return {"success": True, "deleted_id": page_id}

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _strip_html(self, html: str) -> str:
        """Simple HTML tag stripping."""
        import re
        clean = re.sub(r'<[^>]+>', '', html)
        return clean.strip()


# Singleton pattern for client instance
_db_client: Optional[PlaneDBClient] = None


async def get_db_client() -> PlaneDBClient:
    """Get or create the database client singleton."""
    global _db_client
    if _db_client is None:
        config = PlaneDBConfig.from_env()
        _db_client = PlaneDBClient(config)
    return _db_client
