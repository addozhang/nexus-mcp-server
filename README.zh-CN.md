# Nexus MCP Server

[English](README.md) | 简体中文

适用于 Sonatype Nexus Repository Manager 3（OSS 和 Pro 版本）的 MCP (Model Context Protocol) 服务器，让 AI 助手能够查询 Maven、Python (PyPI) 和 Docker 仓库。

## 功能特性
- 🚀 **多种传输模式** - SSE（默认）或 streamable-http 传输
- 🌐 **HTTP 流式传输** - 基于 SSE 的现代化传输，支持 HTTP 头认证
- 🔐 **按请求认证** - 凭证通过 HTTP 头传递（无需硬编码密钥）
- 📦 **Maven 支持** - 搜索制品、列出版本、获取元数据
- 🐍 **Python 支持** - 搜索包、列出版本、获取元数据
- 🐳 **Docker 支持** - 列出镜像、获取标签、镜像元数据
- ⚡ **FastMCP 框架** - 快速、现代化的 Python 实现


## 兼容性

**支持的 Nexus 版本：**
- ✅ Nexus Repository Manager 3.x OSS（开源版）
- ✅ Nexus Repository Manager 3.x Pro（专业版）

本服务器使用标准的 Nexus REST API v1 (`/service/rest/v1`)，该 API 在 OSS 和 Pro 版本中都可用。

## 可用工具

本 MCP 服务器提供 **6 个只读工具**用于查询 Nexus 仓库：

### 📦 Maven 工具
| 工具 | 说明 | 参数 |
|------|------|------|
| `search_maven_artifact` | 搜索 Maven 制品 | `group_id`, `artifact_id`, `version`, `repository` |
| `get_maven_versions` | 获取 Maven 制品的所有版本（分页） | `group_id`, `artifact_id`, `repository`, `page_size`, `continuation_token` |

### 🐍 Python/PyPI 工具
| 工具 | 说明 | 参数 |
|------|------|------|
| `search_python_package` | 搜索 Python 包 | `name`, `repository` |
| `get_python_versions` | 获取 Python 包的所有版本（分页） | `package_name`, `repository`, `page_size`, `continuation_token` |

### 🐳 Docker 工具
| 工具 | 说明 | 参数 |
|------|------|------|
| `list_docker_images` | 列出仓库中的所有 Docker 镜像 | `repository` |
| `get_docker_tags` | 获取 Docker 镜像的所有标签 | `repository`, `image_name` |

**注意：** 所有工具都是只读的，使用安全。不支持写操作（创建/更新/删除）。
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
# 快速启动
docker run -p 8000:8000 addozhang/nexus-mcp-server:latest

# 或使用 docker-compose
docker-compose up

# 详细部署指南请参阅 DOCKER.md
```

详细部署指南请参阅 [DOCKER.md](DOCKER.md)。

## 配置

### 服务器配置
服务器可通过命令行参数或环境变量进行配置：

| 变量 | 命令行参数 | 描述 | 默认值 |
|------|-----------|------|--------|
| `NEXUS_MCP_HOST` | `--host` | 绑定的主机地址 | `0.0.0.0` |
| `NEXUS_MCP_PORT` | `--port` | 监听端口 | `8000` |
| `NEXUS_MCP_TRANSPORT` | `--transport` | 传输模式（`sse` 或 `streamable-http`）| `sse` |

**优先级：** 命令行参数 > 环境变量 > 默认值

**传输模式：**
- `sse`（默认）- Server-Sent Events 传输，兼容大多数 MCP 客户端
- `streamable-http` - Streamable HTTP 传输，适用于偏好此协议的客户端

### 运行服务器

#### 本地开发
```bash
# SSE 模式（默认）
python -m nexus_mcp

# Streamable-HTTP 模式
python -m nexus_mcp --transport streamable-http

# 自定义端口
python -m nexus_mcp --port 9000

# 自定义主机和端口
python -m nexus_mcp --host 127.0.0.1 --port 9000
```

#### 使用 Docker
```bash
# SSE 模式（默认）
docker run -p 8000:8000 addozhang/nexus-mcp-server:latest

# Streamable-HTTP 模式
docker run -e NEXUS_MCP_TRANSPORT=streamable-http -p 8000:8000 addozhang/nexus-mcp-server:latest

# 自定义端口
docker run -e NEXUS_MCP_PORT=9000 -p 9000:9000 addozhang/nexus-mcp-server:latest

# 或使用 docker-compose
docker-compose up

# 详细部署指南请参阅 DOCKER.md
```

详细部署指南请参阅 [DOCKER.md](DOCKER.md)。

### 通过 HTTP 头认证
凭证通过每个请求的 HTTP 头传递：

| 头 | 描述 | 示例 | 必需 |
|------|------|------|------|
| `X-Nexus-Url` | Nexus 实例 URL | `https://nexus.company.com` | 是 |
| `X-Nexus-Username` | 用户名 | `admin` | 是 |
| `X-Nexus-Password` | 密码 | `secret123` | 是 |
| `X-Nexus-Verify-SSL` | 验证 SSL 证书 | `false` | 否（默认：`true`）|

