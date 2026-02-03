You are running a Ralph PLANNING loop for: Refactoring Nexus MCP Server to use HTTP streaming transport.

**Your Task**: Read the new specification in `specs/http-streaming.md` and analyze the required changes. Update `IMPLEMENTATION_PLAN.md` with a clear task list for this refactoring.

## Context
- **Current state**: Working MCP server using stdio transport with credentials as tool parameters
- **Target state**: HTTP streaming (SSE) transport with credentials in headers
- **New spec**: `specs/http-streaming.md` - Detailed requirements for the change
- **Original specs**: Still valid, only transport mechanism changes

## Rules
- **DO NOT implement any code**
- **DO NOT commit anything**
- Focus only on planning the refactoring tasks
- Consider backward compatibility if needed
- Update existing IMPLEMENTATION_PLAN.md or create a new section
- Mark original tasks as [COMPLETED] if needed

## Analysis Required
1. Read current implementation (src/nexus_mcp/server.py, auth.py)
2. Understand FastMCP HTTP transport capabilities
3. Identify all places that need changes (server, tools, tests, docs)
4. Plan testing strategy for HTTP transport
5. Consider migration path for existing users

## Output
Update `IMPLEMENTATION_PLAN.md` with:
1. New prioritized task list for refactoring
2. Dependencies between tasks
3. Testing requirements
4. Documentation updates needed
5. Any risks or open questions

## Completion Signal
When the refactoring plan is complete, add this line to `IMPLEMENTATION_PLAN.md`:
```
STATUS: REFACTORING_PLAN_COMPLETE
```
