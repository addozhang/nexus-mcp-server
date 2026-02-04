# Ralph PLANNING Loop - Nexus MCP Server Streamable-HTTP Support

## Goal
为 Nexus MCP Server 添加 streamable-http 传输模式支持，允许用户通过启动参数选择 SSE 或 streamable-http。

## Context
- 当前项目: Python FastMCP 实现的 Nexus Repository MCP 服务器
- 当前传输模式: HTTP SSE (Server-Sent Events)
- 测试覆盖: 42/42 通过
- 代码质量: mypy + ruff 全部通过

## Requirements (specs/)
阅读 `specs/*.md` 了解详细需求和约束。

## Your Task (PLANNING ONLY)
1. 阅读当前代码库结构
2. 了解 FastMCP 的 transport 参数支持
3. 分析需要修改的文件和测试
4. 创建详细的 `IMPLEMENTATION_PLAN.md`，包括：
   - 任务分解（优先级排序）
   - 文件修改列表
   - 测试策略
   - 潜在风险点

## Rules
- ❌ **DO NOT** 实现任何代码
- ❌ **DO NOT** 运行测试
- ❌ **DO NOT** 提交更改
- ✅ **ONLY** 更新 `IMPLEMENTATION_PLAN.md`
- ✅ 如果需求不清晰，在计划中写出问题

## Completion
当计划完成且可执行时，在 `IMPLEMENTATION_PLAN.md` 末尾添加：
```
STATUS: PLANNING_COMPLETE
```
