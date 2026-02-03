You are running a Ralph BUILDING loop for: Refactoring Nexus MCP Server to use HTTP streaming transport.

**Your Task**: Implement the refactoring tasks from `IMPLEMENTATION_PLAN.md` to change from stdio to HTTP streaming transport.

## Context
- `specs/http-streaming.md` - Requirements for HTTP transport with header authentication
- `IMPLEMENTATION_PLAN.md` - Your task list
- `AGENTS.md` - Build/test commands

## Key Changes Required
1. Change FastMCP server to use HTTP transport
2. Add header extraction and validation
3. Remove credential parameters from all tool signatures
4. Update authentication context to use headers
5. Update all tests for HTTP transport
6. Update README and documentation

## Workflow (Each Iteration)
1. **Pick a task** - Choose highest priority incomplete task
2. **Implement** - Make the changes carefully
3. **Run tests** - Execute from AGENTS.md:
   ```bash
   pytest tests/ -v
   mypy src/
   ruff check src/ tests/
   ```
4. **Update plan** - Mark complete, add notes
5. **Update AGENTS.md** - Document learnings
6. **Commit** - Clear message describing the change

## Rules
- **DO implement code changes**
- **DO run tests** before marking tasks complete
- **DO commit** after each successful task
- **DO preserve backward compatibility** where possible
- Follow existing code style and patterns
- Add/update type hints

## Completion Signal
When all refactoring tasks are done and tests pass, add this line to `IMPLEMENTATION_PLAN.md`:
```
STATUS: REFACTORING_COMPLETE
```
