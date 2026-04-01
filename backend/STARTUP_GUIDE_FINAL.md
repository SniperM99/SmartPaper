# SmartPaper 后端启动指南（最终版）

## 一、快速启动（推荐）

### 方式 1：使用启动脚本

```bash
cd /Users/m99/Documents/SmartPaper/backend
./start_backend.sh
```

### 方式 2：手动启动

```bash
# 进入后端目录
cd /Users/m99/Documents/SmartPaper/backend

# 激活虚拟环境
source ../.venv/bin/activate

# 设置 PYTHONPATH（重要！）
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 二、依赖安装

### 自动安装依赖

```bash
cd /Users/m99/Documents/SmartPaper/backend
./install_deps.sh
```

### 手动安装依赖

```bash
cd /Users/m99/Documents/SmartPaper
source .venv/bin/activate

# FastAPI 基础依赖
pip install fastapi uvicorn python-multipart

# 数据验证
pip install pydantic pydantic-settings

# 异步支持
pip install httpx aiofiles

# CORS
pip install python-cors

# 数据库
pip install sqlalchemy aiosqlite alembic

# 认证和授权
pip install 'python-jose[cryptography]' 'passlib[bcrypt]'

# 工具库
pip install python-dotenv loguru

# 速率限制
pip install slowapi

# 邮箱验证
pip install email-validator
```

---

## 三、环境配置

创建 `.env` 文件（如果不存在）：

```bash
# 应用配置
ENV=development
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./smartpaper.db

# JWT 密钥（生产环境请使用强密钥）
SECRET_KEY=smartpaper-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 配置
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8080

# LLM 配置（可选）
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o

ZHIPUAI_API_KEY=your-zhipuai-api-key
ZHIPUAI_MODEL=glm-4

# Zotero 配置（可选）
ZOTERO_API_KEY=your-zotero-api-key
ZOTERO_USER_ID=your-zotero-user-id
```

---

## 四、验证启动成功

看到以下输出表示启动成功：

```
INFO:     Will watch for changes in these directories: ['/Users/m99/Documents/SmartPaper/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 五、访问后端

### 健康检查

```bash
curl http://localhost:8000/health
```

### API 文档

- Swagger UI：http://localhost:8000/api/docs
- ReDoc：http://localhost:8000/api/redoc
- OpenAPI JSON：http://localhost:8000/api/openapi.json

---

## 六、常见问题

### 1. ModuleNotFoundError: No module named 'application'

**原因**：未设置 PYTHONPATH

**解决**：
```bash
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH
```

### 2. ModuleNotFoundError: No module named 'jose'

**原因**：未安装 python-jose

**解决**：
```bash
pip install 'python-jose[cryptography]'
```

### 3. ModuleNotFoundError: No module named 'aiosqlite'

**原因**：未安装 aiosqlite

**解决**：
```bash
pip install aiosqlite
```

### 4. ModuleNotFoundError: No module named 'slowapi'

**原因**：未安装 slowapi

**解决**：
```bash
pip install slowapi
```

### 5. TypeError: 'ALLOWED_ORIGINS' is not a list

**原因**：环境变量格式错误

**解决**：
在 `.env` 文件中使用逗号分隔的字符串：
```
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8080
```

---

## 七、项目依赖关系

```
SmartPaper/
├── backend/app/           # FastAPI 后端
│   └── main.py           # 主应用入口
├── application/           # 应用编排层（被后端引用）
├── domain/               # 领域模型（被后端引用）
├── infrastructure/       # 基础设施（被后端引用）
└── src/                  # 工具模块（被后端引用）
```

后端启动时，Python 需要能够找到这些目录，因此必须设置 PYTHONPATH。

---

## 八、完整启动流程

### 终端 1：启动后端

```bash
cd /Users/m99/Documents/SmartPaper/backend
./start_backend.sh
```

### 终端 2：启动前端

```bash
cd /Users/m99/Documents/SmartPaper/vue-frontend
npm run dev
```

### 访问应用

- 前端：http://localhost:5173
- 后端 API 文档：http://localhost:8000/api/docs

---

## 九、脚本说明

### start_backend.sh

后端启动脚本，自动完成以下操作：
1. 激活虚拟环境
2. 设置 PYTHONPATH
3. 启动后端服务

### install_deps.sh

依赖安装脚本，自动安装所有后端依赖：
1. FastAPI 基础依赖
2. 数据验证库
3. 异步支持
4. 数据库
5. 认证授权
6. 工具库
7. 速率限制
8. 邮箱验证

---

## 十、性能优化

### 生产环境启动

```bash
# 使用 gunicorn + uvicorn workers
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 数据库优化

```bash
# 生产环境建议使用 PostgreSQL 或 MySQL
# 修改 .env 文件：
DATABASE_URL=postgresql+asyncpg://user:password@localhost/smartpaper
```

---

祝使用愉快！🎉
