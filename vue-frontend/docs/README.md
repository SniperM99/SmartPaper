# Vue 研究地图组件文档

## 目录

- [快速开始](#快速开始)
- [功能特性](#功能特性)
- [组件说明](#组件说明)
- [类型定义](#类型定义)
- [API 参考](#api-参考)
- [样式指南](#样式指南)
- [开发指南](#开发指南)

---

## 快速开始

### 安装

```bash
cd vue-frontend
npm install
```

### 开发

```bash
npm run dev
```

### 构建

```bash
npm run build
```

---

## 功能特性

### 研究图谱 (ResearchGraph)

- 🎨 **可视化展示**
  - 7 种实体类型：论文、主题、问题、方法、数据集、指标、空白
  - 8 种关系类型：研究主题、解决问题、使用方法等
  - 论文节点矩形展示，其他节点圆形展示

- 🖱️ **交互功能**
  - 节点拖拽
  - 缩放和平移
  - 节点/边点击查看详情
  - 悬停高亮相关元素

- 📐 **布局算法**
  - 力导向布局（默认）
  - 圆形布局
  - 层级布局

- 🔍 **筛选功能**
  - 按实体类型筛选
  - 按最小提及数筛选

### 研究时间线 (ResearchTimeline)

- 按年份显示研究进展
- 每个年份显示：论文数、关键主题、关键方法、年度亮点
- 点击年份显示详情

### 研究空白 (ResearchGaps)

- 显示研究空白列表
- 按优先级筛选（高/中/低）
- 显示空白类型（明确空白/稀疏主题/缺失评估）
- 点击空白显示详情

### 研究聚类 (ResearchClusters)

- 显示研究聚类
- 每个聚类显示：论文数、主题数、方法数、摘要
- 点击聚类显示详情

---

## 组件说明

### ResearchGraph.vue

主图谱组件，使用 D3.js 实现交互式知识图谱。

#### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data` | `ResearchMapData` | - | 研究地图数据 |
| `loading` | `boolean` | `false` | 加载状态 |

#### Events

| 事件 | 参数 | 说明 |
|------|------|------|
| `nodeClick` | `node: GraphNode` | 节点点击事件 |
| `edgeClick` | `edge: GraphEdge` | 边点击事件 |
| `filterChange` | `filters: FilterOptions` | 筛选变更事件 |

#### Slots

无

### ResearchTimeline.vue

时间线组件，展示研究随时间的演进。

#### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `events` | `TimelineEvent[]` | - | 时间线事件列表 |

#### Events

| 事件 | 参数 | 说明 |
|------|------|------|
| `eventClick` | `event: TimelineEvent` | 事件点击事件 |

### ResearchGaps.vue

研究空白组件，展示领域内的研究机会点。

#### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `gaps` | `ResearchGap[]` | - | 研究空白列表 |

#### Events

| 事件 | 参数 | 说明 |
|------|------|------|
| `gapClick` | `gap: ResearchGap` | 空白点击事件 |

### ResearchClusters.vue

研究聚类组件，展示相似研究的分组。

#### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `clusters` | `ResearchCluster[]` | - | 聚类列表 |

#### Events

| 事件 | 参数 | 说明 |
|------|------|------|
| `clusterClick` | `cluster: ResearchCluster` | 聚类点击事件 |

---

## 类型定义

### ResearchMapData

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

### ResearchEntity

```typescript
interface ResearchEntity {
  id: string
  entity_type: EntityType
  label: string
  aliases: string[]
  paper_ids: string[]
  mentions: number
  metadata: Record<string, any>
}
```

### GraphNode

```typescript
interface GraphNode {
  id: string
  entity_type: EntityType
  label: string
  x?: number
  y?: number
  vx?: number
  vy?: number
  r?: number
  width?: number
  height?: number
  color: string
  size: number
  paper_ids: string[]
  mentions: number
  metadata: Record<string, any>
  selected?: boolean
  highlighted?: boolean
}
```

---

## API 参考

### fetchResearchMap

获取研究地图数据。

```typescript
async function fetchResearchMap(cacheKeys?: string[]): Promise<ResearchMapData>
```

**参数：**

- `cacheKeys` - 知识卡缓存键列表

**返回：**

`Promise<ResearchMapData>` - 研究地图数据

**示例：**

```typescript
const data = await fetchResearchMap(['cache-key-1', 'cache-key-2'])
```

### fetchEntityDetail

获取单个实体详情。

```typescript
async function fetchEntityDetail(entityId: string): Promise<any>
```

**参数：**

- `entityId` - 实体 ID

**返回：**

`Promise<any>` - 实体详情

### searchNodes

搜索节点。

```typescript
async function searchNodes(
  query: string,
  filters?: {
    entityTypes?: string[]
    minMentions?: number
  }
): Promise<any[]>
```

**参数：**

- `query` - 搜索关键词
- `filters` - 筛选条件

**返回：**

`Promise<any[]>` - 搜索结果列表

### exportResearchMap

导出研究地图。

```typescript
async function exportResearchMap(format: 'json' | 'svg' = 'json'): Promise<Blob>
```

**参数：**

- `format` - 导出格式

**返回：**

`Promise<Blob>` - 导出的文件

---

## 样式指南

### 颜色系统

```css
:root {
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-text: #1e293b;
  --color-text-secondary: #64748b;
  --color-border: #e2e8f0;
  --color-bg: #f1f5f9;
}
```

### 实体类型颜色

```typescript
const ENTITY_TYPE_COLORS = {
  paper: '#3b82f6',       // 蓝色
  topic: '#10b981',       // 绿色
  problem: '#f59e0b',     // 橙色
  method: '#8b5cf6',      // 紫色
  dataset: '#ec4899',     // 粉色
  metric: '#06b6d4',      // 青色
  gap: '#ef4444',         // 红色
}
```

### 优先级颜色

```css
.priority-badge.high { color: #dc2626; background: #fef2f2; }
.priority-badge.medium { color: #d97706; background: #fffbeb; }
.priority-badge.low { color: #16a34a; background: #f0fdf4; }
```

---

## 开发指南

### 添加新实体类型

1. 在 `src/types/research-map.ts` 中添加新类型：
```typescript
export type EntityType = ... | 'new_type'
```

2. 在 `ENTITY_TYPE_COLORS` 中添加颜色：
```typescript
const ENTITY_TYPE_COLORS = {
  ...
  new_type: '#xxxxxx',
}
```

3. 在 `ENTITY_TYPE_LABELS` 中添加标签：
```typescript
const ENTITY_TYPE_LABELS = {
  ...
  new_type: '新类型',
}
```

### 自定义布局算法

在 `ResearchGraph.vue` 中添加新布局：

```typescript
const applyCustomLayout = (layoutNodes: GraphNode[], ...) => {
  // 自定义布局逻辑
}

// 在 applyLayout 中添加
case 'custom':
  applyCustomLayout(layoutNodes, ...)
  break
```

### 性能优化建议

1. 使用 `v-memo` 优化列表渲染
2. 大型图谱使用虚拟滚动
3. 使用 Web Worker 处理复杂计算
4. 合理使用 `computed` 缓存计算结果

---

## 更多文档

- [集成指南](./INTEGRATION_GUIDE.md) - 与 Streamlit 集成
- [安装指南](./SETUP_GUIDE.md) - 安装和部署
- [项目主文档](../README.md) - 项目概述
