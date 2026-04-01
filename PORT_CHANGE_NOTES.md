# SmartPaper 端口修改说明

## 修改内容

本次修改将 SmartPaper 的前端和后端端口调整为：

- **前端**: `3000` → `3071`
- **后端**: `8000` → `8713`

## 修改的文件

### 1. 前端配置
- `vue-frontend/vite.config.ts`
  - `server.port`: `3000` → `3071`
  - `server.proxy['/api'].target`: `http://localhost:8000` → `http://localhost:8713`

### 2. 后端配置
- `backend/.env`
  - `PORT`: `8000` → `8713`
  - `ALLOWED_ORIGINS`: 添加 `http://localhost:3071`

- `backend/.env.example`
  - `PORT`: `8000` → `8713`
  - `ALLOWED_ORIGINS`: 更新为包含 `http://localhost:3071`

### 3. 启动脚本
- `backend/start_backend.sh`
  - uvicorn 端口: `8000` → `8713`

- `backend/start.sh`
  - uvicorn 端口: `8000` → `8713`

- `start_all.sh`
  - `BACKEND_PORT`: `8000` → `8713`
  - `FRONTEND_PORT`: `3000` → `3071`
  - uvicorn 端口: `8000` → `8713`
  - 启动信息提示更新

### 4. API 配置
- `vue-frontend/src/api/zotero.ts`
  - 默认 API 地址: `http://localhost:8000` → `http://localhost:8713`

### 5. 启动文档
- `QUICK_START.md`
  - 更新访问地址说明

## 访问地址

修改后，服务访问地址为：

- **前端界面**: http://localhost:3071
- **后端 API**: http://localhost:8713
- **API 文档**: http://localhost:8713/api/docs
- **ReDoc 文档**: http://localhost:8713/api/redoc
- **健康检查**: http://localhost:8713/health

## 启动方式

启动方式保持不变：

```bash
cd /Users/m99/Documents/SmartPaper
./start_all.sh
```

## 注意事项

1. 如果之前有使用旧端口的进程正在运行，`start_all.sh` 脚本会自动检测并停止它们
2. 浏览器缓存可能导致需要清除缓存后访问新端口
3. 如果手动启动，请确保使用新的端口配置
4. 防火墙或代理软件可能需要更新端口规则

## 修改日期

2026-03-31
