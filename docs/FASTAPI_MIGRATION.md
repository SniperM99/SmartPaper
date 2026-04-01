# SmartPaper 后端迁移到 FastAPI 文档

## 概述

SmartPaper 已完成从 Streamlit 单体架构到 FastAPI 后端 + Vue 前端的前后端分离架构迁移。

## 架构变更

### 之前的架构

```
Streamlit (streamlit.app.py)
├── 界面层
├── 业务逻辑层
└── 核心功能层
```

### 现在的架构

```
Frontend (Vue)      Backend (FastAPI)     Core
├── 页面组件         ├── API 路由          ├── Application Services
├── 状态管理         ├── 业务服务层        ├── Domain Models
└── 请求封装         └── 核心配置           └── Infrastructure
```

## 后端目录结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── api/                 # API 路由
│   │   ├── routers/
│   │   │   ├── paper_analysis.py       # 论文分析
│   │   │   ├── literature_ingestion.py # 文献导入
│   │   │   ├── research_map.py         # 研究地图
│   │   │   ├── zotero.py               # Zotero 集成
│   │   │   ├── file_ops.py             # 文件操作
│   │   │   └── profile.py              # 科研画像
│   ├── core/                # 核心配置
│   │   ├── config.py
│   │   └── logging.py
│   ├── models/              # 数据模型
│   │   ├── requests.py
│   │   └── responses.py
│   └── services/            # 业务服务
│       ├── analysis_service.py
│       ├── ingestion_service.py
│       ├── research_map_service.py
│       ├── zotero_service.py
│       ├── file_service.py
│       └── profile_service.py
├── requirements.txt
├── .env.example
├── start.sh
└── README.md
```

## API 端点总览

### 1. 论文分析 (`/api/analysis`)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/analysis/analyze-file` | 上传并分析论文文件（流式） |
| POST | `/api/analysis/analyze-url` | 从 URL 分析论文（流式） |
| POST | `/api/analysis/analyze-local` | 分析本地论文文件（流式） |
| POST | `/api/analysis/compare` | 多论文对比分析（流式） |
| GET | `/api/analysis/result/{paper_id}` | 获取分析结果 |

### 2. 文献导入 (`/api/ingestion`)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/ingestion/ingest-local` | 批量导入本地文献 |
| POST | `/api/ingestion/ingest-arxiv` | 从 arXiv 下载并导入 |
| GET | `/api/ingestion/papers` | 获取论文库列表 |
| GET | `/api/ingestion/papers/{paper_id}` | 获取论文详情 |
| DELETE | `/api/ingestion/papers/{paper_id}` | 删除论文 |

### 3. 研究地图 (`/api/research-map`)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/research-map/query` | 查询研究地图 |
| GET | `/api/research-map/data` | 获取研究地图数据 |
| POST | `/api/research-map/rebuild` | 重建研究地图 |

### 4. Zotero 集成 (`/api/zotero`)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/zotero/collections` | 获取收藏夹列表 |
| GET | `/api/zotero/items` | 获取文献条目 |
| POST | `/api/zotero/import` | 从 Zotero 导入文献 |
| GET | `/api/zotero/test-connection` | 测试连接 |

### 5. 文件操作 (`/api/files`)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/files/upload` | 上传文件 |
| GET | `/api/files/download/{file_path}` | 下载文件 |
| GET | `/api/files/stream/{file_path}` | 流式读取文件 |
| GET | `/api/files/info/{file_path}` | 获取文件信息 |
| DELETE | `/api/files/delete/{file_path}` | 删除文件 |

### 6. 科研画像 (`/api/profile`)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/profile/profile` | 获取科研画像 |
| PUT | `/api/profile/profile` | 更新科研画像 |
| GET | `/api/profile/options` | 获取分析选项 |

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置 API Key
```

### 3. 启动后端服务

```bash
./start.sh
# 或
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 5. 测试 API

```bash
python test_api.py
```

## 与核心层集成

FastAPI 后端通过以下方式复用现有的核心层代码：

