# Implementation Plan

## Status: PLANNING_COMPLETE

---

## Gap Analysis

### Current State
- **No source code exists** - The `src/` directory and all Python files are missing
- **No `pyproject.toml`** - Project configuration needs to be created
- **No tests** - Test infrastructure needs to be set up
- **Specifications complete** - All 5 spec files define clear requirements

### Target State
- Fully functional MCP server using FastMCP
- Support for Maven, Python, and Docker repository queries
- Header-based authentication (per-request credentials)
- Comprehensive test coverage

---

## Prioritized Task List

### Phase 1: Project Foundation (Priority: Critical)

#### Task 1.1: Create Project Configuration
**Description**: Set up `pyproject.toml` with all dependencies and project metadata.

**Dependencies**: None

**Success Criteria**:
- [ ] `pyproject.toml` exists with correct metadata
- [ ] Dependencies listed: `fastmcp`, `httpx`, `pydantic`
- [ ] Dev dependencies: `pytest`, `mypy`, `ruff`
- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `python -m nexus_mcp` entry point configured

---

#### Task 1.2: Create Package Structure
**Description**: Set up the `src/nexus_mcp/` package with `__init__.py` and `__main__.py`.

**Dependencies**: Task 1.1

**Success Criteria**:
- [ ] `src/nexus_mcp/__init__.py` exists with version info
- [ ] `src/nexus_mcp/__main__.py` exists for CLI entry point
- [ ] `python -m nexus_mcp` runs (even if it does nothing yet)

---

### Phase 2: Core Infrastructure (Priority: High)

#### Task 2.1: Implement Nexus REST API Client
**Description**: Create `nexus_client.py` with httpx-based client for Nexus API.

**Dependencies**: Task 1.2

**Success Criteria**:
- [ ] `NexusClient` class accepts URL, username, password
- [ ] Uses HTTP Basic Auth for requests
- [ ] URL validation before requests
- [ ] Proper error handling for network/auth failures
- [ ] No credentials logged
- [ ] Async support using `httpx.AsyncClient`

**Open Questions**:
- Q1: Should the client support both sync and async modes, or async-only?
  - *Recommendation*: Async-only (FastMCP is async-native)

---

#### Task 2.2: Implement Authentication Context
**Description**: Create mechanism to extract credentials from MCP request headers.

**Dependencies**: Task 2.1

**Success Criteria**:
- [ ] Extracts `X-Nexus-Url`, `X-Nexus-Username`, `X-Nexus-Password` headers
- [ ] Validates URL format (must be valid HTTPS/HTTP URL)
- [ ] Returns clear error for missing credentials
- [ ] Uses FastMCP dependency injection pattern

**Open Questions**:
- Q2: Does FastMCP support request headers natively, or do we need custom middleware?
  - *Action*: Check FastMCP docs during implementation

---

#### Task 2.3: Create MCP Server Skeleton
**Description**: Set up `server.py` with FastMCP server initialization and tool registration.

**Dependencies**: Task 2.2

**Success Criteria**:
- [ ] FastMCP server instance created
- [ ] Server starts and listens for connections
- [ ] Placeholder tools registered (can be empty stubs)
- [ ] Proper logging configured
- [ ] `python -m nexus_mcp` starts the server

---

### Phase 3: Maven Support (Priority: High)

#### Task 3.1: Implement `search_maven_artifact` Tool
**Description**: MCP tool to search Maven components by groupId, artifactId, or coordinates.

**Dependencies**: Task 2.3

**Success Criteria**:
- [ ] Accepts parameters: `repository` (optional), `group_id`, `artifact_id`, `version` (optional)
- [ ] Calls Nexus REST API: `/service/rest/v1/search`
- [ ] Returns structured results: groupId, artifactId, version, format
- [ ] Handles pagination via continuation token
- [ ] Validates inputs before API call

---

#### Task 3.2: Implement `get_maven_versions` Tool
**Description**: MCP tool to get all versions of a specific Maven artifact.

**Dependencies**: Task 3.1

**Success Criteria**:
- [ ] Accepts parameters: `repository` (optional), `group_id`, `artifact_id`
- [ ] Returns list of versions (sorted, newest first)
- [ ] Includes download URLs for each version
- [ ] Handles large version lists with pagination

