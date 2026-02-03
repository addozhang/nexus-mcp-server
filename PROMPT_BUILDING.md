You are running a Ralph BUILDING loop for: Building a Nexus Pro 3 MCP server.

**Your Task**: Implement tasks from `IMPLEMENTATION_PLAN.md`, run tests, and update documentation as you learn.

## Context
- `specs/*.md` - Detailed requirements for each component
- `IMPLEMENTATION_PLAN.md` - Your task list and progress tracker
- `AGENTS.md` - Build/test commands and operational learnings

## Workflow (Each Iteration)
1. **Pick a task** - Choose the highest priority incomplete task from `IMPLEMENTATION_PLAN.md`
2. **Investigate** - Check existing code; don't assume files are missing
3. **Implement** - Write code, following Python best practices
4. **Run backpressure** - Execute test/lint commands from `AGENTS.md`:
   ```bash
   pytest tests/ -v
   mypy src/
   ruff check src/ tests/
   ```
5. **Update plan** - Mark task as complete, add notes/learnings
6. **Update AGENTS.md** - Document any new operational details (API quirks, gotchas)
7. **Commit** - Commit with a clear, descriptive message

## Rules
- **DO implement code**
- **DO run tests** before marking tasks complete
- **DO commit** after each successful task
- **DO update** `IMPLEMENTATION_PLAN.md` with progress
- Follow the structure defined in `AGENTS.md`
- Handle errors gracefully
- Add type hints and docstrings

## Completion Signal
When all tasks are done and tests pass, add this line to `IMPLEMENTATION_PLAN.md`:
```
STATUS: COMPLETE
```