1. **Application 层服务**: 直接使用 `application/` 下的服务类
   - `PaperAnalysisService` - 论文分析
   - `LiteratureIngestionService` - 文献导入
   - `MultiPaperService` - 多论文对比
   - `ResearchMapService` - 研究地图
   - `ZoteroIntegrationService` - Zotero 集成
   - `WorkbenchService` - 工作台管理

2. **Infrastructure 层**: 使用现有的基础设施
   - `LLMClient` - LLM 调用
   - `PDFConverter` - PDF 转换
   - 各种工具类

3. **核心工具**: 使用 `src/core/` 下的工具
   - `load_config()` - 配置加载
   - `get_prompt()` - 提示词管理
   - `get_available_options()` - 获取可用选项

## 流式响应

所有分析接口都支持 SSE (Server-Sent Events) 流式响应，前端可以实时接收分析结果。

### 响应格式

```typescript
// 数据块类型
type ChunkType = "chunk" | "final" | "error";

interface AnalysisChunk {
  type: ChunkType;
  content?: string;      // type="chunk" 时的内容
  success?: boolean;     // type="final" 时的成功标志
  file_path?: string;    // type="final" 时的输出文件路径
  paper_id?: string;     // 论文ID
  error?: string;        // type="error" 时的错误信息
}
```

### 前端使用示例

```typescript
const response = await fetch('/api/analysis/analyze-url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://arxiv.org/abs/2310.12345',
    role: 'phd_assistant',
    domain: 'general',
    task: 'phd_analysis',
    use_chain: false
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      // 处理数据块
      if (data.type === 'chunk') {
        // 更新UI显示分析内容
        appendContent(data.content);
      } else if (data.type === 'final') {
        // 分析完成
        showResult(data.file_path);
      }
    }
  }
}
```

## 错误处理

所有 API 返回统一的响应格式：

```json
{
  "success": true|false,
  "message": "操作结果说明",
  "data": {
    // 响应数据
  }
}
```

## CORS 配置

后端已配置 CORS，允许来自以下源的跨域请求：

- `http://localhost:5173` - Vue 前端开发服务器
- `http://localhost:8080`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:8080`

如需添加新的源，修改 `app/core/config.py` 中的 `ALLOWED_ORIGINS` 配置。

## 日志系统

日志使用 Loguru，配置如下：

- **控制台日志**: 所有 INFO 级别及以上
- **文件日志**: 所有 DEBUG 级别及以上，按天轮转，保留30天
- **错误日志**: 单独记录 ERROR 级别日志

日志文件位置：`logs/` 目录

## 文件存储

- **上传文件**: `temp/` 目录
- **分析结果**: `outputs/` 目录
- **日志文件**: `logs/` 目录

最大上传文件大小：100MB（可在 `app/core/config.py` 中修改）

## 部署

### 开发环境

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 生产环境

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker 部署（待实现）

```bash
# 构建镜像
docker build -t smartpaper-backend backend/

# 运行容器
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e ZOTERO_API_KEY=your_key \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/temp:/app/temp \
  smartpaper-backend
```

## 下一步工作

1. **完善论文库持久化**: 实现数据库存储（SQLite/PostgreSQL）
2. **添加认证授权**: 实现用户认证和权限管理
3. **优化性能**: 添加缓存、异步任务队列
4. **完善测试**: 编写单元测试和集成测试
5. **Docker 支持**: 添加 Dockerfile 和 docker-compose.yml
6. **监控告警**: 添加应用监控和日志告警

## 注意事项

1. 确保 `.env` 文件中的 API Key 已正确配置
2. 前端需要处理流式响应的特殊格式
3. 文件上传大小限制为 100MB
4. 所有路径参数需要正确编码
5. 建议在生产环境中使用 Nginx 反向代理

## 相关文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SSE (Server-Sent Events) 规范](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [Streamlit 到 FastAPI 迁移指南](./docs/STREAMLIT_TO_FASTAPI.md) (待补充)
