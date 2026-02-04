# Nexus MCP Server

English | [简体中文](README.zh-CN.md)

MCP (Model Context Protocol) server for Sonatype Nexus Pro 3, enabling AI assistants to query Maven, Python (PyPI), and Docker repositories.

## Features
- **HTTP streaming transport** - Modern SSE-based transport with header authentication
- **Per-request authentication** - Credentials passed via HTTP headers (no hardcoded secrets)
- **Maven support** - Search artifacts, list versions, get metadata
- **Python support** - Search packages, list versions, get metadata
- **Docker support** - List images, get tags, image metadata
- **FastMCP framework** - Fast, modern Python implementation

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
docker build -t nexus-mcp-server .
docker run -p 8000:8000 nexus-mcp-server
```

## Configuration

### Server Configuration
The server can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXUS_MCP_HOST` | Host to bind to | `0.0.0.0` |
| `NEXUS_MCP_PORT` | Port to listen on | `8000` |

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
| `get_maven_versions` | Get all versions of an artifact | `group_id`, `artifact_id`, `repository` |

### Python Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `search_python_package` | Search Python packages | `name`, `repository` |
| `get_python_versions` | Get all versions of a package | `package_name`, `repository` |

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

## License
MIT

## Contributing
Contributions welcome! Please run tests and linting before submitting PRs.
