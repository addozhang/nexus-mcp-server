"""Tests for the Nexus REST API client."""

import pytest
import respx
from conftest import SAMPLE_MAVEN_SEARCH_RESPONSE, make_search_response
from httpx import Response

from nexus_mcp.nexus_client import (
    NexusAuthError,
    NexusClient,
    NexusCredentials,
    NexusError,
    NexusNotFoundError,
)


class TestNexusCredentials:
    """Tests for NexusCredentials validation."""

    def test_valid_https_url(self) -> None:
        """Valid HTTPS URL should be accepted."""
        creds = NexusCredentials(
            url="https://nexus.example.com",
            username="user",
            password="pass",
        )
        creds.validate_url()  # Should not raise

    def test_valid_http_url(self) -> None:
        """Valid HTTP URL should be accepted."""
        creds = NexusCredentials(
            url="http://localhost:8081",
            username="user",
            password="pass",
        )
        creds.validate_url()  # Should not raise

    def test_invalid_url_no_scheme(self) -> None:
        """URL without scheme should be rejected."""
        creds = NexusCredentials(
            url="nexus.example.com",
            username="user",
            password="pass",
        )
        with pytest.raises(ValueError, match="Invalid Nexus URL"):
            creds.validate_url()

    def test_invalid_url_wrong_scheme(self) -> None:
        """URL with non-HTTP scheme should be rejected."""
        creds = NexusCredentials(
            url="ftp://nexus.example.com",
            username="user",
            password="pass",
        )
        with pytest.raises(ValueError, match="URL scheme must be http or https"):
            creds.validate_url()


class TestNexusClient:
    """Tests for NexusClient."""

    def test_client_creation_with_valid_credentials(
        self, nexus_credentials: NexusCredentials
    ) -> None:
        """Client should be created with valid credentials."""
        client = NexusClient(nexus_credentials)
        assert client._base_url == "https://nexus.example.com"

    def test_client_strips_trailing_slash(self) -> None:
        """Client should strip trailing slash from URL."""
        creds = NexusCredentials(
            url="https://nexus.example.com/",
            username="user",
            password="pass",
        )
        client = NexusClient(creds)
        assert client._base_url == "https://nexus.example.com"

    def test_client_preserves_url_path(self) -> None:
        """Client should preserve path in URL (e.g., /nexus)."""
        creds = NexusCredentials(
            url="https://nexus.example.com:8081/nexus",
            username="user",
            password="pass",
        )
        client = NexusClient(creds)
        assert client._base_url == "https://nexus.example.com:8081/nexus"

    def test_client_creation_with_invalid_url(self) -> None:
        """Client should reject invalid URL."""
        creds = NexusCredentials(
            url="not-a-url",
            username="user",
            password="pass",
        )
        with pytest.raises(ValueError):
            NexusClient(creds)


