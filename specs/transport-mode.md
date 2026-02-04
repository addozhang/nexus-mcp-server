# Transport Mode Support Specification

## Overview
添加 streamable-http 传输模式支持，使用户可以在 SSE 和 streamable-http 之间选择。

## Functional Requirements

### FR1: Transport Type Selection
- 支持启动参数 `--transport` 选择传输模式
- 可选值: `sse` (默认), `streamable-http`
- 示例: `python -m nexus_mcp_server --transport streamable-http`

### FR2: Port Configuration
- 支持 `--port` 参数自定义端口
- 默认: 8000
- 示例: `python -m nexus_mcp_server --port 9000`

### FR3: Environment Variable Support
- 支持通过环境变量配置传输类型
- `NEXUS_MCP_TRANSPORT=streamable-http`
- 优先级: 命令行参数 > 环境变量 > 默认值

### FR4: Docker Support
- Docker 容器支持通过环境变量切换模式
- 示例: `docker run -e NEXUS_MCP_TRANSPORT=streamable-http ...`

## Non-Functional Requirements

### NFR1: Backward Compatibility
- 默认行为保持不变（SSE 模式）
- 现有用户无需修改配置
- 现有测试继续通过

### NFR2: Code Quality
- 所有新代码通过 mypy 类型检查
- 所有新代码通过 ruff 代码风格检查
- 测试覆盖率不低于现有水平（100%）

### NFR3: Documentation
- README 更新传输模式说明
- 添加使用示例
- 中英文文档同步更新

## Acceptance Criteria

1. ✅ 可以通过 `--transport sse` 启动（默认）
2. ✅ 可以通过 `--transport streamable-http` 启动
3. ✅ 两种模式都能正常处理 MCP 请求
4. ✅ 所有现有测试通过
5. ✅ 添加新传输模式的集成测试
6. ✅ mypy + ruff 检查全部通过
7. ✅ Docker 镜像支持环境变量配置
8. ✅ 文档完整准确

## Out of Scope
- WebSocket 传输支持（未来考虑）
- 多端口同时监听（未来考虑）
- 传输模式自动检测（未来考虑）
