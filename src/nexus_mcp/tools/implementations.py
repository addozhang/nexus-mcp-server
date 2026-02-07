"""Tool implementations for Nexus MCP Server.

These are the core implementations, separate from the MCP decorator registration.
"""

from typing import Any

from nexus_mcp.nexus_client import (
    NexusAuthError,
    NexusClient,
    NexusConnectionError,
    NexusCredentials,
    NexusError,
    NexusNotFoundError,
    SearchResult,
)


def _create_client(creds: NexusCredentials) -> NexusClient:
    """Create a NexusClient from credentials."""
    return NexusClient(creds)


def _format_search_results(results: list[SearchResult]) -> list[dict[str, Any]]:
    """Format search results for output."""
    return [
        {
            "repository": r.repository,
            "group": r.group,
            "name": r.name,
            "version": r.version,
            "format": r.format,
            "assets": [
                {"downloadUrl": a.get("downloadUrl", ""), "path": a.get("path", "")}
                for a in r.assets
            ],
        }
        for r in results
    ]


def _handle_nexus_error(e: NexusError) -> str:
    """Convert NexusError to a user-friendly error message."""
    if isinstance(e, NexusAuthError):
        return f"Authentication error: {e}"
    elif isinstance(e, NexusConnectionError):
        return f"Connection error: {e}"
    elif isinstance(e, NexusNotFoundError):
        return f"Not found: {e}"
    else:
        return f"Nexus error: {e}"


# ============================================================================
# Maven Tools
# ============================================================================


async def search_maven_artifact_impl(
    creds: NexusCredentials,
    group_id: str | None = None,
    artifact_id: str | None = None,
    version: str | None = None,
    repository: str | None = None,
) -> dict[str, Any]:
    """Search for Maven artifacts in Nexus Repository Manager.

    Search Maven repositories by groupId, artifactId, or version.
    Returns matching artifacts with their versions and download URLs.
    """
    if not group_id and not artifact_id:
        return {"error": "At least one of group_id or artifact_id must be provided"}

    try:
        client = _create_client(creds)
        results = await client.search_all(
            repository=repository,
            format="maven2",
            group=group_id,
            name=artifact_id,
            version=version,
        )

        return {
            "count": len(results),
            "artifacts": _format_search_results(results),
        }

    except NexusError as e:
        return {"error": _handle_nexus_error(e)}
    except ValueError as e:
        return {"error": f"Invalid parameters: {e}"}


async def get_maven_versions_impl(
    creds: NexusCredentials,
    group_id: str,
    artifact_id: str,
    repository: str | None = None,
    page_size: int = 20,
    continuation_token: str | None = None,
) -> dict[str, Any]:
    """Get versions of a specific Maven artifact with pagination.

    Returns a paginated list of available versions for the specified groupId:artifactId.
    Use continuation_token to fetch subsequent pages.

    Args:
        group_id: Maven group ID
        artifact_id: Maven artifact ID
        repository: Optional repository name
        page_size: Number of versions per page (default 20)
        continuation_token: Token for next page (from previous response)
    """
    try:
        client = _create_client(creds)

        # Fetch one page from Nexus API
        response = await client.search(
            repository=repository,
            format="maven2",
            group=group_id,
            name=artifact_id,
            continuation_token=continuation_token,
        )

        # Extract unique versions from this page
        versions_with_assets: dict[str, dict[str, Any]] = {}
        for r in response.items:
            if r.version not in versions_with_assets:
                versions_with_assets[r.version] = {
                    "version": r.version,
                    "repository": r.repository,
                    "assets": [
                        {"downloadUrl": a.get("downloadUrl", ""), "path": a.get("path", "")}
                        for a in r.assets
                    ],
                }

        # Sort versions (simple string sort - works for most version schemes)
        sorted_versions = sorted(
            versions_with_assets.values(), key=lambda x: str(x["version"]), reverse=True
        )

        result: dict[str, Any] = {
            "groupId": group_id,
            "artifactId": artifact_id,
            "count": len(sorted_versions),
            "versions": sorted_versions,
        }

        # Include continuation token if there are more results
        if response.continuation_token:
            result["continuationToken"] = response.continuation_token
            result["hasMore"] = True
        else:
            result["hasMore"] = False

        return result

    except NexusError as e:
        return {"error": _handle_nexus_error(e)}
    except ValueError as e:
        return {"error": f"Invalid parameters: {e}"}


# ============================================================================
# Python/PyPI Tools
# ============================================================================


async def search_python_package_impl(
    creds: NexusCredentials,
    name: str,
    repository: str | None = None,
) -> dict[str, Any]:
    """Search for Python packages in Nexus Repository Manager.

    Searches PyPI-format repositories for packages matching the given name.
    Handles Python package naming conventions (underscores vs hyphens).
    """
    try:
        client = _create_client(creds)

        # Search with original name
        results = await client.search_all(
            repository=repository,
            format="pypi",
            name=name,
        )

        # Also try with normalized name (underscores <-> hyphens)
        normalized = name.replace("-", "_") if "-" in name else name.replace("_", "-")
        if normalized != name:
            additional = await client.search_all(
                repository=repository,
                format="pypi",
                name=normalized,
            )
            # Deduplicate by ID
            seen_ids = {r.id for r in results}
            results.extend(r for r in additional if r.id not in seen_ids)

        return {
            "count": len(results),
            "packages": _format_search_results(results),
        }

    except NexusError as e:
        return {"error": _handle_nexus_error(e)}
    except ValueError as e:
        return {"error": f"Invalid parameters: {e}"}


