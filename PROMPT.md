# Nexus MCP Server

Build an MCP (Model Context Protocol) server for Sonatype Nexus Pro 3 that enables LLMs to query Maven, Python, and Docker repositories.

## Goal (JTBD)
Enable AI assistants to search and retrieve artifact information from Nexus repositories without hardcoded credentials. Credentials are passed per-request via headers.

## Context Files
- **Specifications**: `specs/*.md` - Detailed requirements for each component
- **Implementation Plan**: `IMPLEMENTATION_PLAN.md` - Current tasks and progress
- **Operational Guide**: `AGENTS.md` - Tests, build commands, learnings

## Architecture
- **Language**: Python
- **Framework**: FastMCP
- **Authentication**: Per-request headers (X-Nexus-Url, X-Nexus-Username, X-Nexus-Password)
- **Supported Formats**: Maven, Python (PyPI), Docker

## Development Approach
This project uses the Ralph Wiggum loop:
1. **PLANNING phase** - Read specs, analyze gaps, create/update implementation plan
2. **BUILDING phase** - Implement tasks, run tests, update plan, commit

---

**Current Mode**: Will be set by ralph-loop.sh script (PLANNING or BUILDING)
