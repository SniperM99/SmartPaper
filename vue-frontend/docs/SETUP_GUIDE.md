# Vue 研究地图组件安装指南

## 快速开始

### 前置要求

- Node.js 18+ 和 npm/yarn
- Python 3.10+（用于后端 API）
- Streamlit

### 1. 安装 Python 依赖

SmartPaper 项目已经包含必要的 Python 依赖，无需额外安装。

如果需要单独安装 FastAPI 和相关依赖：

```bash
pip install fastapi uvicorn
```

### 2. 安装 Vue 前端依赖

进入 vue-frontend 目录并安装依赖：

```bash
cd vue-frontend
npm install
```

### 3. 启动开发服务器

#### 启动 Vue 开发服务器

在 `vue-frontend` 目录下运行：

```bash
npm run dev
```

服务器将运行在 `http://localhost:5173`

#### 启动 Streamlit 应用

在项目根目录下运行：

```bash
streamlit run streamlit.app.py
```

Streamlit 将运行在 `http://localhost:8501`

### 4. 访问研究地图

1. 在浏览器中打开 `http://localhost:8501`
2. 在侧边栏选择「🧠 分析工作流」
3. 选择「研究映射」标签
4. 选择「Vue 交互式图谱」视图模式

## 开发工作流

### 开发 Vue 组件

```bash
cd vue-frontend
npm run dev  # 启动开发服务器
```

开发服务器支持热重载，修改代码后会自动刷新页面。

### 修改类型定义

类型定义位于 `src/types/research-map.ts`，修改后无需重新启动，Vite 会自动检测变化。

### 添加新组件

1. 在 `src/components/` 下创建新组件
2. 在需要的地方导入并使用
3. 确保组件遵循 Vue 3 Composition API 规范

### 修改 API

API 端点位于 `infrastructure/research_map_api.py`：

1. 修改 Python API 代码
2. 重启 Streamlit 应用（API 服务器会在后台自动重启）

## 生产部署

### 构建 Vue 应用

```bash
cd vue-frontend
npm run build
```

构建产物将输出到 `vue-frontend/dist/` 目录。

### 部署选项

#### 选项 1：独立部署

将 Vue 应用部署到静态文件服务器（如 Nginx、Vercel），通过 API 与 Streamlit 后端通信。

#### 选项 2：嵌入式部署

将构建后的静态文件嵌入到 Streamlit 应用中，使用 iframe 方式加载。

#### 选项 3：Streamlit Cloud 部署

在 Streamlit Cloud 上部署时，需要：

1. 确保前端文件已构建
2. 使用相对路径引用静态资源
3. 配置 CORS 允许跨域请求

## 故障排查

### Vue 开发服务器无法启动

检查 Node.js 版本是否满足要求：

```bash
node --version  # 应该是 18.0 或更高
```

### API 请求失败

1. 确认 API 服务器已启动（检查 Streamlit 日志）
2. 检查端口 8001 是否被占用
3. 确认 CORS 配置正确

### 图谱不显示

1. 检查浏览器控制台是否有错误
2. 确认后端返回了正确的数据格式
3. 查看网络请求是否成功

### 样式问题

清除浏览器缓存并刷新页面：

```bash
# 开发模式中，Vite 会自动处理缓存
# 生产模式中，清除缓存后刷新
```

## 性能优化

### 大型图谱优化

如果图谱节点数超过 1000，考虑：

1. 启用虚拟滚动
2. 使用 Web Worker 处理布局计算
3. 分批加载数据

### 构建优化

在 `vite.config.ts` 中配置：

```typescript
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'vendor': ['vue', 'pinia', 'vue-router'],
        'd3': ['d3', 'd3-force', 'd3-zoom', 'd3-selection']
      }
    }
  }
}
```

## 相关文档

- [集成指南](./INTEGRATION_GUIDE.md) - 如何将 Vue 组件集成到 Streamlit
- [API 文档](../README.md) - API 端点详细说明
- [组件文档](./COMPONENTS.md) - 各个组件的详细说明

## 获取帮助

如有问题，请：

1. 查看项目文档
2. 检查 GitHub Issues
3. 联系团队成员