---

### Phase 4: Python Support (Priority: Medium)

#### Task 4.1: Implement `search_python_package` Tool
**Description**: MCP tool to search Python packages by name or keyword.

**Dependencies**: Task 2.3

**Success Criteria**:
- [ ] Accepts parameters: `repository` (optional), `name`, `keyword` (optional)
- [ ] Calls Nexus REST API with `format=pypi`
- [ ] Returns package name, version, format (wheel/sdist)
- [ ] Handles naming conventions (underscores vs hyphens)

---

#### Task 4.2: Implement `get_python_versions` Tool
**Description**: MCP tool to get all versions of a Python package.

**Dependencies**: Task 4.1

**Success Criteria**:
- [ ] Accepts parameters: `repository` (optional), `package_name`
- [ ] Returns list of versions with format info
- [ ] Includes download URLs for wheels and sdist

---

### Phase 5: Docker Support (Priority: Medium)

#### Task 5.1: Implement `list_docker_images` Tool
**Description**: MCP tool to list Docker images in a repository.

**Dependencies**: Task 2.3

**Success Criteria**:
- [ ] Accepts parameters: `repository`
- [ ] Calls Nexus REST API with `format=docker`
- [ ] Returns image names with metadata
- [ ] Handles pagination

---

#### Task 5.2: Implement `get_docker_tags` Tool
**Description**: MCP tool to get tags for a specific Docker image.

**Dependencies**: Task 5.1

**Success Criteria**:
- [ ] Accepts parameters: `repository`, `image_name`
- [ ] Returns tags with digest, size, push date
- [ ] May use Docker Registry v2 API via Nexus
- [ ] Handles multi-architecture images

**Open Questions**:
- Q3: Should we use Nexus REST API or Docker Registry v2 API for tag listing?
  - *Consideration*: Nexus REST API is more consistent, Docker v2 API provides more metadata

---

### Phase 6: Testing & Quality (Priority: High)

#### Task 6.1: Set Up Test Infrastructure
**Description**: Create `tests/` directory with pytest fixtures and mocks.

**Dependencies**: Task 1.2

**Success Criteria**:
- [ ] `tests/conftest.py` with common fixtures
- [ ] Mock Nexus API responses using `respx` or `httpx` mocking
- [ ] Test client for MCP server
- [ ] `pytest tests/ -v` runs successfully

---

#### Task 6.2: Unit Tests for NexusClient
**Description**: Test the Nexus API client in isolation.

**Dependencies**: Task 6.1, Task 2.1

**Success Criteria**:
- [ ] Tests for successful API calls
- [ ] Tests for auth failures (401)
- [ ] Tests for network errors
- [ ] Tests for invalid URL handling

---

#### Task 6.3: Integration Tests for MCP Tools
**Description**: Test each MCP tool end-to-end with mocked Nexus API.

**Dependencies**: Task 6.2, All Tool Tasks

**Success Criteria**:
- [ ] Each tool has at least 2 test cases
- [ ] Tests cover happy path and error cases
- [ ] Tests verify response structure

---

#### Task 6.4: Type Checking and Linting
**Description**: Ensure all code passes mypy and ruff checks.

**Dependencies**: All implementation tasks

**Success Criteria**:
- [ ] `mypy src/` passes with no errors
- [ ] `ruff check src/ tests/` passes with no errors
- [ ] All functions have type annotations

---

### Phase 7: Documentation & Deployment (Priority: Low)

#### Task 7.1: Update README with Usage Instructions
**Description**: Document how to configure and use the MCP server.

**Dependencies**: All implementation tasks

**Success Criteria**:
- [ ] Installation instructions
- [ ] Configuration via headers explained
- [ ] Example MCP client configuration
- [ ] Troubleshooting section

---

#### Task 7.2: Verify Dockerfile
**Description**: Ensure Dockerfile works for sandboxed execution.

**Dependencies**: Task 2.3

**Success Criteria**:
- [ ] `docker build .` succeeds
- [ ] Container runs the MCP server
- [ ] Health check works

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
