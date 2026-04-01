# SmartPaper FastAPI 后端启动指南

## 重要说明

FastAPI 后端需要与 SmartPaper 核心代码库集成，因此需要从项目根目录启动，不能独立运行。

## 启动步骤

### 1. 安装依赖

**从项目根目录安装依赖**：

```bash
cd /Users/m99/Documents/SmartPaper
pip install -r backend/requirements.txt
```

### 2. 配置环境变量

```bash
cd /Users/m99/Documents/SmartPaper/backend
cp .env.example .env
# 编辑 .env 文件，配置 API Key
```

### 3. 启动服务

**方式 1: 从项目根目录启动（推荐）**

```bash
cd /Users/m99/Documents/SmartPaper
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

**方式 2: 修改 Python 路径后从 backend 目录启动**

```bash
cd /Users/m99/Documents/SmartPaper/backend
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**方式 3: 使用启动脚本**

```bash
cd /Users/m99/Documents/SmartPaper
bash backend/start.sh
```

## 验证服务

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

预期输出：
```json
{
  "success": true,
  "service": "SmartPaper API",
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. 访问 API 文档

打开浏览器访问：
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 3. 运行测试脚本

```bash
cd /Users/m99/Documents/SmartPaper
python backend/test_api.py
```

## 常见问题

### Q1: 为什么不能独立在 backend 目录运行？

**A**: FastAPI 后端需要引用 SmartPaper 核心代码库（`application/`, `src/core/` 等模块），这些模块位于项目根目录。需要将项目根目录添加到 Python 路径中。

### Q2: 提示 "No module named 'application'"？

**A**: 这表示 Python 找不到应用层模块。解决方法：
- 从项目根目录启动（推荐）
- 或设置 `PYTHONPATH` 环境变量

### Q3: 如何配置 API Key？

**A**: 编辑 `backend/.env` 文件：

```env
OPENAI_API_KEY=your_openai_api_key
ZHIPUAI_API_KEY=your_zhipuai_api_key
ZOTERO_API_KEY=your_zotero_api_key
ZOTERO_USER_ID=your_zotero_user_id
```

### Q4: 开发模式下如何热重载？

**A**: 启动时添加 `--reload` 参数：

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Q5: 如何查看日志？

**A**: 日志文件位于 `backend/logs/` 目录：
- `smartpaper_YYYY-MM-DD.log` - 所有日志
- `error_YYYY-MM-DD.log` - 错误日志

## 生产环境部署

### 1. 使用多个 Worker

```bash
cd /Users/m99/Documents/SmartPaper
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. 使用 Gunicorn + Uvicorn Workers

```bash
cd /Users/m99/Documents/SmartPaper
gunicorn backend.app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 3. 使用 Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 复制整个项目
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# 设置工作目录
WORKDIR /app/backend

# 复制环境配置
COPY backend/.env .

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
cd /Users/m99/Documents/SmartPaper
docker build -t smartpaper-backend .
docker run -p 8000:8000 smartpaper-backend
```

### 4. 使用 Nginx 反向代理

```nginx
upstream smartpaper_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.smartpaper.com;

    location /api/ {
        proxy_pass http://smartpaper_backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_buffering off;  # 支持 SSE
    }

    location /health {
        proxy_pass http://smartpaper_backend/health;
    }
}
```

## 性能优化建议

### 1. 启用 Gzip 压缩

```python
# 在 app/main.py 中
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 2. 配置 CORS

```python
# 在 app/core/config.py 中
ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]
```

### 3. 使用 Redis 缓存

```python
# 安装依赖
pip install redis fastapi-cache2

# 配置缓存
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="smartpaper")
```

### 4. 异步数据库连接

```python
# 使用 asyncpg
import asyncpg

async def get_db_connection():
    return await asyncpg.connect("postgresql://user:pass@localhost/db")
```

## 监控和日志

### 1. 集成 Prometheus 监控

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

访问 http://localhost:8000/metrics 查看监控指标。

### 2. 集成 Sentry 错误追踪

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
)
```

### 3. 配置日志级别

```bash
# 开发环境
export LOG_LEVEL=DEBUG

# 生产环境
export LOG_LEVEL=INFO
```

## 相关文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [项目架构文档](../docs/BACKEND_ARCHITECTURE.md)
- [API 使用文档](../docs/FASTAPI_MIGRATION.md)
- [快速开始](../docs/API_QUICKSTART.md)
