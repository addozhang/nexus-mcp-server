# Agent Operational Guide

## Project: Nexus MCP Server

### Build & Test Commands (Backpressure)

**Setup**:
```bash
python -m venv venv
source venv/bin/activate  # or venv/bin/activate.fish
pip install -e ".[dev]"
```

**Run tests**:
```bash
pytest tests/ -v
```

**Type checking**:
```bash
mypy src/
```

**Linting**:
```bash
ruff check src/ tests/
```

**Run server locally**:
```bash
python -m nexus_mcp
```

### Project Structure
```
nexus-mcp-server/
├── src/nexus_mcp/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── nexus_client.py    # Nexus REST API client
│   └── tools/             # MCP tool implementations
├── tests/
├── pyproject.toml
├── README.md
└── Dockerfile             # For sandboxed execution
```

### Dependencies
- `fastmcp` - MCP server framework
- `httpx` - HTTP client for Nexus API
- `pydantic` - Data validation
- `pytest` - Testing
- `mypy` - Type checking
- `ruff` - Linting

### Operational Learnings

#### FastMCP Framework
- FastMCP's `@mcp.tool` decorator wraps functions into `FunctionTool` objects, making them non-callable directly
- For testability, separate tool implementation functions (`*_impl`) from MCP decorators
- Import implementations in `server.py` and wrap them with `@mcp.tool`

#### MCP Protocol & Authentication
- MCP protocol (stdio transport) does not support HTTP headers
- Credentials must be passed as tool parameters: `nexus_url`, `nexus_username`, `nexus_password`
- Each tool call receives fresh credentials, enabling multi-tenant use

#### Nexus API Quirks
- Search API uses `format` parameter for repository type filtering (maven2, pypi, docker)
- Maven coordinates: use `maven.groupId`, `maven.artifactId`, `maven.version` params
- Python packages: may need to normalize names (hyphen vs underscore)
- Pagination uses `continuationToken` in response, pass back as query param

#### Testing with respx
- Use `httpx.ConnectError` (not generic `Exception`) for connection error mocking
- Import sorting: `httpx` before `respx` when both needed
- `respx.mock` decorator handles async test functions automatically

#### Project Structure
```
src/nexus_mcp/
├── __init__.py          # Version and main() entry point
├── __main__.py          # CLI runner: python -m nexus_mcp
├── server.py            # FastMCP server with @mcp.tool decorators
├── nexus_client.py      # Async httpx client for Nexus REST API
├── auth.py              # NexusConnectionParams type definitions
└── tools/
    ├── __init__.py      # Re-exports implementations
    └── implementations.py  # Testable tool functions (*_impl)
```
