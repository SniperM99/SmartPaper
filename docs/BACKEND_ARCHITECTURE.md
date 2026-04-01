# SmartPaper 后端架构文档

## 架构概述

SmartPaper 后端采用分层架构，基于 FastAPI 框架实现 RESTful API 服务，并与现有的核心层深度集成。

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Vue)                            │
└────────────────────┬──────────────────────────────────────────┘
                     │ HTTP/HTTPS + SSE
┌────────────────────▼──────────────────────────────────────────┐
│                    API 路由层 (FastAPI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ /analysis│  │ /ingestion│  │ /research │  │  /zotero │     │
│  │  routers │  │  routers │  │   -map   │  │  routers │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└────────────────────┬──────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────────┐
│                    业务服务层 (Services)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Analysis  │  │Ingestion │  │ Research │  │  Zotero  │     │
│  │ Service  │  │ Service  │  │  Map     │  │ Service  │     │
│  │          │  │          │  │ Service  │  │          │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└────────────────────┬──────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────────┐
│                    应用层 (Application)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Paper    │  │Literature│  │ Multi    │  │ Workbench│     │
│  │Analysis  │  │Ingestion │  │Paper     │  │ Service  │     │
│  │Service   │  │Service   │  │Service   │  │          │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│  ┌──────────┐  ┌──────────┐                                  │
│  │ Research │  │ Zotero   │                                  │
│  │Map       │  │Integr.   │                                  │
│  │Service   │  │Service   │                                  │
│  └──────────┘  └──────────┘                                  │
└────────────────────┬──────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────────┐
│                  核心层 (Core + Domain)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│  │ Config   │  │ Prompt   │  │ History  │                     │
│  │ Loader   │  │ Manager  │  │ Manager  │                     │
│  └──────────┘  └──────────┘  └──────────┘                     │
└────────────────────┬──────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────────┐
│                基础设施层 (Infrastructure)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│  │ LLM      │  │ PDF      │  │ Storage  │                     │
│  │ Client   │  │ Converter│  │ Manager  │                     │
│  └──────────┘  └──────────┘  └──────────┘                     │
└───────────────────────────────────────────────────────────────┘
```

## 目录结构

```
backend/
├── app/
│   ├── main.py                    # FastAPI 应用入口
│   │
│   ├── api/                       # API 路由层
│   │   ├── __init__.py            # 路由聚合
│   │   └── routers/               # 各功能模块路由
│   │       ├── paper_analysis.py      # 论文分析 API
│   │       ├── literature_ingestion.py # 文献导入 API
│   │       ├── research_map.py         # 研究地图 API
│   │       ├── zotero.py               # Zotero 集成 API
│   │       ├── file_ops.py             # 文件操作 API
│   │       └── profile.py              # 科研画像 API
│   │
│   ├── core/                      # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py               # Pydantic 配置管理
│   │   └── logging.py              # Loguru 日志配置
│   │
│   ├── models/                    # 数据模型（Pydantic）
│   │   ├── __init__.py
│   │   ├── requests.py             # 请求模型定义
│   │   └── responses.py            # 响应模型定义
│   │
│   └── services/                  # 业务服务层
│       ├── __init__.py
│       ├── analysis_service.py     # 论文分析服务
│       ├── ingestion_service.py    # 文献导入服务
│       ├── research_map_service.py  # 研究地图服务
│       ├── zotero_service.py       # Zotero 集成服务
│       ├── file_service.py         # 文件服务
│       └── profile_service.py      # 科研画像服务
│
├── requirements.txt                # Python 依赖
├── .env.example                   # 环境变量示例
├── start.sh                       # 启动脚本
├── test_api.py                    # API 测试脚本
├── README.md                      # 项目文档
└── MIGRATION_SUMMARY.md           # 迁移完成报告
```

## 各层职责

### 1. API 路由层 (`app/api/`)

**职责**:
- 接收 HTTP 请求
- 参数验证（Pydantic 模型）
- 调用业务服务
- 返回标准化响应
- 处理流式响应（SSE）

**示例**:

```python
@router.post("/analyze-url")
async def analyze_url(request: UrlAnalysisRequest):
    return StreamingResponse(
        stream_generator(
            analysis_service.analyze_from_url(
                url=request.url,
                role=request.role,
                task=request.task,
                domain=request.domain,
            )
        ),
        media_type="text/event-stream",
    )
```

### 2. 业务服务层 (`app/services/`)

**职责**:
- 实现业务逻辑
- 调用应用层服务
- 处理数据转换
- 管理服务状态

**示例**:

```python
class AnalysisService:
    def __init__(self):
        self.config = load_config()
        self.paper_service = PaperAnalysisService(self.config)

    def analyze_from_url(self, url, role, task, domain):
        stream_gen = self.paper_service.analyze_url_stream(
            url, role=role, task=task, domain=domain
        )
        for chunk in stream_gen:
            yield chunk
```

### 3. 数据模型层 (`app/models/`)

**职责**:
- 定义请求参数模型
- 定义响应数据模型
- 自动数据验证
- 生成 API 文档

**示例**:

```python
class UrlAnalysisRequest(BaseModel):
    url: str = Field(..., description="论文URL")
    role: str = Field(..., description="分析角色")
    domain: str = Field(..., description="研究领域")
    task: str = Field(..., description="分析任务")
    use_chain: bool = Field(False, description="是否开启多轮分析链")
```

### 4. 核心配置层 (`app/core/`)

**职责**:
- 环境变量管理
- 应用配置加载
- 日志系统配置

**示例**:

```python
class Settings(BaseSettings):
    APP_NAME: str = "SmartPaper API"
    OPENAI_API_KEY: Optional[str] = None
    PORT: int = 8000

settings = Settings()
```

### 5. 应用层 (`application/`)

**职责**:
- 核心业务逻辑
- 论文分析流程编排
- 跨服务协调

**服务类**:
- `PaperAnalysisService` - 论文分析
- `LiteratureIngestionService` - 文献导入
- `MultiPaperService` - 多论文对比
- `ResearchMapService` - 研究地图
- `ZoteroIntegrationService` - Zotero 集成
- `WorkbenchService` - 工作台管理

### 6. 核心层 (`src/core/`)

**职责**:
- 配置加载
- 提示词管理
- 历史记录管理
- 任务管理

### 7. 基础设施层 (`infrastructure/`)

**职责**:
- LLM 客户端封装
- PDF 转换器
- 存储管理
- 外部服务集成

## 数据流

### 论文分析流程

```
用户请求
  │
  ▼
API 路由层 (paper_analysis.py)
  │ 接收请求参数
  ▼
业务服务层 (analysis_service.py)
  │ 调用应用层服务
  ▼
应用层 (PaperAnalysisService)
  │ 流程编排
  ├─► PDF 转换 (PDFConverter)
  ├─► LLM 调用 (LLMClient)
  └─► 结构化提取
  │
  ▼
返回结果（流式/标准）
  │
  ▼
用户界面
```

### 文献导入流程

```
用户上传/URL/本地路径
  │
  ▼
API 路由层 (literature_ingestion.py)
  │
  ▼
业务服务层 (ingestion_service.py)
  │
  ▼
应用层 (LiteratureIngestionService)
  ├─► 下载/读取文件
  ├─► 解析元数据
  ├─► 保存到论文库
  └─► 触发分析（可选）
  │
  ▼
返回导入结果
```

### 研究地图查询流程

```
用户查询
  │
  ▼
API 路由层 (research_map.py)
  │
  ▼
业务服务层 (research_map_service.py)
  │
  ▼
应用层 (ResearchMapService)
  ├─► 向量检索
  ├─► LLM 生成回答
  └─► 返回来源和推理
  │
  ▼
返回查询结果
```

## 关键设计决策

### 1. 为什么选择 FastAPI？

- **类型安全**: 基于 Pydantic 的自动数据验证
- **异步支持**: 原生支持 asyncio，提高并发性能
- **自动文档**: 自动生成 OpenAPI/Swagger 文档
- **性能优秀**: 基于 Starlette，性能接近 Go/Rust
- **生态完善**: 与现有 Python 生态系统兼容性好

### 2. 为什么分层架构？

- **关注点分离**: 每层职责明确，易于维护
- **可测试性**: 各层可独立测试
- **可扩展性**: 新增功能只需扩展对应层
- **复用性**: 业务服务可被多个 API 复用

### 3. 为什么使用 SSE 流式响应？

- **实时反馈**: 用户可以实时看到分析进度
- **用户体验**: 不需要等待全部完成
- **内存效率**: 边生成边传输，减少内存占用

### 4. 如何与现有代码集成？

- **复用应用层**: 直接使用 `application/` 下的服务类
- **适配接口**: 通过 Service 层封装现有接口
- **渐进迁移**: 不需要重写核心逻辑

## 性能优化建议

### 1. 异步处理

```python
# 使用异步文件操作
async def save_file(content: bytes, path: str):
    async with aiofiles.open(path, 'wb') as f:
        await f.write(content)
```

### 2. 连接池

```python
# HTTP 客户端连接池
http_client = httpx.AsyncClient(limits=httpx.Limits(max_connections=100))
```

### 3. 缓存机制

```python
# 使用 Redis 缓存
from fastapi_cache import FastAPICache, Coder
from fastapi_cache.backends.redis import RedisBackend

@cache(expire=3600)
async def get_analysis_options():
    return profile_service.get_analysis_options()
```

### 4. 任务队列

```python
# 使用 Celery 处理长时间任务
from celery import Celery

celery = Celery('smartpaper', broker='redis://localhost:6379')

@celery.task
async def analyze_paper_async(paper_id: str):
    # 异步分析逻辑
    pass
```

## 安全性建议

### 1. 认证授权

```python
# JWT 认证
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # 验证 token
    return user
```

### 2. 请求限流

```python
# 使用 slowapi 限流
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze_paper(request: Request):
    # ...
```

### 3. 输入验证

```python
# Pydantic 自动验证
class PaperAnalysisRequest(BaseModel):
    url: HttpUrl  # 自动验证 URL 格式
    role: str = Field(..., min_length=1, max_length=50)
```

### 4. CORS 配置

```python
# 限制允许的源
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # 配置文件中定义
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 监控和日志

### 1. 日志配置

```python
# 使用 loguru
logger.add(
    "logs/smartpaper_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    level="INFO"
)
```

### 2. 健康检查

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": check_db_connection(),
            "llm": check_llm_connection(),
        }
    }
```

### 3. 性能监控

```python
# 使用 prometheus
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## 部署建议

### 1. Docker 部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./outputs:/app/outputs
      - ./temp:/app/temp
      - ./logs:/app/logs
```

### 3. Nginx 反向代理

```nginx
location /api/ {
    proxy_pass http://localhost:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_buffering off;  # 禁用缓冲支持 SSE
}
```

## 总结

SmartPaper 后端采用清晰的分层架构，各层职责明确，易于维护和扩展。通过复用现有的应用层代码，实现了从 Streamlit 到 FastAPI 的平滑迁移。未来可以在服务层、缓存、认证等方面进一步优化，提升性能和安全性。
