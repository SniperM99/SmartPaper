# SmartPaper FastAPI Backend

SmartPaper 智能论文分析平台后端服务，提供 RESTful API 接口。

## 项目结构

```
backend/
├── app/
│   ├── __init__.py          # 应用初始化
│   ├── main.py              # FastAPI 主应用
│   ├── api/                 # API 路由层
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── paper_analysis.py        # 论文分析 API
│   │       ├── literature_ingestion.py  # 文献导入 API
│   │       ├── research_map.py          # 研究地图 API
│   │       ├── zotero.py                # Zotero 集成 API
│   │       ├── file_ops.py              # 文件操作 API
│   │       └── profile.py               # 科研画像 API
│   ├── core/                # 核心配置
│   │   ├── config.py        # 配置管理
│   │   └── logging.py       # 日志配置
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── requests.py      # 请求模型
│   │   └── responses.py     # 响应模型
│   └── services/            # 业务服务层
│       ├── __init__.py
│       ├── analysis_service.py      # 论文分析服务
│       ├── ingestion_service.py     # 文献导入服务
│       ├── research_map_service.py  # 研究地图服务
│       ├── zotero_service.py        # Zotero 集成服务
│       ├── file_service.py          # 文件服务
│       └── profile_service.py       # 科研画像服务
├── requirements.txt         # Python 依赖
├── .env.example            # 环境配置示例
├── start.sh                # 启动脚本
└── README.md               # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置 API Key
```

### 3. 启动服务

```bash
# 方式1: 使用启动脚本
./start.sh

# 方式2: 直接使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API 端点

### 论文分析 (`/api/analysis`)

- `POST /api/analysis/analyze-file` - 上传并分析论文文件（流式）
- `POST /api/analysis/analyze-url` - 从 URL 分析论文（流式）
- `POST /api/analysis/analyze-local` - 分析本地论文文件（流式）
- `POST /api/analysis/compare` - 多论文对比分析（流式）
- `GET /api/analysis/result/{paper_id}` - 获取分析结果

### 文献导入 (`/api/ingestion`)

- `POST /api/ingestion/ingest-local` - 批量导入本地文献
- `POST /api/ingestion/ingest-arxiv` - 从 arXiv 下载并导入
- `GET /api/ingestion/papers` - 获取论文库列表
- `GET /api/ingestion/papers/{paper_id}` - 获取论文详情
- `DELETE /api/ingestion/papers/{paper_id}` - 删除论文

### 研究地图 (`/api/research-map`)

- `POST /api/research-map/query` - 查询研究地图
- `GET /api/research-map/data` - 获取研究地图数据
- `POST /api/research-map/rebuild` - 重建研究地图

### Zotero 集成 (`/api/zotero`)

- `GET /api/zotero/collections` - 获取收藏夹列表
- `GET /api/zotero/items` - 获取文献条目
- `POST /api/zotero/import` - 从 Zotero 导入文献
- `GET /api/zotero/test-connection` - 测试连接

### 文件操作 (`/api/files`)

- `POST /api/files/upload` - 上传文件
- `GET /api/files/download/{file_path}` - 下载文件
- `GET /api/files/stream/{file_path}` - 流式读取文件
- `GET /api/files/info/{file_path}` - 获取文件信息
- `DELETE /api/files/delete/{file_path}` - 删除文件

### 科研画像 (`/api/profile`)

- `GET /api/profile/profile` - 获取科研画像
- `PUT /api/profile/profile` - 更新科研画像
- `GET /api/profile/options` - 获取分析选项

## 技术栈

- **Web 框架**: FastAPI
- **ASGI 服务器**: Uvicorn
- **数据验证**: Pydantic
- **日志**: Loguru
- **异步支持**: asyncio, aiofiles

## 与核心层集成

FastAPI 后端通过以下方式与 SmartPaper 核心层集成：

1. **Application 层服务**: 复用 `application/` 下的服务类
2. **Infrastructure 层**: 使用现有的 LLM 客户端、PDF 转换器等
3. **核心工具**: 使用 `src/core/` 下的配置加载、提示词管理等

## 开发指南

### 添加新的 API 端点

1. 在 `app/api/routers/` 创建或编辑路由文件
2. 在 `app/api/__init__.py` 注册路由
3. 在 `app/services/` 实现业务逻辑
4. 在 `app/models/` 定义请求/响应模型

### 流式响应

所有分析接口都支持 SSE (Server-Sent Events) 流式响应：

```python
return StreamingResponse(
    stream_generator(generator),
    media_type="text/event-stream",
)
```

### 错误处理

全局异常处理在 `app/main.py` 中配置：

```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"全局异常捕获: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "服务器内部错误"},
    )
```

## 部署

### 生产环境

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (待实现)

```bash
# 构建镜像
docker build -t smartpaper-backend .

# 运行容器
docker run -p 8000:8000 smartpaper-backend
```

## 注意事项

1. 确保 `.env` 文件中的 API Key 已正确配置
2. 上传文件大小限制为 100MB（可在 `app/core/config.py` 中修改）
3. 日志文件保存在 `logs/` 目录
4. 临时文件保存在 `temp/` 目录
5. 分析结果保存在 `outputs/` 目录

## License

与 SmartPaper 主项目保持一致
