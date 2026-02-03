"""Common test fixtures and utilities."""

import pytest
import respx
from httpx import Response

from nexus_mcp.nexus_client import NexusCredentials


@pytest.fixture
def nexus_credentials() -> NexusCredentials:
    """Fixture providing test Nexus credentials."""
    return NexusCredentials(
        url="https://nexus.example.com",
        username="testuser",
        password="testpass",
    )


@pytest.fixture
def mock_nexus() -> respx.MockRouter:
    """Fixture providing a mocked Nexus API.

    Use with respx to mock HTTP requests:

        def test_something(mock_nexus: respx.MockRouter):
            mock_nexus.get("/service/rest/v1/search").mock(
                return_value=Response(200, json={"items": []})
            )
    """
    with respx.mock(base_url="https://nexus.example.com") as mock:
        yield mock


# Sample response data for tests
SAMPLE_MAVEN_SEARCH_RESPONSE = {
    "items": [
        {
            "id": "bWF2ZW4tcmVsZWFzZXM6Y29tLmV4YW1wbGU6YXJ0aWZhY3Q6MS4wLjA=",
            "repository": "maven-releases",
            "format": "maven2",
            "group": "com.example",
            "name": "artifact",
            "version": "1.0.0",
            "assets": [
                {
                    "downloadUrl": "https://nexus.example.com/repository/maven-releases/com/example/artifact/1.0.0/artifact-1.0.0.jar",
                    "path": "com/example/artifact/1.0.0/artifact-1.0.0.jar",
                    "contentType": "application/java-archive",
                }
            ],
        },
        {
            "id": "bWF2ZW4tcmVsZWFzZXM6Y29tLmV4YW1wbGU6YXJ0aWZhY3Q6MS4xLjA=",
            "repository": "maven-releases",
            "format": "maven2",
            "group": "com.example",
            "name": "artifact",
            "version": "1.1.0",
            "assets": [
                {
                    "downloadUrl": "https://nexus.example.com/repository/maven-releases/com/example/artifact/1.1.0/artifact-1.1.0.jar",
                    "path": "com/example/artifact/1.1.0/artifact-1.1.0.jar",
                    "contentType": "application/java-archive",
                }
            ],
        },
    ],
    "continuationToken": None,
}

SAMPLE_PYTHON_SEARCH_RESPONSE = {
    "items": [
        {
            "id": "cHlwaS1yZWxlYXNlczpyZXF1ZXN0czoyLjI4LjA=",
            "repository": "pypi-releases",
            "format": "pypi",
            "group": None,
            "name": "requests",
            "version": "2.28.0",
            "assets": [
                {
                    "downloadUrl": "https://nexus.example.com/repository/pypi-releases/packages/requests/2.28.0/requests-2.28.0-py3-none-any.whl",
                    "path": "packages/requests/2.28.0/requests-2.28.0-py3-none-any.whl",
                    "contentType": "application/zip",
                }
            ],
        }
    ],
    "continuationToken": None,
}

SAMPLE_DOCKER_SEARCH_RESPONSE = {
    "items": [
        {
            "id": "ZG9ja2VyLWhvc3RlZDpteS1hcHA6bGF0ZXN0",
            "repository": "docker-hosted",
            "format": "docker",
            "group": None,
            "name": "my-app",
            "version": "latest",
            "assets": [
                {
                    "downloadUrl": "https://nexus.example.com/v2/my-app/manifests/latest",
                    "path": "v2/my-app/manifests/latest",
                    "contentType": "application/vnd.docker.distribution.manifest.v2+json",
                }
            ],
        }
    ],
    "continuationToken": None,
}


def make_search_response(
    items: list[dict], continuation_token: str | None = None
) -> dict:
    """Helper to create a search response structure."""
    return {
        "items": items,
        "continuationToken": continuation_token,
    }


def make_error_response(status: int, message: str) -> Response:
    """Helper to create an error response."""
    return Response(status, json={"message": message})
