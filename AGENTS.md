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

**Run server locally** (HTTP transport on port 8000):
```bash
python -m nexus_mcp

# Or with custom host/port:
NEXUS_MCP_HOST=127.0.0.1 NEXUS_MCP_PORT=9000 python -m nexus_mcp
```

**Test server with curl**:
```bash
curl http://localhost:8000/health
```

### Project Structure
```
nexus-mcp-server/
├── src/nexus_mcp/
│   ├── __init__.py          # Version and main() entry point
│   ├── __main__.py          # CLI runner: python -m nexus_mcp
│   ├── server.py            # FastMCP server with @mcp.tool decorators
│   ├── nexus_client.py      # Async httpx client for Nexus REST API
│   ├── auth.py              # NexusConnectionParams type definitions
│   ├── dependencies.py      # Header extraction for credentials
│   └── tools/
│       ├── __init__.py      # Re-exports implementations
│       └── implementations.py  # Testable tool functions (*_impl)
├── tests/
│   ├── conftest.py          # Fixtures and sample data
│   ├── test_nexus_client.py # Client unit tests
│   ├── test_tools.py        # Tool integration tests
│   └── test_http_transport.py # HTTP transport tests
├── specs/                   # Requirement specifications
├── pyproject.toml
├── README.md
└── Dockerfile               # For containerized deployment
```

### Dependencies
- `fastmcp` - MCP server framework (with HTTP SSE transport)
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

#### HTTP Transport & Authentication
- Server uses HTTP SSE transport: `mcp.run(transport="sse", host="0.0.0.0", port=8000)`
- Credentials passed via HTTP headers: `X-Nexus-Url`, `X-Nexus-Username`, `X-Nexus-Password`
- Use `get_http_request()` from `fastmcp.server.dependencies` to access request headers
- Headers are case-insensitive (Starlette normalizes to lowercase)
- Credentials extracted via `dependencies.py:get_nexus_credentials()`

#### Credential Extraction Pattern
```python
from fastmcp.server.dependencies import get_http_request

def get_nexus_credentials() -> NexusCredentials:
    request = get_http_request()
    headers = request.headers if request else {}
    nexus_url = headers.get("x-nexus-url")
    # ... validate and return NexusCredentials
```

#### Nexus API Quirks
- Search API uses `format` parameter for repository type filtering (maven2, pypi, docker)
- Maven coordinates: use `maven.groupId`, `maven.artifactId`, `maven.version` params
- Python packages: may need to normalize names (hyphen vs underscore)
- Pagination uses `continuationToken` in response, pass back as query param

#### Testing with respx
- Use `httpx.ConnectError` (not generic `Exception`) for connection error mocking
- Import sorting: `httpx` before `respx` when both needed
- `respx.mock` decorator handles async test functions automatically

#### Testing HTTP Headers
- Mock `get_http_request()` to test credential extraction
- Use `unittest.mock.patch` to inject mock request with headers
- Test fixtures in `conftest.py`: `mock_http_headers`, `mock_http_headers_missing`

#### Migration Notes (stdio -> HTTP)
- Removed credential parameters from tool signatures
- Tools now call `get_nexus_credentials()` internally
- Tests use `NexusCredentials` object instead of individual params
- Old type aliases (`NexusUrl`, `NexusUsername`, `NexusPassword`) removed from auth.py
