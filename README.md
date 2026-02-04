# Nexus MCP Server

<!-- mcp-name: io.github.addozhang/nexus -->

English | [简体中文](README.zh-CN.md)

MCP (Model Context Protocol) server for Sonatype Nexus Repository Manager 3 (OSS and Pro), enabling AI assistants to query Maven, Python (PyPI), and Docker repositories.

## Features
- **Multiple transport modes** - SSE (default) or streamable-http transport
- **HTTP streaming transport** - Modern SSE-based transport with header authentication
- **Per-request authentication** - Credentials passed via HTTP headers (no hardcoded secrets)
- **Maven support** - Search artifacts, list versions, get metadata
- **Python support** - Search packages, list versions, get metadata
- **Docker support** - List images, get tags, image metadata
- **FastMCP framework** - Fast, modern Python implementation

## Compatibility

**Supported Nexus versions:**
- ✅ Nexus Repository Manager 3.x OSS (Open Source)
- ✅ Nexus Repository Manager 3.x Pro

This server uses the standard Nexus REST API v1 (`/service/rest/v1`), which is available in both OSS and Pro editions.

## Available Tools

This MCP server provides **6 read-only tools** for querying Nexus repositories:

### 📦 Maven Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `search_maven_artifact` | Search for Maven artifacts | `group_id`, `artifact_id`, `version`, `repository` |
| `get_maven_versions` | Get all versions of a Maven artifact (paginated) | `group_id`, `artifact_id`, `repository`, `page_size`, `continuation_token` |

### 🐍 Python/PyPI Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `search_python_package` | Search for Python packages | `name`, `repository` |
| `get_python_versions` | Get all versions of a Python package (paginated) | `package_name`, `repository`, `page_size`, `continuation_token` |

### 🐳 Docker Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `list_docker_images` | List all Docker images in a repository | `repository` |
| `get_docker_tags` | Get all tags for a Docker image | `repository`, `image_name` |

**Note:** All tools are read-only and safe to use. No write operations (create/update/delete) are supported.

## Installation

### From Source
```bash
# Clone the repository
git clone https://github.com/your-org/nexus-mcp-server.git
cd nexus-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv/bin/activate.fish

# Install in development mode
pip install -e ".[dev]"

# Run the server (defaults to http://0.0.0.0:8000)
python -m nexus_mcp
```

### Using Docker
```bash
# Quick start
docker run -p 8000:8000 addozhang/nexus-mcp-server:latest

# Or use docker-compose
docker-compose up

# See DOCKER.md for detailed deployment guide
```

For detailed deployment guide, see [DOCKER.md](DOCKER.md).

## Configuration

### Server Configuration
The server can be configured using command line arguments or environment variables:

| Variable | CLI Argument | Description | Default |
|----------|--------------|-------------|---------|
| `NEXUS_MCP_HOST` | `--host` | Host to bind to | `0.0.0.0` |
| `NEXUS_MCP_PORT` | `--port` | Port to listen on | `8000` |
| `NEXUS_MCP_TRANSPORT` | `--transport` | Transport mode (`sse` or `streamable-http`) | `sse` |

**Priority:** CLI arguments > Environment variables > Default values

**Transport Modes:**
- `sse` (default) - Server-Sent Events transport, compatible with most MCP clients
- `streamable-http` - Streamable HTTP transport for clients that prefer this protocol

### Running the Server

#### Local Development
```bash
# SSE mode (default)
python -m nexus_mcp

# Streamable-HTTP mode
python -m nexus_mcp --transport streamable-http

# Custom port
python -m nexus_mcp --port 9000

# Custom host and port
python -m nexus_mcp --host 127.0.0.1 --port 9000
```

#### Using Docker
```bash
# SSE mode (default)
docker run -p 8000:8000 addozhang/nexus-mcp-server:latest

# Streamable-HTTP mode
docker run -e NEXUS_MCP_TRANSPORT=streamable-http -p 8000:8000 addozhang/nexus-mcp-server:latest

# Custom port
docker run -e NEXUS_MCP_PORT=9000 -p 9000:9000 addozhang/nexus-mcp-server:latest

# Or use docker-compose
docker-compose up

# See DOCKER.md for detailed deployment guide
```

For detailed deployment guide, see [DOCKER.md](DOCKER.md).

### Authentication via HTTP Headers
Credentials are passed as HTTP headers with each request:

| Header | Description | Example | Required |
|--------|-------------|---------|----------|
| `X-Nexus-Url` | Nexus instance URL | `https://nexus.company.com` | Yes |
| `X-Nexus-Username` | Username | `admin` | Yes |
| `X-Nexus-Password` | Password | `secret123` | Yes |
| `X-Nexus-Verify-SSL` | Verify SSL certificates | `false` | No (default: `true`) |

