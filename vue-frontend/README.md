# SmartPaper 研究地图 Vue 组件

交互式知识图谱可视化组件，用于展示论文、主题、方法等研究实体及其关系。

## 功能特性

### 🎨 可视化
- 7 种实体类型（论文、主题、问题、方法、数据集、指标、空白）
- 8 种关系类型（研究主题、解决问题、使用方法等）
- 论文节点矩形展示，其他节点圆形展示
- 提及数徽章显示

### 🖱️ 交互功能
- 节点拖拽
- 缩放和平移
- 节点/边点击查看详情
- 悬停高亮相关元素
- 多种布局算法（力导向、圆形、层级）

### 🔍 筛选与搜索
- 按实体类型筛选
- 按最小提及数筛选
- 节点搜索功能

### 📊 辅助视图
- 研究时间线
- 研究空白列表
- 聚类视图

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **D3.js** - 数据可视化
- **Pinia** - 状态管理
- **Vue Router** - 路由管理

## 安装

```bash
# 安装依赖
npm install
```

## 开发

```bash
# 启动开发服务器
npm run dev
```

访问 http://localhost:5173

## 构建

```bash
# 构建生产版本
npm run build
```

构建产物将输出到 `dist/` 目录。

## 使用示例

### 基础使用

```vue
<template>
  <ResearchGraph
    :data="researchMapData"
    :loading="isLoading"
    @node-click="handleNodeClick"
    @edge-click="handleEdgeClick"
  />
</template>

<script setup>
import ResearchGraph from '@/components/ResearchGraph.vue'
import { ref, onMounted } from 'vue'

const researchMapData = ref(null)
const isLoading = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    const response = await fetch('/api/research-map')
    researchMapData.value = await response.json()
  } finally {
    isLoading.value = false
  }
})

const handleNodeClick = (node) => {
  console.log('节点点击:', node)
}

const handleEdgeClick = (edge) => {
  console.log('边点击:', edge)
}
</script>
```

### 完整视图

```vue
<template>
  <ResearchMapView />
</template>

<script setup>
import ResearchMapView from '@/views/ResearchMapView.vue'
</script>
```

## 组件文档

详见 [集成指南](./docs/INTEGRATION_GUIDE.md)

## API 数据格式

```typescript
interface ResearchMapData {
  overview: Record<string, any>
  entities: ResearchEntity[]
  relations: ResearchRelation[]
  timeline: TimelineEvent[]
  clusters: ResearchCluster[]
  gaps: ResearchGap[]
}
```

完整类型定义见 `src/types/research-map.ts`

## 与 Streamlit 集成

支持多种集成方式：

1. **独立页面**：Vue 前端独立部署，通过 HTTP API 通信
2. **组件嵌入**：将构建后的静态文件嵌入 Streamlit
3. **自定义组件**：创建 Streamlit 自定义组件

详细说明见 [集成指南](./docs/INTEGRATION_GUIDE.md)

## 项目结构

```
src/
├── components/        # Vue 组件
│   ├── ResearchGraph.vue
│   ├── ResearchTimeline.vue
│   ├── ResearchGaps.vue
│   └── ResearchClusters.vue
├── views/            # 页面视图
│   └── ResearchMapView.vue
├── types/            # TypeScript 类型
│   └── research-map.ts
├── utils/            # 工具函数
│   └── api.ts
├── App.vue           # 根组件
├── main.ts           # 入口文件
└── style.css         # 全局样式
```

## 性能优化

- 使用 D3 力导向布局算法
- 支持按需渲染
- 使用 Pinia 状态管理
- 构建时代码分割

## 浏览器支持

- Chrome 90+
- Firefox 88+
- Safari 14+

## License

MIT
