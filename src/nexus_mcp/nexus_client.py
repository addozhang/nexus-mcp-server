"""Nexus Repository Manager REST API client."""

import logging
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class NexusError(Exception):
    """Base exception for Nexus API errors."""

    pass


class NexusAuthError(NexusError):
    """Authentication failed with Nexus."""

    pass


class NexusConnectionError(NexusError):
    """Failed to connect to Nexus."""

    pass


class NexusNotFoundError(NexusError):
    """Resource not found in Nexus."""

    pass


class NexusCredentials(BaseModel):
    """Credentials for connecting to a Nexus instance."""

    url: str = Field(..., description="Base URL of the Nexus instance")
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates (set to False for self-signed certs)")

    def validate_url(self) -> None:
        """Validate that the URL is properly formatted."""
        parsed = urlparse(self.url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid Nexus URL: {self.url}")
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"URL scheme must be http or https, got: {parsed.scheme}")


class SearchResult(BaseModel):
    """A single search result item."""

    id: str = Field(default="", description="Component ID")
    repository: str = Field(default="", description="Repository name")
    group: str | None = Field(default=None, description="Group ID (Maven)")
    name: str = Field(default="", description="Artifact/package name")
    version: str = Field(default="", description="Version string")
    format: str = Field(default="", description="Package format (maven2, pypi, docker)")
    assets: list[dict[str, Any]] = Field(default_factory=list, description="Asset details")


class SearchResponse(BaseModel):
    """Response from a search query."""

    items: list[SearchResult] = Field(default_factory=list)
    continuation_token: str | None = Field(default=None)


class NexusClient:
    """Async HTTP client for the Nexus Repository Manager REST API.

    Uses httpx.AsyncClient for all HTTP requests with HTTP Basic Auth.
    Credentials are not logged.
    """

    API_BASE = "/service/rest/v1"

    def __init__(self, credentials: NexusCredentials) -> None:
        """Initialize the client with credentials.

        Args:
            credentials: Nexus connection credentials.

        Raises:
            ValueError: If the URL is invalid.
        """
        credentials.validate_url()
        self._credentials = credentials
        self._base_url = credentials.url.rstrip("/")
        self._auth = httpx.BasicAuth(credentials.username, credentials.password)
        self._verify_ssl = credentials.verify_ssl

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated request to the Nexus API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (will be joined with base URL)
            params: Query parameters

        Returns:
            JSON response as a dictionary

        Raises:
            NexusAuthError: If authentication fails (401)
            NexusNotFoundError: If resource not found (404)
            NexusConnectionError: If connection fails
            NexusError: For other API errors
        """
        url = urljoin(self._base_url, f"{self.API_BASE}{endpoint}")

        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            async with httpx.AsyncClient(timeout=30.0, verify=self._verify_ssl) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    auth=self._auth,
                )

                if response.status_code == 401:
                    raise NexusAuthError("Authentication failed. Check username and password.")

                if response.status_code == 403:
                    raise NexusAuthError("Access denied. Insufficient permissions.")

                if response.status_code == 404:
                    raise NexusNotFoundError(f"Resource not found: {endpoint}")

                response.raise_for_status()

                result: dict[str, Any] = response.json()
                return result

        except httpx.ConnectError as e:
            raise NexusConnectionError(
                f"Failed to connect to Nexus at {self._base_url}: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise NexusConnectionError(f"Request timed out: {e}") from e
        except httpx.HTTPStatusError as e:
            raise NexusError(
                f"HTTP error: {e.response.status_code} - {e.response.text}"
            ) from e

    async def search(
        self,
        repository: str | None = None,
        format: str | None = None,
        group: str | None = None,
        name: str | None = None,
        version: str | None = None,
        continuation_token: str | None = None,
    ) -> SearchResponse:
        """Search for components in Nexus.

        Args:
            repository: Repository name to search in
            format: Package format (maven2, pypi, docker)
            group: Group ID (for Maven artifacts)
            name: Artifact/package name
            version: Specific version to find
            continuation_token: Token for pagination

        Returns:
            SearchResponse with matching items and optional continuation token
        """
        params = {
            "repository": repository,
            "format": format,
            "group": group,
            "name": name,
            "version": version,
            "continuationToken": continuation_token,
        }

        data = await self._request("GET", "/search", params)

        items = []
        for item in data.get("items", []):
            items.append(
                SearchResult(
                    id=item.get("id", ""),
                    repository=item.get("repository", ""),
                    group=item.get("group"),
                    name=item.get("name", ""),
                    version=item.get("version", ""),
                    format=item.get("format", ""),
                    assets=item.get("assets", []),
                )
            )

        return SearchResponse(
            items=items,
            continuation_token=data.get("continuationToken"),
        )

    async def search_all(
        self,
        repository: str | None = None,
        format: str | None = None,
        group: str | None = None,
        name: str | None = None,
        version: str | None = None,
        max_items: int = 1000,
    ) -> list[SearchResult]:
        """Search for all matching components, handling pagination.

        Args:
            repository: Repository name to search in
            format: Package format (maven2, pypi, docker)
            group: Group ID (for Maven artifacts)
            name: Artifact/package name
            version: Specific version to find
            max_items: Maximum number of items to return (safety limit)

        Returns:
            List of all matching SearchResult items
        """
        all_items: list[SearchResult] = []
        continuation_token: str | None = None

        while len(all_items) < max_items:
            response = await self.search(
                repository=repository,
                format=format,
                group=group,
                name=name,
                version=version,
                continuation_token=continuation_token,
            )

            all_items.extend(response.items)

            if not response.continuation_token:
                break

            continuation_token = response.continuation_token

        return all_items[:max_items]

    async def get_components(
        self,
        repository: str,
        continuation_token: str | None = None,
    ) -> SearchResponse:
        """List components in a specific repository.

        Args:
            repository: Repository name
            continuation_token: Token for pagination

        Returns:
            SearchResponse with components in the repository
        """
        params = {
            "repository": repository,
            "continuationToken": continuation_token,
        }

        data = await self._request("GET", "/components", params)

        items = []
        for item in data.get("items", []):
            items.append(
                SearchResult(
                    id=item.get("id", ""),
                    repository=item.get("repository", ""),
                    group=item.get("group"),
                    name=item.get("name", ""),
                    version=item.get("version", ""),
                    format=item.get("format", ""),
                    assets=item.get("assets", []),
                )
            )

        return SearchResponse(
            items=items,
            continuation_token=data.get("continuationToken"),
        )
