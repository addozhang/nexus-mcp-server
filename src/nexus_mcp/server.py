"""MCP Server for Nexus Repository Manager."""

import logging
from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse

from nexus_mcp.dependencies import (
    InvalidCredentialsError,
    MissingCredentialsError,
    get_nexus_credentials,
)
from nexus_mcp.tools.implementations import (
    get_docker_tags_impl,
    get_maven_versions_impl,
    get_python_versions_impl,
    list_docker_images_impl,
    search_maven_artifact_impl,
    search_python_package_impl,
)

logger = logging.getLogger(__name__)

# Create the FastMCP server instance
mcp = FastMCP(
    name="nexus-mcp",
    instructions="""
    Nexus MCP Server - Query Sonatype Nexus Repository Manager.

    This server provides tools to search and query Maven, Python (PyPI), and Docker
    repositories hosted in Nexus Repository Manager.

    Authentication is handled via HTTP headers:
    - X-Nexus-Url: The base URL of your Nexus instance
    - X-Nexus-Username: Your Nexus username
    - X-Nexus-Password: Your Nexus password

    Available tools:
    - search_maven_artifact: Search for Maven artifacts by group/artifact ID
    - get_maven_versions: Get all versions of a specific Maven artifact
    - search_python_package: Search for Python packages
    - get_python_versions: Get all versions of a Python package
    - list_docker_images: List Docker images in a repository
    - get_docker_tags: Get tags for a specific Docker image
    """,
)


