"""MCP Server for Nexus Repository Manager."""

import logging
from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from nexus_mcp.auth import NexusPassword, NexusUrl, NexusUsername
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

    All tools require Nexus connection credentials:
    - nexus_url: The base URL of your Nexus instance
    - nexus_username: Your Nexus username
    - nexus_password: Your Nexus password

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
# Maven Tools
# ============================================================================


@mcp.tool
async def search_maven_artifact(
    nexus_url: NexusUrl,
    nexus_username: NexusUsername,
    nexus_password: NexusPassword,
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
    """Search for Maven artifacts in Nexus Repository Manager.

    Search Maven repositories by groupId, artifactId, or version.
    Returns matching artifacts with their versions and download URLs.
    """
    return await search_maven_artifact_impl(
        nexus_url=nexus_url,
        nexus_username=nexus_username,
        nexus_password=nexus_password,
        group_id=group_id,
        artifact_id=artifact_id,
        version=version,
        repository=repository,
    )


@mcp.tool
async def get_maven_versions(
    nexus_url: NexusUrl,
    nexus_username: NexusUsername,
    nexus_password: NexusPassword,
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
) -> dict[str, Any]:
    """Get all versions of a specific Maven artifact.

    Returns a list of all available versions for the specified groupId:artifactId,
    sorted from newest to oldest.
    """
    return await get_maven_versions_impl(
        nexus_url=nexus_url,
        nexus_username=nexus_username,
        nexus_password=nexus_password,
        group_id=group_id,
        artifact_id=artifact_id,
        repository=repository,
    )


# ============================================================================
# Python/PyPI Tools
# ============================================================================


@mcp.tool
async def search_python_package(
    nexus_url: NexusUrl,
    nexus_username: NexusUsername,
    nexus_password: NexusPassword,
    name: Annotated[
        str,
        Field(description="Python package name to search for (e.g., 'requests')"),
    ],
    repository: Annotated[
        str | None,
        Field(description="Repository name to search in (searches all if not specified)"),
    ] = None,
) -> dict[str, Any]:
    """Search for Python packages in Nexus Repository Manager.

    Searches PyPI-format repositories for packages matching the given name.
    Handles Python package naming conventions (underscores vs hyphens).
    """
    return await search_python_package_impl(
        nexus_url=nexus_url,
        nexus_username=nexus_username,
        nexus_password=nexus_password,
        name=name,
        repository=repository,
    )


@mcp.tool
async def get_python_versions(
    nexus_url: NexusUrl,
    nexus_username: NexusUsername,
    nexus_password: NexusPassword,
    package_name: Annotated[
        str,
        Field(description="Python package name (e.g., 'requests')"),
    ],
    repository: Annotated[
        str | None,
        Field(description="Repository name to search in (searches all if not specified)"),
    ] = None,
) -> dict[str, Any]:
    """Get all versions of a specific Python package.

    Returns all available versions of the package with format information
    (wheel, sdist, etc.) and download URLs.
    """
    return await get_python_versions_impl(
        nexus_url=nexus_url,
        nexus_username=nexus_username,
        nexus_password=nexus_password,
        package_name=package_name,
        repository=repository,
    )


# ============================================================================
# Docker Tools
# ============================================================================


@mcp.tool
async def list_docker_images(
    nexus_url: NexusUrl,
    nexus_username: NexusUsername,
    nexus_password: NexusPassword,
    repository: Annotated[
        str,
        Field(description="Docker repository name to list images from"),
    ],
) -> dict[str, Any]:
    """List Docker images in a Nexus repository.

    Returns all Docker images available in the specified repository
    with their latest tags.
    """
    return await list_docker_images_impl(
        nexus_url=nexus_url,
        nexus_username=nexus_username,
        nexus_password=nexus_password,
        repository=repository,
    )


@mcp.tool
async def get_docker_tags(
    nexus_url: NexusUrl,
    nexus_username: NexusUsername,
    nexus_password: NexusPassword,
    repository: Annotated[
        str,
        Field(description="Docker repository name"),
    ],
    image_name: Annotated[
        str,
        Field(description="Docker image name (e.g., 'my-app' or 'library/nginx')"),
    ],
) -> dict[str, Any]:
    """Get all tags for a specific Docker image.

    Returns detailed information about all tags for the specified image,
    including digest and asset information when available.
    """
    return await get_docker_tags_impl(
        nexus_url=nexus_url,
        nexus_username=nexus_username,
        nexus_password=nexus_password,
        repository=repository,
        image_name=image_name,
    )


def run_server() -> None:
    """Run the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Starting Nexus MCP Server")
    mcp.run()
