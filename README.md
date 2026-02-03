# Nexus MCP Server

MCP (Model Context Protocol) server for Sonatype Nexus Pro 3, enabling AI assistants to query Maven, Python (PyPI), and Docker repositories.

## Features
- **Per-request authentication** - Credentials passed as tool parameters (no hardcoded secrets)
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

# Run the server
python -m nexus_mcp
```

### Using Docker
```bash
docker build -t nexus-mcp-server .
docker run -it nexus-mcp-server python -m nexus_mcp
```

## Configuration

### Authentication
Unlike HTTP-based APIs, MCP uses stdio transport which doesn't support headers. Credentials are passed as parameters to each tool call:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `nexus_url` | Nexus instance URL | `https://nexus.company.com` |
| `nexus_username` | Username | `admin` |
| `nexus_password` | Password | `secret123` |

### MCP Client Configuration (Claude Desktop)
Add to your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "nexus": {
      "command": "python",
      "args": ["-m", "nexus_mcp"],
      "cwd": "/path/to/nexus-mcp-server",
      "env": {
        "PATH": "/path/to/nexus-mcp-server/venv/bin:$PATH"
      }
    }
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
│   └── mcp-architecture.md
├── src/nexus_mcp/           # Source code
│   ├── __init__.py          # Package init with version
│   ├── __main__.py          # CLI entry point
│   ├── server.py            # FastMCP server with tools
│   ├── nexus_client.py      # Nexus REST API client
│   ├── auth.py              # Authentication types
│   └── tools/               # Tool implementations
│       ├── __init__.py
│       └── implementations.py
├── tests/                   # Test suite
│   ├── conftest.py          # Fixtures and sample data
│   ├── test_nexus_client.py # Client unit tests
│   └── test_tools.py        # Tool integration tests
├── AGENTS.md                # Operational guide
├── IMPLEMENTATION_PLAN.md   # Task tracking
└── pyproject.toml           # Python project metadata
```

## Troubleshooting

### Connection Errors
- Verify `nexus_url` is correct and accessible
- Check network connectivity to your Nexus instance
- Ensure HTTPS certificates are valid (or use HTTP for local instances)

### Authentication Errors
- Verify username and password are correct
- Ensure the user has read permissions on the repositories
- Check if the Nexus instance requires specific authentication methods

### Empty Results
- Verify the repository name is correct
- Check that the package/artifact exists in Nexus
- For Python packages, try both hyphen and underscore naming

## License
MIT

## Contributing
Contributions welcome! Please run tests and linting before submitting PRs.
