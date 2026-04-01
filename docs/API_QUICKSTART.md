# SmartPaper API 快速开始

本文档帮助你快速上手 SmartPaper FastAPI 后端 API。

## 启动后端服务

```bash
cd backend
./start.sh
```

服务将在 http://localhost:8000 启动。

## 访问 API 文档

打开浏览器访问：

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 常用 API 示例

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

### 2. 分析 arXiv 论文

```bash
curl -X POST http://localhost:8000/api/analysis/analyze-url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://arxiv.org/abs/2310.12345",
    "role": "phd_assistant",
    "domain": "general",
    "task": "phd_analysis",
    "use_chain": false
  }'
```

### 3. 获取论文列表

```bash
curl http://localhost:8000/api/ingestion/papers
```

### 4. 查询研究地图

```bash
curl -X POST http://localhost:8000/api/research-map/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "transformer 架构",
    "scope": "all",
    "max_results": 5
  }'
```

### 5. 获取分析选项

```bash
curl http://localhost:8000/api/profile/options
```

### 6. 测试 Zotero 连接

```bash
curl http://localhost:8000/api/zotero/test-connection
```

## 流式响应处理

所有分析接口都支持 SSE (Server-Sent Events) 流式响应。

### JavaScript/TypeScript 示例

```javascript
const response = await fetch('http://localhost:8000/api/analysis/analyze-url', {
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

      if (data.type === 'chunk') {
        // 显示分析内容
        console.log(data.content);
      } else if (data.type === 'final') {
        // 分析完成
        console.log('分析完成:', data.file_path);
      } else if (data.type === 'error') {
        // 错误处理
        console.error('错误:', data.error);
      }
    }
  }
}
```

## 响应格式

所有 API 返回统一的响应格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 响应数据
  }
}
```

## 错误处理

```json
{
  "success": false,
  "message": "错误信息",
  "data": null
}
```

## 环境配置

复制 `.env.example` 为 `.env` 并配置：

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件
```

主要配置项：

```env
OPENAI_API_KEY=your_key_here
ZHIPUAI_API_KEY=your_key_here
ZOTERO_API_KEY=your_key_here
ZOTERO_USER_ID=your_user_id_here
```

## 测试脚本

运行测试脚本验证 API：

```bash
python backend/test_api.py
```

## 更多文档

- [完整 API 文档](FASTAPI_MIGRATION.md)
- [项目 README](../README.md)
- [Backend README](../backend/README.md)