**注意**：连接使用自签名证书的自托管 Nexus 实例时，设置 `X-Nexus-Verify-SSL: false`。

### MCP 客户端配置（Claude Desktop）
添加到 Claude Desktop 配置文件 (`~/.config/claude/claude_desktop_config.json`)：

```json
{
  "mcpServers": {
    "nexus": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "X-Nexus-Url": "https://nexus.company.com",
        "X-Nexus-Username": "admin",
        "X-Nexus-Password": "secret123"
      }
    }
  }
}
```

对于自签名证书：
```json
{
  "mcpServers": {
    "nexus": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "X-Nexus-Url": "https://nexus.company.com",
        "X-Nexus-Username": "admin",
        "X-Nexus-Password": "secret123",
        "X-Nexus-Verify-SSL": "false"
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
| `get_maven_versions` | 获取制品的版本（分页） | `group_id`, `artifact_id`, `repository`, `page_size`（默认 50）, `continuation_token` |

**分页示例**：
```python
# 第一页
response = get_maven_versions("com.example", "myapp")
# response 包含：versions, hasMore, continuationToken（如果 hasMore 为 true）

# 下一页
if response["hasMore"]:
    next_response = get_maven_versions(
        "com.example", 
        "myapp", 
        continuation_token=response["continuationToken"]
    )
```

**搜索示例**：
```python
# 搜索 Spring Boot
search_maven_artifact(
    group_id="org.springframework.boot",
    artifact_id="spring-boot-starter",
    repository="maven-central"
)
```

### Python 工具
| 工具 | 描述 | 参数 |
|------|------|------|
| `search_python_package` | 搜索 Python 包 | `name`, `repository` |
| `get_python_versions` | 获取包的版本（分页） | `package_name`, `repository`, `page_size`（默认 50）, `continuation_token` |

**分页说明**：与 Maven 相同 - 检查 `hasMore` 并使用 `continuationToken` 获取后续页面。

**示例**：
```python
# 搜索 requests 包
search_python_package(
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
│   ├── mcp-architecture.md   # MCP 架构
│   └── http-streaming.md     # HTTP 流式传输
├── src/nexus_mcp/           # 源代码
│   ├── __init__.py          # 包初始化（含版本号）
│   ├── __main__.py          # CLI 入口点
│   ├── server.py            # FastMCP 服务器及工具定义
│   ├── nexus_client.py      # Nexus REST API 客户端
│   ├── auth.py              # 认证类型定义
│   ├── dependencies.py      # 从请求头提取凭证
│   └── tools/               # 工具实现
│       ├── __init__.py
│       └── implementations.py
├── tests/                   # 测试套件
│   ├── conftest.py          # 测试夹具和样本数据
│   ├── test_nexus_client.py # 客户端单元测试
│   ├── test_tools.py        # 工具集成测试
│   └── test_http_transport.py # HTTP 传输测试
├── AGENTS.md                # 运维指南
├── IMPLEMENTATION_PLAN.md   # 任务跟踪
└── pyproject.toml           # Python 项目元数据
```

## 故障排查

### 连接错误
- 验证 MCP 服务器正在运行 (`python -m nexus_mcp`)
- 检查端口 8000 是否可访问
- 验证 `X-Nexus-Url` 头正确且可访问
- 检查到 Nexus 实例的网络连接
- 确保 HTTPS 证书有效（或对本地实例使用 HTTP）

### 认证错误
- 验证 `X-Nexus-Username` 和 `X-Nexus-Password` 头正确
- 确保用户对仓库有读取权限
- 检查 Nexus 实例是否需要特定认证方法

### 缺少凭证错误
- 确保设置了所有三个头：`X-Nexus-Url`、`X-Nexus-Username`、`X-Nexus-Password`
- 检查 MCP 客户端是否支持 HTTP 头

### 空结果
- 验证仓库名称正确
- 检查包/制品在 Nexus 中是否存在
- 对于 Python 包，尝试使用连字符和下划线两种命名方式

### 传输模式问题
**使用 streamable-http 时连接超时：**
- 确保客户端支持 streamable-http 传输
- 尝试改用 SSE 模式：`python -m nexus_mcp --transport sse`
- 检查防火墙规则是否允许 HTTP 连接

**工具未显示：**
- SSE 和 streamable-http 两种模式暴露相同的工具
- 验证是否正确传递了头（X-Nexus-*）
- 检查服务器日志中的认证错误

## 技术栈
- **Python 3.10+** - 现代 Python 特性
- **FastMCP** - MCP 服务器框架
- **httpx** - 异步 HTTP 客户端
- **pydantic** - 数据验证
- **pytest** - 测试框架

## 限制说明
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