async def get_python_versions_impl(
    creds: NexusCredentials,
    package_name: str,
    repository: str | None = None,
    page_size: int = 20,
    continuation_token: str | None = None,
) -> dict[str, Any]:
    """Get versions of a specific Python package with pagination.

    Returns paginated versions of the package with format information
    (wheel, sdist, etc.) and download URLs.

    Args:
        package_name: Python package name
        repository: Optional repository name
        page_size: Number of versions per page (default 20)
        continuation_token: Token for next page (from previous response)
    """
    try:
        client = _create_client(creds)

        # Search with original name
        response = await client.search(
            repository=repository,
            format="pypi",
            name=package_name,
            continuation_token=continuation_token,
        )

        # Also try normalized name if no continuation token (first page only)
        if not continuation_token:
            normalized = (
                package_name.replace("-", "_")
                if "-" in package_name
                else package_name.replace("_", "-")
            )
            if normalized != package_name:
                additional_response = await client.search(
                    repository=repository,
                    format="pypi",
                    name=normalized,
                )
                # Merge results
                seen_ids = {r.id for r in response.items}
                response.items.extend(
                    r for r in additional_response.items if r.id not in seen_ids
                )

        # Group by version
        versions_data: dict[str, dict[str, Any]] = {}
        for r in response.items:
            if r.version not in versions_data:
                versions_data[r.version] = {
                    "version": r.version,
                    "repository": r.repository,
                    "assets": [],
                }
            versions_data[r.version]["assets"].extend(
                [
                    {
                        "downloadUrl": a.get("downloadUrl", ""),
                        "path": a.get("path", ""),
                        "contentType": a.get("contentType", ""),
                    }
                    for a in r.assets
                ]
            )

        sorted_versions = sorted(
            versions_data.values(), key=lambda x: str(x["version"]), reverse=True
        )

        result: dict[str, Any] = {
            "packageName": package_name,
            "count": len(sorted_versions),
            "versions": sorted_versions,
        }

        # Include continuation token if there are more results
        if response.continuation_token:
            result["continuationToken"] = response.continuation_token
            result["hasMore"] = True
        else:
            result["hasMore"] = False

        return result

    except NexusError as e:
        return {"error": _handle_nexus_error(e)}
    except ValueError as e:
        return {"error": f"Invalid parameters: {e}"}


# ============================================================================
# Docker Tools
# ============================================================================


async def list_docker_images_impl(
    creds: NexusCredentials,
    repository: str,
) -> dict[str, Any]:
    """List Docker images in a Nexus repository.

    Returns all Docker images available in the specified repository
    with their latest tags.
    """
    try:
        client = _create_client(creds)

        results = await client.search_all(
            repository=repository,
            format="docker",
        )

        # Group by image name, collect all versions (tags)
        images: dict[str, dict[str, Any]] = {}
        for r in results:
            if r.name not in images:
                images[r.name] = {
                    "name": r.name,
                    "repository": r.repository,
                    "tags": [],
                }
            if r.version and r.version not in images[r.name]["tags"]:
                images[r.name]["tags"].append(r.version)

        # Sort tags within each image
        for img in images.values():
            img["tags"].sort(reverse=True)

        return {
            "repository": repository,
            "count": len(images),
            "images": list(images.values()),
        }

    except NexusError as e:
        return {"error": _handle_nexus_error(e)}
    except ValueError as e:
        return {"error": f"Invalid parameters: {e}"}


async def get_docker_tags_impl(
    creds: NexusCredentials,
    repository: str,
    image_name: str,
) -> dict[str, Any]:
    """Get all tags for a specific Docker image.

    Returns detailed information about all tags for the specified image,
    including digest and asset information when available.
    """
    try:
        client = _create_client(creds)

        results = await client.search_all(
            repository=repository,
            format="docker",
            name=image_name,
        )

        tags: list[dict[str, Any]] = []
        for r in results:
            tag_info = {
                "tag": r.version,
                "repository": r.repository,
                "assets": [
                    {
                        "downloadUrl": a.get("downloadUrl", ""),
                        "path": a.get("path", ""),
                        "contentType": a.get("contentType", ""),
                    }
                    for a in r.assets
                ],
            }
            tags.append(tag_info)

        # Sort by tag name
        tags.sort(key=lambda x: str(x["tag"]), reverse=True)

        return {
            "repository": repository,
            "imageName": image_name,
            "count": len(tags),
            "tags": tags,
        }

    except NexusError as e:
        return {"error": _handle_nexus_error(e)}
    except ValueError as e:
        return {"error": f"Invalid parameters: {e}"}
