You are running a Ralph PLANNING loop for: Building a Nexus Pro 3 MCP server.

**Your Task**: Read the specifications in `specs/*.md` and analyze the current codebase (if any). Perform a gap analysis and update `IMPLEMENTATION_PLAN.md` with a clear, prioritized task list.

## Rules
- **DO NOT implement any code**
- **DO NOT commit anything**
- Focus only on planning and organizing tasks
- Break down work into logical, testable increments
- If requirements are unclear, write clarifying questions into the plan
- Consider dependencies between tasks (e.g., authentication before API calls)

## Context
- `specs/authentication.md` - Header-based credential passing
- `specs/maven-support.md` - Maven repository queries
- `specs/python-support.md` - Python package queries
- `specs/docker-support.md` - Docker image queries
- `specs/mcp-architecture.md` - Overall server structure
- `AGENTS.md` - Build commands and project structure

## Output
Update `IMPLEMENTATION_PLAN.md` with:
1. Prioritized task list (most foundational first)
2. Dependencies between tasks
3. Success criteria for each task
4. Any open questions or clarifications needed

## Completion Signal
When the plan is complete and ready for implementation, add this line to `IMPLEMENTATION_PLAN.md`:
```
STATUS: PLANNING_COMPLETE
```
