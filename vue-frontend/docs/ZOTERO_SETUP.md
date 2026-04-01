# Zotero 集成组件 - 快速开始

## 安装

```bash
cd vue-frontend
npm install
```

## 开发模式

```bash
# 启动开发服务器
npm run dev

# 访问地址
http://localhost:5173/zotero
```

## 生产构建

```bash
# 构建
npm run build

# 预览构建结果
npm run preview
```

## 环境配置

创建 `.env.development` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 后端 API 要求

后端需要提供以下接口：

- `POST /api/zotero/test-connection` - 测试连接
- `GET /api/zotero/items` - 获取文献列表
- `GET /api/zotero/collections` - 获取集合列表
- `POST /api/zotero/sync` - 同步数据
- `POST /api/zotero/import` - 上传导入文件
- `POST /api/zotero/import-to-library` - 导入到论文库
- `GET /api/zotero/search` - 搜索文献
- `POST /api/zotero/writeback-analysis` - 回写分析结果

详细 API 文档请参考 [ZOTERO_INTEGRATION.md](./ZOTERO_INTEGRATION.md)。

## 主要功能

### 1. 连接配置
- 配置 Zotero API Key 和 Library ID
- 测试连接是否正常
- 自动保存配置到本地

### 2. 文献库
- 浏览所有 Zotero 文献
- 搜索和筛选文献
- 批量选择文献
- 导入到 SmartPaper 论文库

### 3. 导入管理
- 上传 Zotero 导出文件
- 跟踪导入进度
- 查看导入历史

## 文件说明

- `src/types/zotero.ts` - TypeScript 类型定义
- `src/stores/zotero.ts` - Pinia 状态管理
- `src/api/zotero.ts` - API 服务层
- `src/components/workspace/` - Zotero 相关组件
- `src/views/ZoteroWorkspace.vue` - Zotero 工作区视图
- `src/router/index.ts` - 路由配置

## 样式

组件使用项目统一的 CSS 变量系统（`src/assets/styles/variables.css`）。
