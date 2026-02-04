# Testing Strategy

## Test Levels

### Unit Tests
- 参数解析逻辑（argparse + 环境变量）
- 传输模式选择逻辑
- 默认值处理

### Integration Tests
- SSE 模式端到端测试（现有）
- Streamable-HTTP 模式端到端测试（新增）
- 错误处理测试

### Smoke Tests
- 服务器启动成功
- 健康检查端点响应
- 基本 MCP 请求/响应

## Test Coverage Goals
- 行覆盖率: ≥95%
- 分支覆盖率: ≥90%
- 关键路径: 100%

## Test Commands (Backpressure)

```bash
# 运行所有测试
pytest tests/ -v --cov=nexus_mcp_server --cov-report=term-missing

# 类型检查
mypy src/nexus_mcp_server --strict

# 代码风格
ruff check src/ tests/

# 快速验证
pytest tests/ -v -k "test_transport"
```

## Test Data
- 使用 pytest fixtures 模拟 Nexus API 响应
- 使用 mock 隔离外部依赖
- 不依赖真实 Nexus 实例

## Test Isolation
- 每个测试独立运行
- 不共享状态
- 可并行执行（pytest-xdist）

## Edge Cases to Test
1. 无效的 transport 参数值
2. 端口冲突
3. 缺少必需的环境变量（Nexus URL/凭据）
4. 网络超时
5. 大响应数据
6. 并发请求
