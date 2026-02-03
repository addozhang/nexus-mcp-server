"""Authentication and credential handling for Nexus MCP Server."""

from pydantic import BaseModel, Field

from nexus_mcp.nexus_client import NexusClient, NexusCredentials


class NexusConnectionParams(BaseModel):
    """Parameters for connecting to a Nexus instance.

    These can be passed as tool parameters or extracted from request context.
    """

    nexus_url: str = Field(
        ...,
        description="Base URL of the Nexus instance (e.g., https://nexus.example.com)",
    )
    nexus_username: str = Field(
        ...,
        description="Username for Nexus authentication",
    )
    nexus_password: str = Field(
        ...,
        description="Password for Nexus authentication",
    )

    def to_credentials(self) -> NexusCredentials:
        """Convert to NexusCredentials for the client."""
        return NexusCredentials(
            url=self.nexus_url,
            username=self.nexus_username,
            password=self.nexus_password,
        )

    def create_client(self) -> NexusClient:
        """Create a NexusClient with these credentials."""
        return NexusClient(self.to_credentials())


# Re-export credential utilities from dependencies module
# These are the primary way to access credentials in tools
__all__ = [
    "NexusConnectionParams",
    "NexusCredentials",
    "NexusClient",
]
