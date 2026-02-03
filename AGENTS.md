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
*(Will be updated during BUILDING iterations)*

- Add learnings about Nexus API quirks here
- Document any authentication edge cases
- Note performance considerations
