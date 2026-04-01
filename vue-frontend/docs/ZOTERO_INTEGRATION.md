# Zotero 集成 - Vue 组件文档

## 概述

SmartPaper Zotero 集成是一个完整的 Vue.js 前端解决方案，用于连接 Zotero 文献管理工具并导入文献数据。

## 功能特性

### 1. 连接配置
- ✅ Zotero API Key 管理
- ✅ Library ID 配置（支持个人库和群组库）
- ✅ 连接测试与验证
- ✅ 同步状态实时显示
- ✅ 配置信息本地持久化（关联用户）

### 2. 文献库管理
- ✅ 文献列表展示（列表视图 / 卡片视图）
- ✅ 搜索功能（标题、作者、摘要）
- ✅ 多维度筛选（类型、标签、集合）
- ✅ 排序功能（日期、标题、添加时间）
- ✅ 批量选择和操作
- ✅ 文献详情预览

### 3. 导入管理
- ✅ 文件拖放上传
- ✅ 支持多种格式（JSON、BibTeX、RDF）
- ✅ 导入配置选项（附件、笔记、标签、集合）
- ✅ 导入批次记录
- ✅ 导入进度跟踪
- ✅ 错误处理与重试

### 4. 交互优化
- ✅ 加载状态提示
- ✅ 错误消息显示
- ✅ 成功操作反馈
- ✅ 响应式设计（支持桌面和移动端）
- ✅ 流畅的过渡动画
- ✅ 专业 SVG 图标

### 5. 认证集成
- ✅ 用户身份验证
- ✅ Token 管理
- ✅ 配置按用户隔离
- ✅ 自动加载用户配置

## 项目结构

```
vue-frontend/
├── src/
│   ├── api/
│   │   └── zotero.ts              # Zotero API 服务层
│   ├── assets/
│   │   └── styles/
│   │       └── variables.css      # 全局 CSS 变量
│   ├── components/
│   │   ├── common/
│   │   │   └── Icon.vue           # 通用图标组件
│   │   ├── icons/
│   │   │   ├── IconDatabase.vue   # 数据库图标
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── Sidebar.vue        # 侧边栏（已更新）
│   │   │   └── Header.vue
│   │   └── workspace/
│   │       ├── ZoteroConfigPanel.vue      # 连接配置面板
│   │       ├── ZoteroLibraryPanel.vue     # 文献库面板
│   │       ├── ZoteroImportPanel.vue      # 导入管理面板
│   │       └── ZoteroWorkspaceIndex.vue   # 工作区主容器
│   ├── router/
│   │   └── index.ts              # 路由配置
│   ├── stores/
│   │   ├── auth.ts               # 认证状态管理
│   │   ├── app.ts                 # 应用全局状态
│   │   └── zotero.ts             # Zotero 状态管理
│   ├── types/
│   │   └── zotero.ts             # TypeScript 类型定义
│   ├── views/
│   │   └── ZoteroWorkspace.vue   # Zotero 工作区视图
│   ├── App.vue                   # 根组件
│   └── main.ts                   # 应用入口
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 快速开始

### 1. 安装依赖

```bash
cd vue-frontend
npm install
```

### 2. 配置环境变量

创建 `.env.development` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 `http://localhost:5173/zotero` 查看 Zotero 集成页面。

### 4. 构建生产版本

```bash
npm run build
```

## 技术栈

- **框架**: Vue 3 (Composition API + `<script setup>`)
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **构建工具**: Vite
- **语言**: TypeScript
- **样式**: CSS Variables + Scoped CSS

## 状态管理

### Auth Store (认证状态)

```typescript
{
  user: User | null
  token: string | null
  isAuthenticated: boolean
}
```

**主要方法**:
- `login(email, password)` - 登录
- `logout()` - 登出
- `validateToken()` - 验证 token

### App Store (应用状态)

```typescript
{
  sidebarCollapsed: boolean
  sidebarMobileOpen: boolean
  theme: 'light' | 'dark'
  globalLoading: boolean
  notifications: Notification[]
}
```

**主要方法**:
- `toggleSidebar()` - 切换侧边栏
- `addNotification()` - 添加通知
- `toggleTheme()` - 切换主题

### Zotero Store (Zotero 状态)

```typescript
{
  config: ZoteroConfig
  connection: ZoteroConnection
  items: ZoteroItem[]
  collections: ZoteroCollection[]
  batches: ZoteroImportBatch[]
  isLoading: boolean
  selectedItems: Set<string>
  searchParams: ZoteroSearchParams
}
```

**主要方法**:
- `setConfig()` - 设置配置
- `testConnection()` - 测试连接
- `syncAll()` - 同步全部
- `fetchItems()` - 获取文献
- `importSelectedToLibrary()` - 导入选中文献

## 图标系统

所有图标使用 SVG 格式，通过 `Icon` 组件统一管理：

```vue
<Icon name="database" :size="20" color="var(--color-primary)" />
```