# ============================================================================
# Health Check Endpoint
# ============================================================================


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for container orchestration."""
    return JSONResponse({
        "status": "healthy",
        "service": "nexus-mcp",
        "version": "0.1.0",
    })


def _get_credentials_or_error() -> dict[str, Any] | None:
    """Get credentials from headers or return error dict.

    Returns None if credentials are valid, error dict otherwise.
    """
    try:
        get_nexus_credentials()
        return None
    except MissingCredentialsError as e:
        return {"error": f"Authentication error: {e}"}
    except InvalidCredentialsError as e:
        return {"error": f"Invalid credentials: {e}"}


# ============================================================================
# Maven Tools
# ============================================================================


@mcp.tool
async def search_maven_artifact(
    group_id: Annotated[
        str | None,
        Field(description="Maven groupId to search for (e.g., 'org.apache.maven')"),
    ] = None,
    artifact_id: Annotated[
        str | None,
        Field(description="Maven artifactId to search for (e.g., 'maven-core')"),
    ] = None,
    version: Annotated[
        str | None,
        Field(description="Specific version to search for"),
    ] = None,
    repository: Annotated[
        str | None,
        Field(description="Repository name to search in (searches all if not specified)"),
    ] = None,
) -> dict[str, Any]:
    """Search for Maven artifacts by group ID, artifact ID, or version.

    Searches across all Maven repositories (or a specific one) and returns 
    matching artifacts with their available versions and download URLs.
    
    At least one of group_id or artifact_id must be provided.
    """
    try:
        creds = get_nexus_credentials()
    except (MissingCredentialsError, InvalidCredentialsError) as e:
        return {"error": f"Authentication error: {e}"}

    return await search_maven_artifact_impl(
        creds=creds,
        group_id=group_id,
        artifact_id=artifact_id,
        version=version,
        repository=repository,
    )


@mcp.tool
async def get_maven_versions(
    group_id: Annotated[
        str,
        Field(description="Maven groupId (e.g., 'org.apache.maven')"),
    ],
    artifact_id: Annotated[
        str,
        Field(description="Maven artifactId (e.g., 'maven-core')"),
    ],
    repository: Annotated[
        str | None,
        Field(description="Repository name to search in (searches all if not specified)"),
    ] = None,
    page_size: Annotated[
        int,
        Field(description="Number of versions per page (default 50)", ge=1, le=1000),
    ] = 50,
    continuation_token: Annotated[
        str | None,
        Field(description="Continuation token from previous response for pagination"),
    ] = None,
) -> dict[str, Any]:
    """Get all versions of a specific Maven artifact with pagination.

    Returns a paginated list of available versions for the specified groupId:artifactId.
    Use continuation_token to fetch subsequent pages.

    Response includes:
    - versions: List of versions in this page
    - hasMore: Whether there are more pages
    - continuationToken: Token to fetch next page (if hasMore is true)
    """
    try:
        creds = get_nexus_credentials()
    except (MissingCredentialsError, InvalidCredentialsError) as e:
        return {"error": f"Authentication error: {e}"}

    return await get_maven_versions_impl(
        creds=creds,
        group_id=group_id,
        artifact_id=artifact_id,
        repository=repository,
        page_size=page_size,
        continuation_token=continuation_token,
    )


# ============================================================================
# Python/PyPI Tools
# ============================================================================


@mcp.tool
async def search_python_package(
    name: Annotated[
        str,
        Field(description="Python package name to search for (e.g., 'requests')"),
    ],
    repository: Annotated[
        str | None,
        Field(description="Repository name to search in (searches all if not specified)"),
    ] = None,
) -> dict[str, Any]:
    """Search for Python/PyPI packages by name.

    Searches PyPI-format repositories and automatically handles Python's 
    naming conventions (converts between hyphens and underscores, e.g., 
    'my-package' vs 'my_package').
    
    Returns matching packages with their versions and download URLs.
    """
    try:
        creds = get_nexus_credentials()
    except (MissingCredentialsError, InvalidCredentialsError) as e:
        return {"error": f"Authentication error: {e}"}

    return await search_python_package_impl(
        creds=creds,
        name=name,
        repository=repository,
    )


@mcp.tool
async def get_python_versions(
    package_name: Annotated[
        str,
        Field(description="Python package name (e.g., 'requests')"),
    ],
    repository: Annotated[
        str | None,
        Field(description="Repository name to search in (searches all if not specified)"),
    ] = None,
    page_size: Annotated[
        int,
        Field(description="Number of versions per page (default 50)", ge=1, le=1000),
    ] = 50,
    continuation_token: Annotated[
        str | None,
        Field(description="Continuation token from previous response for pagination"),
    ] = None,
) -> dict[str, Any]:
    """Get all versions of a specific Python package with pagination.

    Returns paginated versions of the package with format information
    (wheel, sdist, etc.) and download URLs.

    Response includes:
    - versions: List of versions in this page
    - hasMore: Whether there are more pages
    - continuationToken: Token to fetch next page (if hasMore is true)
    """
    try:
        creds = get_nexus_credentials()
    except (MissingCredentialsError, InvalidCredentialsError) as e:
        return {"error": f"Authentication error: {e}"}

    return await get_python_versions_impl(
        creds=creds,
        package_name=package_name,
        repository=repository,
        page_size=page_size,
        continuation_token=continuation_token,
    )


# ============================================================================
# Docker Tools
# ============================================================================


@mcp.tool
async def list_docker_images(
    repository: Annotated[
        str,
        Field(description="Docker repository name to list images from"),
    ],
) -> dict[str, Any]:
    """List all Docker images in a repository.

    Returns all Docker images available in the specified repository
    with their available tags (sorted by tag name).
    """
    try:
        creds = get_nexus_credentials()
    except (MissingCredentialsError, InvalidCredentialsError) as e:
        return {"error": f"Authentication error: {e}"}

    return await list_docker_images_impl(
        creds=creds,
        repository=repository,
    )


@mcp.tool
async def get_docker_tags(
    repository: Annotated[
        str,
        Field(description="Docker repository name"),
    ],
    image_name: Annotated[
        str,
        Field(description="Docker image name (e.g., 'my-app' or 'library/nginx')"),
    ],
) -> dict[str, Any]:
    """Get all tags/versions for a specific Docker image.

    Returns detailed information about all tags for the specified image,
    including manifests, digests, and download URLs.
    """
    try:
        creds = get_nexus_credentials()
    except (MissingCredentialsError, InvalidCredentialsError) as e:
        return {"error": f"Authentication error: {e}"}

    return await get_docker_tags_impl(
        creds=creds,
        repository=repository,
        image_name=image_name,
    )


def run_server() -> None:
    """Run the MCP server with HTTP transport."""
    import os

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    host = os.environ.get("NEXUS_MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("NEXUS_MCP_PORT", "8000"))

    logger.info(f"Starting Nexus MCP Server on {host}:{port}")
    mcp.run(transport="sse", host=host, port=port)
