# Fix Agent Web 完整版

基于现有CLI项目的完整Web版本，提供现代化的Web界面和完整的AI代理功能。

## 🚀 快速开始

### 一键启动
```bash
./start_server.sh
```

### 手动启动
```bash
# 启动后端服务
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 测试功能
cd ..
python test_complete.py
```

### 停止服务
```bash
./stop_server.sh
```

## ✨ 核心功能

### 🔄 完整集成CLI逻辑
- **AI适配器**: 通过适配器模式完全复用CLI项目的AI代理逻辑
- **DeepAgents框架**: 支持多代理架构和HITL（人在环路）设计
- **工具系统**: 集成CLI的所有工具（代码分析、网络请求等）
- **流式响应**: 保持CLI原有的流式输出特性

### 🌐 现代化Web界面
- **RESTful API**: 完整的REST API支持
- **WebSocket通信**: 实时双向通信
- **会话管理**: 支持多会话并发
- **文件上传**: 支持项目文件上传和分析

### 💾 数据持久化
- **SQLAlchemy数据库**: 支持SQLite/PostgreSQL/MySQL
- **会话存储**: 持久化保存对话历史
- **用户管理**: 支持多用户系统（预留）
- **项目管理**: 支持多个项目管理

### 🧠 记忆系统
- **文件系统记忆**: 使用文件系统存储长期记忆
- **会话记忆**: 每个会话独立的记忆空间
- **记忆管理API**: 支持记忆的读取、写入、列表管理

## 📁 项目结构

```
web_app/
├── backend/                     # 后端API服务
│   ├── main.py                 # FastAPI应用入口
│   ├── app/
│   │   ├── api/                # API路由
│   │   │   ├── sessions.py     # 会话管理API
│   │   │   ├── files.py        # 文件上传API
│   │   │   ├── projects.py     # 项目管理API
│   │   │   ├── memory.py       # 记忆系统API
│   │   │   └── config.py       # 配置管理API
│   │   ├── core/               # 核心功能
│   │   │   ├── config.py       # 应用配置
│   │   │   └── ai_adapter.py   # AI适配器（集成CLI逻辑）
│   │   ├── models/             # 数据模型
│   │   │   ├── database.py     # 数据库模型
│   │   │   └── schemas.py      # API数据结构
│   │   ├── services/           # 业务逻辑
│   │   │   └── session_service.py  # 会话服务
│   │   └── websocket/          # WebSocket通信
│   │       ├── chat_handler.py    # 聊天处理器
│   │       └── connection_manager.py  # 连接管理
│   └── requirements.txt       # Python依赖
├── test_complete.py           # 完整功能测试
├── start_server.sh            # 启动脚本
├── stop_server.sh             # 停止脚本
└── README_COMPLETE.md         # 本文档
```

## 🔧 技术架构

### 后端技术栈
- **FastAPI**: 现代Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **WebSocket**: 实时双向通信
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI服务器

### 核心设计模式
- **适配器模式**: AI适配器桥接CLI和Web
- **依赖注入**: FastAPI的依赖系统
- **中间件架构**: 支持可插拔的中间件
- **服务层模式**: 清晰的业务逻辑分层

## 📚 API文档

启动服务后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

#### 会话管理
- `POST /api/sessions/` - 创建会话
- `GET /api/sessions/` - 获取会话列表
- `GET /api/sessions/{session_id}` - 获取会话详情
- `DELETE /api/sessions/{session_id}` - 删除会话

#### WebSocket通信
- `WS /ws/{session_id}` - 实时聊天连接

#### 文件管理
- `POST /api/files/upload` - 上传文件
- `GET /api/files/{file_id}` - 下载文件

#### 记忆系统
- `GET /api/memory/files/{session_id}` - 获取记忆文件列表
- `GET /api/memory/file/{session_id}/{file_path}` - 读取记忆文件
- `POST /api/memory/file/{session_id}/{file_path}` - 写入记忆文件

## 🧪 测试

运行完整功能测试：
```bash
python test_complete.py
```

测试包括：
- ✅ REST API健康检查
- ✅ 会话创建和管理
- ✅ WebSocket连接和通信
- ✅ AI响应流式传输
- ✅ 记忆系统操作

## 🎯 使用示例

### 1. 创建会话
```bash
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Content-Type: application/json" \
  -d '{"title": "My Session"}'
```

### 2. WebSocket聊天
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session-id');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到:', data);
};

ws.send(JSON.stringify({
    type: 'chat',
    content: '你好，Fix Agent！'
}));
```

### 3. 文件上传
```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@/path/to/file.py" \
  -F "session_id=session-id"
```

## 🔄 CLI集成状态

当前版本已完成基础架构和Web服务。CLI模块的完整集成需要：

1. **环境配置**: 确保CLI项目的环境变量正确配置
2. **依赖安装**: CLI项目的所有依赖已安装
3. **路径配置**: 确保CLI项目路径正确（`/src`目录）

当CLI模块可用时，AI适配器会自动：
- 加载DeepAgents框架
- 初始化多代理系统
- 集成所有工具和中间件
- 提供完整的AI功能

## 🛠️ 开发说明

### 环境要求
- Python 3.8+
- 现代浏览器（支持WebSocket）

### 配置说明
主要配置在 `backend/app/core/config.py`：
- 数据库连接
- API服务端口
- 文件存储路径
- AI模型配置

### 扩展开发
- 新增API路由：在 `app/api/` 目录下创建新模块
- 新增中间件：在 `app/core/` 目录下实现
- 数据库模型：在 `app/models/database.py` 中定义
- 业务逻辑：在 `app/services/` 目录下实现

## 📊 性能特性

- **异步处理**: FastAPI全异步支持
- **连接池**: 数据库连接池管理
- **流式响应**: 实时AI响应流
- **缓存机制**: 记忆系统缓存优化
- **负载均衡**: 支持多实例部署

## 🔒 安全特性

- **CORS配置**: 跨域请求控制
- **输入验证**: Pydantic数据验证
- **SQL注入防护**: SQLAlchemy ORM保护
- **文件安全**: 文件类型和大小限制

## 🚀 部署说明

### 开发环境
```bash
./start_server.sh
```

### 生产环境
```bash
# 使用Docker（推荐）
docker-compose up -d

# 或直接部署
pip install -r backend/requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📝 当前状态

### ✅ 已完成功能
- 完整的后端API服务
- WebSocket流式通信
- AI适配器架构
- 数据库持久化
- 记忆系统集成
- 文件上传功能
- 会话管理系统
- 完整的测试套件

### 🔄 进行中
- React前端界面开发
- 用户认证系统
- 项目管理功能

### 📋 后续规划
- 代码分析可视化
- 性能监控面板
- 多租户支持
- 移动端适配

---

**注意**: 这是一个完整的Web应用框架，可以独立运行。当CLI项目完全集成后，将提供完整的AI代理功能。