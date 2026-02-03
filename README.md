# Nexus MCP Server

MCP (Model Context Protocol) server for Sonatype Nexus Pro 3, enabling AI assistants to query Maven, Python (PyPI), and Docker repositories.

## Features
- 🔐 **Per-request authentication** via headers (no hardcoded credentials)
- 📦 **Maven support**: Search artifacts, list versions, get metadata
- 🐍 **Python support**: Search packages, list versions, get metadata
- 🐳 **Docker support**: List images, get tags, image metadata
- ⚡ **FastMCP framework**: Fast, modern Python implementation

## Authentication
Credentials are passed per-request via headers:
- `X-Nexus-Url`: Nexus instance URL (e.g., `https://nexus.company.com`)
- `X-Nexus-Username`: Username
- `X-Nexus-Password`: Password

## Quick Start

### Prerequisites
- Python 3.10+
- Docker (for sandboxed development)

### Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run server
python -m nexus_mcp
```

## Ralph Loop Development
This project is built using the Ralph Wiggum loop with `opencode`:

```bash
# Run the complete loop (Planning → Building)
./ralph-loop.sh
```

The loop will:
1. **Plan** - Analyze specs and create implementation plan (5 iterations max)
2. **Build** - Implement tasks, run tests, commit (10 iterations max)
3. **Stop** - When `STATUS: COMPLETE` appears in `IMPLEMENTATION_PLAN.md`

### Monitoring Progress
- Watch real-time: `tail -f .ralph/ralph.log`
- Check plan: `cat IMPLEMENTATION_PLAN.md`
- Review commits: `git log --oneline`

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
│   ├── server.py            # Main MCP server
│   ├── nexus_client.py      # Nexus REST API client
│   └── tools/               # MCP tool implementations
├── tests/                   # Test suite
├── AGENTS.md                # Operational guide & backpressure commands
├── IMPLEMENTATION_PLAN.md   # Current tasks & progress
├── ralph-loop.sh            # Ralph Wiggum automation script
└── pyproject.toml           # Python project metadata
```

## MCP Tools
- `search_maven_artifact` - Search Maven repositories
- `get_maven_versions` - Get versions of a Maven artifact
- `search_python_package` - Search Python packages
- `get_python_versions` - Get versions of a Python package
- `list_docker_images` - List Docker images
- `get_docker_tags` - Get tags for a Docker image

## License
MIT

## Contributing
This project is auto-generated using the Ralph loop. Manual contributions welcome!
