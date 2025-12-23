"""Configuration for Plane MCP Server."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _load_dotenv():
    """Load .env file from MCP directory if it exists."""
    # Try to find .env relative to this file
    config_dir = Path(__file__).parent.parent.parent  # mcp/
    env_file = config_dir / ".env"

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = value


# Load .env on module import
_load_dotenv()


@dataclass
class PlaneConfig:
    """Plane API configuration."""

    api_url: str
    api_key: str
    workspace_slug: Optional[str] = None

    @classmethod
    def from_env(cls) -> "PlaneConfig":
        """Load configuration from environment variables."""
        api_url = os.getenv("PLANE_API_URL")
        api_key = os.getenv("PLANE_API_KEY")

        if not api_url:
            raise ValueError("PLANE_API_URL environment variable is required")
        if not api_key:
            raise ValueError("PLANE_API_KEY environment variable is required")

        # Normalize URL (remove trailing slash)
        api_url = api_url.rstrip("/")

        return cls(
            api_url=api_url,
            api_key=api_key,
            workspace_slug=os.getenv("PLANE_WORKSPACE_SLUG"),
        )


# API endpoints
ENDPOINTS = {
    "workspaces": "/api/v1/workspaces/",
    "projects": "/api/v1/workspaces/{workspace_slug}/projects/",
    "project": "/api/v1/workspaces/{workspace_slug}/projects/{project_id}/",
    "issues": "/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues/",
    "issue": "/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues/{issue_id}/",
    "pages": "/api/v1/workspaces/{workspace_slug}/projects/{project_id}/pages/",
    "page": "/api/v1/workspaces/{workspace_slug}/projects/{project_id}/pages/{page_id}/",
    "cycles": "/api/v1/workspaces/{workspace_slug}/projects/{project_id}/cycles/",
    "modules": "/api/v1/workspaces/{workspace_slug}/projects/{project_id}/modules/",
}


def get_config() -> PlaneConfig:
    """Get Plane configuration from environment."""
    return PlaneConfig.from_env()
