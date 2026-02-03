# Nexus MCP Server

[English](README.md) | 简体中文

适用于 Sonatype Nexus Pro 3 的 MCP (Model Context Protocol) 服务器，让 AI 助手能够查询 Maven、Python (PyPI) 和 Docker 仓库。

## 功能特性
- 🔐 **按请求认证** - 凭证通过工具参数传递（无需硬编码密钥）
- 📦 **Maven 支持** - 搜索制品、列出版本、获取元数据
- 🐍 **Python 支持** - 搜索包、列出版本、获取元数据
- 🐳 **Docker 支持** - 列出镜像、获取标签、镜像元数据
- ⚡ **FastMCP 框架** - 快速、现代化的 Python 实现

## 安装

### 从源码安装
```bash
# 克隆仓库
git clone https://github.com/addozhang/nexus-mcp-server.git
cd nexus-mcp-server

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # 或 venv/bin/activate.fish

# 开发模式安装
pip install -e ".[dev]"

# 运行服务器
python -m nexus_mcp
```

### 使用 Docker
```bash
docker build -t nexus-mcp-server .
docker run -it nexus-mcp-server python -m nexus_mcp
```

## 配置

### 认证方式
与基于 HTTP 的 API 不同，MCP 使用 stdio 传输，不支持 HTTP 头。凭证作为参数传递给每个工具调用：

| 参数 | 描述 | 示例 |
|------|------|------|
| `nexus_url` | Nexus 实例 URL | `https://nexus.company.com` |
| `nexus_username` | 用户名 | `admin` |
| `nexus_password` | 密码 | `secret123` |

### MCP 客户端配置（Claude Desktop）
添加到 Claude Desktop 配置文件 (`~/.config/claude/claude_desktop_config.json`)：

```json
{
  "mcpServers": {
    "nexus": {
      "command": "python",
      "args": ["-m", "nexus_mcp"],
      "cwd": "/path/to/nexus-mcp-server",
      "env": {
        "PATH": "/path/to/nexus-mcp-server/venv/bin:$PATH"
      }
    }
  }
}
```

## MCP 工具

### Maven 工具
| 工具 | 描述 | 参数 |
|------|------|------|
| `search_maven_artifact` | 搜索 Maven 仓库 | `group_id`, `artifact_id`, `version`, `repository` |
| `get_maven_versions` | 获取制品的所有版本 | `group_id`, `artifact_id`, `repository` |

**示例**：
```python
# 搜索 Spring Boot
search_maven_artifact(
    nexus_url="https://nexus.example.com",
    nexus_username="user",
    nexus_password="pass",
    group_id="org.springframework.boot",
    artifact_id="spring-boot-starter",
    repository="maven-central"
)
```

### Python 工具
| 工具 | 描述 | 参数 |
|------|------|------|
| `search_python_package` | 搜索 Python 包 | `name`, `repository` |
| `get_python_versions` | 获取包的所有版本 | `package_name`, `repository` |

**示例**：
```python
# 搜索 requests 包
search_python_package(
    nexus_url="https://nexus.example.com",
    nexus_username="user",
    nexus_password="pass",
    name="requests",
    repository="pypi-proxy"
)
```

### Docker 工具
| 工具 | 描述 | 参数 |
|------|------|------|
| `list_docker_images` | 列出仓库中的镜像 | `repository` |
| `get_docker_tags` | 获取镜像的标签 | `repository`, `image_name` |

**示例**：
```python
# 列出 Docker 镜像
list_docker_images(
    nexus_url="https://nexus.example.com",
    nexus_username="user",
    nexus_password="pass",
    repository="docker-hosted"
)
```

## 开发

### 运行测试
```bash
pytest tests/ -v
```

### 类型检查
```bash
mypy src/
```

### 代码检查
```bash
ruff check src/ tests/
```

### 自动修复
```bash
ruff check --fix src/ tests/
```

## 项目结构
```
nexus-mcp-server/
├── specs/                    # 需求文档
│   ├── authentication.md     # 认证规范
│   ├── maven-support.md      # Maven 支持
│   ├── python-support.md     # Python 支持
│   ├── docker-support.md     # Docker 支持
│   └── mcp-architecture.md   # MCP 架构
├── src/nexus_mcp/           # 源代码
│   ├── __init__.py          # 包初始化（含版本号）
│   ├── __main__.py          # CLI 入口点
│   ├── server.py            # FastMCP 服务器及工具定义
│   ├── nexus_client.py      # Nexus REST API 客户端
│   ├── auth.py              # 认证类型定义
│   └── tools/               # 工具实现
│       ├── __init__.py
│       └── implementations.py
├── tests/                   # 测试套件
│   ├── conftest.py          # 测试夹具和样本数据
│   ├── test_nexus_client.py # 客户端单元测试
│   └── test_tools.py        # 工具集成测试
├── AGENTS.md                # 运维指南
├── IMPLEMENTATION_PLAN.md   # 任务跟踪
└── pyproject.toml           # Python 项目元数据
```

## 故障排查

### 连接错误
- 验证 `nexus_url` 正确且可访问
- 检查到 Nexus 实例的网络连接
- 确保 HTTPS 证书有效（或对本地实例使用 HTTP）

### 认证错误
- 验证用户名和密码正确
- 确保用户对仓库有读取权限
- 检查 Nexus 实例是否需要特定认证方法

### 空结果
- 验证仓库名称正确
- 检查包/制品在 Nexus 中是否存在
- 对于 Python 包，尝试使用连字符和下划线两种命名方式

### MCP 客户端问题
- 确保 Python 虚拟环境路径正确
- 检查 `python -m nexus_mcp` 可以独立运行
- 查看 Claude Desktop 日志了解详细错误信息

## 技术栈
- **Python 3.10+** - 现代 Python 特性
- **FastMCP** - MCP 服务器框架
- **httpx** - 异步 HTTP 客户端
- **pydantic** - 数据验证
- **pytest** - 测试框架

## 限制说明
- **MCP 协议限制**：不支持 HTTP 头，凭证必须通过工具参数传递
- **Nexus API**：依赖 Nexus REST API v1（Nexus 3.x）
- **认证方式**：目前仅支持 HTTP Basic Auth

## 开发历史
本项目使用 **Ralph Wiggum Loop** 自动化开发流程，由 OpenCode + Claude Opus 4.5 在 27 分钟内完成：
- 规划：5 轮迭代生成 17 个任务
- 实现：自动完成所有任务、测试和文档
- 质量：26 个测试全部通过，类型检查和代码规范检查无错误

## 许可证
MIT

## 贡献
欢迎贡献！请在提交 PR 前运行测试和代码检查。

## 相关链接
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [Nexus Repository Manager](https://www.sonatype.com/products/nexus-repository)
- [Anthropic Claude](https://www.anthropic.com/claude)
