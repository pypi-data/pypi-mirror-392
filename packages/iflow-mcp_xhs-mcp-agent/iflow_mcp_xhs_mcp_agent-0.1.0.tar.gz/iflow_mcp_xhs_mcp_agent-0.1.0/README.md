# Xiaohongshu MCP Server | 小红书 MCP 服务器

基于 [MCP 协议](https://microsoft.github.io/mcp/) 和 FastAPI 的小红书 API 微服务。

## 功能特点

- ⚡️ **双重服务器支持**：
  - FastAPI RESTful API 服务器
  - MCP 工具集服务器
  - 同时支持 HTTP API 和 MCP 协议调用

- 🔄 **统一的客户端管理**：
  - 自动客户端生命周期管理
  - 支持多个并发客户端
  - 自动清理过期客户端

- 🛡️ **健壮的错误处理**：
  - 统一的错误处理机制
  - 详细的错误信息
  - 适当的状态码

- 📦 **模块化设计**：
  - 共享的基础组件
  - 清晰的代码组织
  - 易于扩展

## 项目结构

```
xhs_mcp_server/
├── app/
│   └── main.py           # FastAPI 应用
├── shared/
│   ├── __init__.py
│   ├── api.py           # 异步 API 客户端
│   ├── client_manager.py # 客户端管理器
│   ├── error_handler.py  # 错误处理
│   └── types.py         # 类型定义
├── mcp_server.py        # MCP 服务器
├── requirements.txt
└── README.md
```

## 环境要求

- Python 3.10+
- 依赖包：见 requirements.txt

## 安装

1. 克隆仓库：
```bash
git clone <repository-url>
cd xhs_mcp_server
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方式

### 启动 FastAPI 服务器

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API 文档可访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 启动 MCP 服务器

```bash
python mcp_server.py
```

MCP 服务器将通过标准输入/输出进行通信。

## API 端点

### 客户端管理

- `POST /clients` - 创建新客户端
- `GET /clients` - 列出所有客户端
- `DELETE /clients/{client_id}` - 删除客户端

### 笔记操作

- `POST /clients/{client_id}/note` - 获取笔记详情
- `POST /clients/{client_id}/note/html` - 从 HTML 获取笔记详情

### 搜索功能

- `POST /clients/{client_id}/search/notes` - 搜索笔记
- `POST /clients/{client_id}/search/users` - 搜索用户

### 用户操作

- `POST /clients/{client_id}/user/info` - 获取用户信息
- `POST /clients/{client_id}/user/notes` - 获取用户笔记

### Feed 功能

- `GET /clients/{client_id}/feed/categories` - 获取推荐流分类
- `GET /clients/{client_id}/feed/{feed_type}` - 获取推荐流内容

## MCP 工具集

### 基础工具

- `create_xhs_client` - 创建客户端实例
- `get_xhs_note` - 获取笔记详情
- `get_xhs_note_html` - 从 HTML 获取笔记

### 搜索工具

- `search_xhs_notes` - 搜索笔记
- `search_xhs_users` - 搜索用户

### 用户工具

- `get_xhs_user_info` - 获取用户信息
- `get_xhs_user_notes` - 获取用户笔记

### Feed 工具

- `get_xhs_feed_categories` - 获取推荐流分类
- `get_xhs_feed` - 获取推荐流内容

## 错误处理

服务器使用统一的错误处理机制：

- HTTP 状态码适当
- 详细的错误信息
- 错误类型标识
- 时间戳
- 堆栈跟踪（开发模式）

错误响应格式：

```json
{
  "status": "error",
  "error": {
    "error_type": "ErrorTypeName",
    "error": "错误描述",
    "detail": "详细信息",
    "status_code": 400,
    "timestamp": "2024-04-25T14:23:39"
  }
}
```

## 许可证

本项目仅供学习和研究使用。使用本项目时请遵守相关法律法规和平台规则。
