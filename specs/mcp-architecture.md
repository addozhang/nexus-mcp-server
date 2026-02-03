# MCP Server Architecture

## Requirement
Build a well-structured MCP server using FastMCP framework.

## Structure
- Use **FastMCP** (Python) for rapid development
- Tool-based architecture (each query operation = one MCP tool)
- Credential handling via context/dependencies

## Tools to Implement
1. `search_maven_artifact` - Search Maven components
2. `get_maven_versions` - Get versions of a Maven artifact
3. `search_python_package` - Search Python packages
4. `get_python_versions` - Get versions of a Python package
5. `list_docker_images` - List Docker images in repository
6. `get_docker_tags` - Get tags for a Docker image

## Error Handling
- Graceful handling of network errors
- Clear messages for authentication failures
- Validation of inputs before API calls

## Success Criteria
- Server starts and registers all tools
- Tools are discoverable by MCP clients
- Follows MCP protocol specification
- Includes proper logging for debugging
