# Nexus MCP Server - Agent Operational Guide

## Project Overview
Python FastMCP 实现的 Sonatype Nexus Repository MCP 服务器。

## Current State
- Transport: HTTP SSE (default) or Streamable-HTTP
- Tests: 59/59 passing (17 new transport tests added)
- Code Quality: mypy + ruff all passing
- Docker: Multi-arch support (amd64 + arm64)

## Backpressure Commands (必须每次运行)

### 运行测试
```bash
# 所有测试
pytest tests/ -v

# 带覆盖率
pytest tests/ -v --cov=nexus_mcp_server --cov-report=term-missing

# 特定测试
pytest tests/test_server.py::test_transport_selection -v
```

### 类型检查
```bash
mypy src/nexus_mcp_server --strict
```

### 代码风格检查
```bash
# 检查
ruff check src/ tests/

# 自动修复
ruff check --fix src/ tests/
```

### 完整验证（提交前必须）
```bash
pytest tests/ -v && mypy src/ --strict && ruff check src/ tests/
```

## Project Structure
```
nexus-mcp-server/
├── src/nexus_mcp_server/
│   ├── __init__.py
│   ├── __main__.py      # 启动入口
│   ├── server.py        # MCP 服务器逻辑
│   └── nexus_client.py  # Nexus API 客户端
├── tests/
│   ├── test_server.py
│   ├── test_nexus_client.py
│   └── conftest.py      # pytest fixtures
├── specs/               # 功能规格
├── Dockerfile
├── pyproject.toml       # 依赖和配置
└── README.md
```

## Common Operations

### 本地开发运行
```bash
# SSE 模式（默认）
python -m nexus_mcp_server

# Streamable-HTTP 模式
python -m nexus_mcp_server --transport streamable-http

# 自定义端口
python -m nexus_mcp_server --port 9000
```

### Docker 运行
```bash
# 构建
docker build -t nexus-mcp-server .

# 运行 SSE
docker run -p 8000:8000 nexus-mcp-server

# 运行 Streamable-HTTP
docker run -e NEXUS_MCP_TRANSPORT=streamable-http -p 8000:8000 nexus-mcp-server
```

## Git Workflow
```bash
# 提交前检查
git status
git diff

# 提交（清晰的 message）
git add <files>
git commit -m "feat: add streamable-http transport support"

# 推送
git push origin main
```

## Debugging Tips
1. 使用 `pytest -vv` 查看详细输出
2. 使用 `pytest --pdb` 在失败时进入调试器
3. 检查 `pyproject.toml` 的依赖版本
4. FastMCP 文档: https://github.com/jlowin/fastmcp

## Lessons Learned
### Transport Mode Implementation (Feb 2026) ✅ COMPLETE
**Status**: Implementation complete (commit 6f805d6)

**Key Decisions**:
1. **Argparse Priority**: Environment variables in argparse defaults work correctly with `os.environ.get()` - CLI args automatically override them
2. **Testing Strategy**: Mock `mcp.run()` to verify arguments without starting actual server
3. **Ruff Auto-fix**: Use `--unsafe-fixes` flag to auto-fix whitespace issues in existing code
4. **Test Count**: Added 17 new tests for transport parameter parsing, bringing total from 42 to 59
5. **Backward Compatibility**: All existing tests passed without modification - default SSE behavior preserved

**Best Practices**:
- Always use `patch("sys.argv")` and `patch.dict(os.environ)` for testing CLI args
- Mock `mcp.run()` instead of starting actual server in unit tests
- Test priority order: CLI > ENV > Default
- Test invalid input rejection with `pytest.raises(SystemExit)`
- Keep default behavior unchanged for backward compatibility

---

**Note**: 每次实施任务后，更新本文件记录新的经验和注意事项。
