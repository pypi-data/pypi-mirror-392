"""API client for agent operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from sdk.generated.api_config import APIConfig
from sdk.generated.models.Agent import Agent

# Import generated service functions
from sdk.generated.services.async_Agent_Management_service import (  # pyright: ignore[reportMissingImports]  # noqa: F401
    listAgents,
)


class AgentsAPIClient:
    """API client for agent operations using generated OpenAPI client.

    This client uses generated service functions directly instead of the adapter
    pattern to reduce indirection and improve type safety.
    """

    def __init__(
        self,
        base_url: str | None = None,
        auth_token: str | None = None,
        api_key: str | None = None,
    ):
        """Initialize with API configuration.

        Args:
            base_url: Base URL for the API
            auth_token: Optional JWT auth token
            api_key: Optional API key
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.api_key = api_key

    @classmethod
    def from_config(cls) -> "AgentsAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            AgentsAPIClient instance
        """
        from cli.config import get_effective_api_config

        api_config = get_effective_api_config()
        return cls(
            base_url=api_config.get("api_url"),
            auth_token=api_config.get("auth_token"),
            api_key=api_config.get("api_key"),
        )

    def _get_api_config(self) -> APIConfig:
        """Get APIConfig for generated client calls.

        When using API keys, we pass a placeholder token since the actual
        authentication happens via the X-API-Key header.
        """
        if not self.base_url:
            raise ValueError(
                "API base URL not configured. "
                "Run 'anyt env add' to configure an environment."
            )
        # Use auth_token if available, otherwise use placeholder for API keys
        token = self.auth_token if self.auth_token else "agent_auth"
        return APIConfig(base_path=self.base_url, access_token=token)

    def _is_authenticated(self) -> bool:
        """Check if client has valid authentication credentials.

        Returns:
            True if auth_token or api_key is configured
        """
        return bool(self.auth_token or self.api_key)

    async def list_agents(self, workspace_id: int) -> list[Agent]:
        """List all agents in a workspace.

        Args:
            workspace_id: ID of the workspace

        Returns:
            List of agents

        Raises:
            HTTPException: If the API request fails
        """
        api_config = self._get_api_config()

        agents = await listAgents(
            api_config_override=api_config,
            workspace_id=workspace_id,
            X_API_Key=self.api_key,
        )

        return agents
