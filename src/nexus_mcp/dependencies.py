"""Dependency injection for Nexus MCP Server.

Provides credential extraction from HTTP headers using FastMCP's dependency system.
"""

from typing import cast
from urllib.parse import urlparse

from fastmcp.server.dependencies import get_http_request

from nexus_mcp.nexus_client import NexusCredentials


class MissingCredentialsError(Exception):
    """Raised when required Nexus credentials are missing from headers."""

    pass


class InvalidCredentialsError(Exception):
    """Raised when Nexus credentials are invalid."""

    pass


def get_nexus_credentials() -> NexusCredentials:
    """Extract Nexus credentials from HTTP request headers.

    This function uses FastMCP's dependency injection system to access
    the current HTTP request and extract credentials from headers.

    Headers (case-insensitive):
    - X-Nexus-Url: Base URL of the Nexus instance
    - X-Nexus-Username: Username for authentication
    - X-Nexus-Password: Password for authentication

    Returns:
        NexusCredentials with validated URL, username, and password.

    Raises:
        MissingCredentialsError: If any required header is missing.
        InvalidCredentialsError: If the URL is invalid.
    """
    request = get_http_request()
    headers = request.headers if request else {}

    # Extract headers (case-insensitive - Starlette headers are already lowercase)
    nexus_url: str | None = headers.get("x-nexus-url")
    nexus_username: str | None = headers.get("x-nexus-username")
    nexus_password: str | None = headers.get("x-nexus-password")

    # Check for missing headers
    missing: list[str] = []
    if not nexus_url:
        missing.append("X-Nexus-Url")
    if not nexus_username:
        missing.append("X-Nexus-Username")
    if not nexus_password:
        missing.append("X-Nexus-Password")

    if missing:
        raise MissingCredentialsError(
            f"Missing required Nexus credentials in headers: {', '.join(missing)}"
        )

    # At this point, we know all values are present (not None)
    # Cast to satisfy type checker after validation
    url = cast(str, nexus_url)
    username = cast(str, nexus_username)
    password = cast(str, nexus_password)

    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise InvalidCredentialsError(f"Invalid Nexus URL: {url}")
    if parsed.scheme not in ("http", "https"):
        raise InvalidCredentialsError(
            f"URL scheme must be http or https, got: {parsed.scheme}"
        )

    return NexusCredentials(
        url=url,
        username=username,
        password=password,
    )
