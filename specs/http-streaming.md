# HTTP Streaming Transport Change

## Requirement
Change MCP server from stdio transport to HTTP streaming (SSE - Server-Sent Events) to support HTTP headers for authentication.

## Current Implementation
- Transport: stdio
- Authentication: Passed as tool parameters (nexus_url, nexus_username, nexus_password)
- Problem: Every tool call requires credentials as parameters

## Target Implementation
- Transport: HTTP streaming (SSE)
- Authentication: HTTP headers (X-Nexus-Url, X-Nexus-Username, X-Nexus-Password)
- Benefit: Credentials passed once in request headers, cleaner tool signatures

## Technical Details

### FastMCP HTTP Support
FastMCP supports multiple transports including HTTP SSE. Need to:
1. Change server initialization to use HTTP transport
2. Add header extraction middleware
3. Store credentials in request context
4. Remove credential parameters from tool signatures

### API Changes
**Before** (stdio):
```python
async def search_maven_artifact(
    nexus_url: str,
    nexus_username: str,
    nexus_password: str,
    group_id: str,
    artifact_id: str,
    ...
)
```

**After** (HTTP streaming):
```python
async def search_maven_artifact(
    group_id: str,
    artifact_id: str,
    ...
    # Credentials from headers via context
)
```

### Client Configuration Changes
**Before**:
```json
{
  "mcpServers": {
    "nexus": {
      "command": "python",
      "args": ["-m", "nexus_mcp"]
    }
  }
}
```

**After**:
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

## Success Criteria
- [x] Server runs on HTTP with SSE transport
- [x] Headers extracted and validated
- [x] All tools work without credential parameters
- [x] All tests updated and passing
- [x] Documentation reflects HTTP transport
- [x] README examples updated

## Implementation Status: COMPLETE

All requirements have been implemented:
- Server uses `mcp.run(transport="sse")` for HTTP streaming
- Headers extracted via `get_http_request()` from FastMCP
- All 6 tools updated to use dependency injection for credentials
- 36 tests passing (10 new for HTTP transport)
- README updated with HTTP configuration examples

## References
- FastMCP HTTP transport documentation
- MCP SSE transport specification
- Original authentication.md requirements
