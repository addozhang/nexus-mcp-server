"""Authentication and credential handling for Nexus MCP Server."""

from typing import Annotated

from pydantic import BaseModel, Field

from nexus_mcp.nexus_client import NexusClient, NexusCredentials


class NexusConnectionParams(BaseModel):
    """Parameters for connecting to a Nexus instance.

    These can be passed as tool parameters or extracted from request context.
    """

    nexus_url: Annotated[
        str,
        Field(description="Base URL of the Nexus instance (e.g., https://nexus.example.com)"),
    ]
    nexus_username: Annotated[
        str,
        Field(description="Username for Nexus authentication"),
    ]
    nexus_password: Annotated[
        str,
        Field(description="Password for Nexus authentication"),
    ]

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


# Type alias for use in tool function signatures
NexusUrl = Annotated[
    str,
    Field(description="Base URL of the Nexus instance (e.g., https://nexus.example.com)"),
]
NexusUsername = Annotated[
    str,
    Field(description="Username for Nexus authentication"),
]
NexusPassword = Annotated[
    str,
    Field(description="Password for Nexus authentication"),
]