**Note**: Set `X-Nexus-Verify-SSL: false` when connecting to self-hosted Nexus instances with self-signed certificates.

### MCP Client Configuration (Claude Desktop)
Add to your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "nexus": {
      "url": "http://localhost:8000/sse",
      "headers": {
        "X-Nexus-Url": "https://nexus.company.com",
        "X-Nexus-Username": "admin",
        "X-Nexus-Password": "secret123"
      }
    }
  }
}
```

For self-signed certificates:
```json
{
  "mcpServers": {
    "nexus": {
      "url": "http://localhost:8000/sse",
      "headers": {
        "X-Nexus-Url": "https://nexus.company.com",
        "X-Nexus-Username": "admin",
        "X-Nexus-Password": "secret123",
        "X-Nexus-Verify-SSL": "false"
      }
    }
  }
}
```

### MCP Client Configuration (Other Clients)
For other MCP clients that support HTTP transport:

```json
{
  "url": "http://localhost:8000/sse",
  "headers": {
    "X-Nexus-Url": "https://nexus.company.com",
    "X-Nexus-Username": "your-username",
    "X-Nexus-Password": "your-password"
  }
}
```

## MCP Tools

### Maven Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `search_maven_artifact` | Search Maven repositories | `group_id`, `artifact_id`, `version`, `repository` |
| `get_maven_versions` | Get versions of an artifact (paginated) | `group_id`, `artifact_id`, `repository`, `page_size` (default 50), `continuation_token` |

**Pagination example:**
```python
# First page
response = get_maven_versions("com.example", "myapp")
# response contains: versions, hasMore, continuationToken (if hasMore is true)

# Next page
if response["hasMore"]:
    next_response = get_maven_versions(
        "com.example", 
        "myapp", 
        continuation_token=response["continuationToken"]
    )
```

### Python Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `search_python_package` | Search Python packages | `name`, `repository` |
| `get_python_versions` | Get versions of a package (paginated) | `package_name`, `repository`, `page_size` (default 50), `continuation_token` |

**Pagination:** Same pattern as Maven - check `hasMore` and use `continuationToken` for subsequent pages.

### Docker Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `list_docker_images` | List images in a repository | `repository` |
| `get_docker_tags` | Get tags for an image | `repository`, `image_name` |

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Type Checking
```bash
mypy src/
```

### Linting
```bash
ruff check src/ tests/
```

## Project Structure
```
nexus-mcp-server/
├── specs/                    # Requirements documents
│   ├── authentication.md
│   ├── maven-support.md
│   ├── python-support.md
│   ├── docker-support.md
│   ├── mcp-architecture.md
│   └── http-streaming.md
├── src/nexus_mcp/           # Source code
│   ├── __init__.py          # Package init with version
│   ├── __main__.py          # CLI entry point
│   ├── server.py            # FastMCP server with tools
│   ├── nexus_client.py      # Nexus REST API client
│   ├── auth.py              # Authentication types
│   ├── dependencies.py      # Credential extraction from headers
│   └── tools/               # Tool implementations
│       ├── __init__.py
│       └── implementations.py
├── tests/                   # Test suite
│   ├── conftest.py          # Fixtures and sample data
│   ├── test_nexus_client.py # Client unit tests
│   ├── test_tools.py        # Tool integration tests
│   └── test_http_transport.py # HTTP transport tests
├── AGENTS.md                # Operational guide
├── IMPLEMENTATION_PLAN.md   # Task tracking
└── pyproject.toml           # Python project metadata
```

## Troubleshooting

### Connection Errors
- Verify the MCP server is running (`python -m nexus_mcp`)
- Check that port 8000 is accessible
- Verify `X-Nexus-Url` header is correct and accessible
- Check network connectivity to your Nexus instance
- Ensure HTTPS certificates are valid (or use HTTP for local instances)

### Authentication Errors
- Verify `X-Nexus-Username` and `X-Nexus-Password` headers are correct
- Ensure the user has read permissions on the repositories
- Check if the Nexus instance requires specific authentication methods

### Missing Credentials Error
- Ensure all three headers are set: `X-Nexus-Url`, `X-Nexus-Username`, `X-Nexus-Password`
- Check that your MCP client supports HTTP headers

### Empty Results
- Verify the repository name is correct
- Check that the package/artifact exists in Nexus
- For Python packages, try both hyphen and underscore naming

### Transport Mode Issues
**Connection timeout with streamable-http:**
- Ensure your client supports streamable-http transport
- Try using SSE mode instead: `python -m nexus_mcp --transport sse`
- Check firewall rules allow HTTP connections

**Tools not appearing:**
- Both SSE and streamable-http expose the same tools
- Verify headers are correctly passed (X-Nexus-*)
- Check server logs for authentication errors

## License
MIT

## Contributing
Contributions welcome! Please run tests and linting before submitting PRs.