**可用图标**:
- `menu` - 菜单
- `database` - 数据库（Zotero）
- `sync` - 同步
- `link` - 连接
- `book` - 书籍/文献
- `file-text` - 文件
- `upload` - 上传
- `download` - 下载
- `search` - 搜索
- `filter` - 筛选
- `check` - 勾选
- `close` - 关闭
- `alert-circle` - 警告
- `check-circle` - 成功
- `info` - 信息
- `loading` - 加载中
- `settings` - 设置
- `help` - 帮助
- `list` - 列表
- `grid` - 网格
- `menu-dots` - 更多选项

## 样式系统

使用 CSS 变量定义设计 tokens：

### 主色调
- `--color-primary`: #1e40af (学术蓝)
- `--color-primary-hover`: #1e3a8a
- `--color-primary-light`: #dbeafe

### 语义色
- `--color-success`: #059669
- `--color-warning`: #d97706
- `--color-error`: #dc2626
- `--color-info`: #0891b2

### 中性色
- `--color-bg-primary`: #ffffff
- `--color-bg-secondary`: #f8fafc
- `--color-bg-tertiary`: #f1f5f9
- `--color-text-primary`: #1e293b
- `--color-text-secondary`: #475569
- `--color-text-tertiary`: #64748b

## 响应式设计

### 断点
- `xs`: 640px
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

### 适配策略
- **桌面端** (≥1024px): 完整功能，侧边栏展开
- **平板端** (768px-1023px): 响应式布局
- **移动端** (<768px): 侧边栏收起，触控优化

## API 接口

### 测试连接
```typescript
POST /api/zotero/test-connection
Body: { apiKey, libraryId, libraryType }
Response: { success, message }
```

### 获取文献列表
```typescript
GET /api/zotero/items?collection=&since=&limit=
Response: ZoteroItem[]
```

### 获取集合列表
```typescript
GET /api/zotero/collections
Response: ZoteroCollection[]
```

### 同步数据
```typescript
POST /api/zotero/sync
Body: { mode: 'full' | 'incremental' }
Response: ZoteroSyncResult
```

### 上传导入文件
```typescript
POST /api/zotero/import
Body: FormData { libraryName, importType, files[] }
Response: ZoteroImportBatch
```

### 导入到论文库
```typescript
POST /api/zotero/import-to-library
Body: { itemKeys[], includeAttachments?, includeNotes?, includeTags? }
Response: ZoteroImportResult
```

### 搜索文献
```typescript
GET /api/zotero/search?q=&itemType=&tags=&collection=
Response: ZoteroItem[]
```

### 回写分析结果
```typescript
POST /api/zotero/writeback-analysis
Body: { itemKey, analysisSummary, tags[] }
Response: { success, message }
```

## 开发指南

### 添加新功能

1. 在 `types/zotero.ts` 中定义类型
2. 在 `api/zotero.ts` 中添加 API 方法
3. 在 `stores/zotero.ts` 中添加状态和操作
4. 创建 Vue 组件（使用 `<script setup>`）
5. 在 `router/index.ts` 中添加路由（如需要）

### 代码规范

- 使用 TypeScript 编写所有代码
- 遵循 Vue 3 Composition API 最佳实践
- 使用 `<script setup>` 语法糖
- 组件样式使用 scoped CSS
- 优先使用 CSS 变量而非硬编码颜色
- 使用 `Icon` 组件而非 emoji

### 组件示例

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import Icon from '../common/Icon.vue'

const items = ref([])
const isLoading = ref(false)

const handleAction = async () => {
  isLoading.value = true
  try {
    // 执行操作
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="component">
    <Icon name="database" :size="20" />
    <p>{{ isLoading ? '加载中...' : '完成' }}</p>
  </div>
</template>

<style scoped>
.component {
  /* 组件样式 */
}
</style>
```

## 常见问题

### Q: 如何获取 Zotero API Key？
A: 登录 Zotero 官网，前往 Account Settings → Feeds/API，创建新的 Private Key。

### Q: Library ID 是什么？
A:
- 个人库：用户 ID（在个人资料页面查看）
- 群组库：群组 ID（在群组设置页面查看）

### Q: 支持哪些导入格式？
A: 支持 Zotero JSON 导出、BibTeX (.bib)、RDF 格式。

### Q: 如何实现离线导入？
A: 在"导入管理"页面上传 Zotero 导出的 JSON 文件，无需在线连接。

### Q: 配置如何保存？
A: 配置保存在 localStorage 中，按用户 ID 隔离存储。

### Q: 如何添加新图标？
A: 在 `src/components/icons/` 创建图标组件，在 `Icon.vue` 的 `icons` 对象中注册。

## 后续计划

- [ ] 实现实时 WebSocket 同步
- [ ] 添加文献笔记编辑功能
- [ ] 支持文献分组和分类
- [ ] 集成 PDF 在线预览
- [ ] 支持跨设备数据同步
- [ ] 添加使用统计和分析
- [ ] 暗色模式完整适配
- [ ] 国际化支持

## 许可证

MIT License