class TestNexusClientSearch:
    """Tests for NexusClient search operations."""

    @respx.mock
    async def test_search_success(self, nexus_credentials: NexusCredentials) -> None:
        """Successful search should return results."""
        respx.get("https://nexus.example.com/service/rest/v1/search").mock(
            return_value=Response(200, json=SAMPLE_MAVEN_SEARCH_RESPONSE)
        )

        client = NexusClient(nexus_credentials)
        result = await client.search(group="com.example", name="artifact")

        assert len(result.items) == 2
        assert result.items[0].group == "com.example"
        assert result.items[0].name == "artifact"
        assert result.items[0].version == "1.0.0"
        assert result.continuation_token is None

    @respx.mock
    async def test_search_with_url_path(self) -> None:
        """Search should work correctly with URL containing path (e.g., /nexus)."""
        creds = NexusCredentials(
            url="https://nexus.example.com:8081/nexus",
            username="user",
            password="pass",
        )

        respx.get("https://nexus.example.com:8081/nexus/service/rest/v1/search").mock(
            return_value=Response(200, json=SAMPLE_MAVEN_SEARCH_RESPONSE)
        )

        client = NexusClient(creds)
        result = await client.search(group="com.example", name="artifact")

        assert len(result.items) == 2
        assert result.items[0].group == "com.example"

    @respx.mock
    async def test_search_with_pagination(
        self, nexus_credentials: NexusCredentials
    ) -> None:
        """Search should handle pagination tokens."""
        page1 = make_search_response(
            [
                {
                    "id": "1",
                    "repository": "maven",
                    "format": "maven2",
                    "group": "com.example",
                    "name": "artifact",
                    "version": "1.0.0",
                    "assets": [],
                }
            ],
            continuation_token="token123",
        )
        page2 = make_search_response(
            [
                {
                    "id": "2",
                    "repository": "maven",
                    "format": "maven2",
                    "group": "com.example",
                    "name": "artifact",
                    "version": "2.0.0",
                    "assets": [],
                }
            ],
        )

        route = respx.get("https://nexus.example.com/service/rest/v1/search")
        route.side_effect = [
            Response(200, json=page1),
            Response(200, json=page2),
        ]

        client = NexusClient(nexus_credentials)
        results = await client.search_all(group="com.example", name="artifact")

        assert len(results) == 2
        assert results[0].version == "1.0.0"
        assert results[1].version == "2.0.0"

    @respx.mock
    async def test_search_empty_results(
        self, nexus_credentials: NexusCredentials
    ) -> None:
        """Search with no matches should return empty list."""
        respx.get("https://nexus.example.com/service/rest/v1/search").mock(
            return_value=Response(200, json={"items": [], "continuationToken": None})
        )

        client = NexusClient(nexus_credentials)
        result = await client.search(name="nonexistent")

        assert len(result.items) == 0

    @respx.mock
    async def test_search_auth_failure(
        self, nexus_credentials: NexusCredentials
    ) -> None:
        """401 response should raise NexusAuthError."""
        respx.get("https://nexus.example.com/service/rest/v1/search").mock(
            return_value=Response(401, json={"message": "Unauthorized"})
        )

        client = NexusClient(nexus_credentials)
        with pytest.raises(NexusAuthError, match="Authentication failed"):
            await client.search(name="artifact")

    @respx.mock
    async def test_search_forbidden(self, nexus_credentials: NexusCredentials) -> None:
        """403 response should raise NexusAuthError."""
        respx.get("https://nexus.example.com/service/rest/v1/search").mock(
            return_value=Response(403, json={"message": "Forbidden"})
        )

        client = NexusClient(nexus_credentials)
        with pytest.raises(NexusAuthError, match="Access denied"):
            await client.search(name="artifact")

    @respx.mock
    async def test_search_not_found(
        self, nexus_credentials: NexusCredentials
    ) -> None:
        """404 response should raise NexusNotFoundError."""
        respx.get("https://nexus.example.com/service/rest/v1/search").mock(
            return_value=Response(404, json={"message": "Not found"})
        )

        client = NexusClient(nexus_credentials)
        with pytest.raises(NexusNotFoundError):
            await client.search(name="artifact")

    @respx.mock
    async def test_search_server_error(
        self, nexus_credentials: NexusCredentials
    ) -> None:
        """500 response should raise NexusError."""
        respx.get("https://nexus.example.com/service/rest/v1/search").mock(
            return_value=Response(500, text="Internal Server Error")
        )

        client = NexusClient(nexus_credentials)
        with pytest.raises(NexusError, match="HTTP error"):
            await client.search(name="artifact")


class TestNexusClientComponents:
    """Tests for NexusClient component listing."""

    @respx.mock
    async def test_get_components_success(
        self, nexus_credentials: NexusCredentials
    ) -> None:
        """Successful component list should return results."""
        respx.get("https://nexus.example.com/service/rest/v1/components").mock(
            return_value=Response(200, json=SAMPLE_MAVEN_SEARCH_RESPONSE)
        )

        client = NexusClient(nexus_credentials)
        result = await client.get_components(repository="maven-releases")

        assert len(result.items) == 2
        assert result.items[0].repository == "maven-releases"
