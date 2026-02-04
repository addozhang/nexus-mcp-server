# Ralph BUILDING Loop - Nexus MCP Server Streamable-HTTP Support

## Goal
实现 Nexus MCP Server 的 streamable-http 传输模式支持。

## Context Files
- `specs/*.md` - 功能规格和约束
- `IMPLEMENTATION_PLAN.md` - 实施计划和任务列表
- `AGENTS.md` - 测试命令和操作指南

## Your Task (每次迭代)
1. **选择任务**: 从 `IMPLEMENTATION_PLAN.md` 选择优先级最高的未完成任务
2. **调查代码**: 阅读相关文件，理解现有实现
3. **实现变更**: 编写清晰、可测试的代码
4. **运行反压测试**: 执行 `AGENTS.md` 中的测试命令
   - pytest 单元测试
   - mypy 类型检查
   - ruff 代码质量检查
5. **更新计划**: 标记任务完成状态，记录发现的问题
6. **更新 AGENTS.md**: 记录学到的经验、常见错误、最佳实践
7. **提交**: 使用清晰的 commit message

## Backpressure Commands
参考 `AGENTS.md` 中的命令：
```bash
pytest tests/ -v
mypy src/
ruff check src/
```

## Completion
当所有任务完成并通过测试后，在 `IMPLEMENTATION_PLAN.md` 末尾添加：
```
STATUS: COMPLETE
```

## Rules
- ✅ 每次只做一个任务
- ✅ 先写测试，再写实现（TDD）
- ✅ 保持向后兼容（默认 SSE）
- ✅ 提交前必须通过所有测试
- ❌ 不要跳过反压测试
- ❌ 不要提交未测试的代码
