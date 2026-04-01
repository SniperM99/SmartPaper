# Vue 研究地图组件集成指南

## 概述

本项目包含一个完整的 Vue 3 前端组件，用于交互式研究地图可视化。组件使用 D3.js 实现力导向图布局，支持节点拖拽、缩放、筛选等功能。

## 项目结构

```
vue-frontend/
├── src/
│   ├── components/         # Vue 组件
│   │   ├── ResearchGraph.vue       # 主图谱组件
│   │   ├── ResearchTimeline.vue    # 时间线组件
│   │   ├── ResearchGaps.vue        # 研究空白组件
│   │   └── ResearchClusters.vue    # 聚类组件
│   ├── views/              # 页面视图
│   │   └── ResearchMapView.vue     # 研究地图主视图
│   ├── types/              # TypeScript 类型定义
│   │   └── research-map.ts         # 研究地图类型
│   ├── utils/              # 工具函数
│   │   └── api.ts                   # API 请求工具
│   ├── App.vue             # 根组件
│   ├── main.ts             # 入口文件
│   └── style.css           # 全局样式
├── public/                 # 静态资源
├── docs/                   # 文档
├── package.json            # 依赖配置
├── vite.config.ts          # Vite 配置
├── tsconfig.json           # TypeScript 配置
└── index.html              # HTML 入口
```

## 功能特性

### ResearchGraph 组件

- **可视化展示**
  - 7 种实体类型（论文、主题、问题、方法、数据集、指标、空白）
  - 8 种关系类型（研究主题、解决问题、使用方法等）
  - 论文节点显示为矩形，其他节点显示为圆形
  - 提及数大于 1 的节点显示徽章

- **交互功能**
  - 节点点击：显示详情面板
  - 节点悬停：高亮相关边
  - 边点击：显示关系详情
  - 背景点击：取消选择

- **布局算法**
  - 力导向布局（默认）
  - 圆形布局
  - 层级布局

- **缩放和平移**
  - 鼠标滚轮缩放
  - 鼠标拖拽平移
  - 控制按钮：放大、缩小、重置

- **筛选功能**
  - 按实体类型筛选
  - 按最小提及数筛选

### ResearchTimeline 组件

- 按年份显示研究进展
- 每个年份显示：论文数、关键主题、关键方法、年度亮点
- 点击年份显示详情

### ResearchGaps 组件

- 显示研究空白列表
- 按优先级筛选（高/中/低）
- 显示空白类型（明确空白/稀疏主题/缺失评估）
- 点击空白显示详情

### ResearchClusters 组件

- 显示研究聚类
- 每个聚类显示：论文数、主题数、方法数、摘要
- 点击聚类显示详情

## 安装与运行

### 安装依赖

```bash
cd vue-frontend
npm install
```

### 开发模式

```bash
npm run dev
```

开发服务器将运行在 `http://localhost:5173`

### 生产构建

```bash
npm run build
```

构建产物将输出到 `dist/` 目录

## 与 Streamlit 集成

### 方案一：独立页面

将 Vue 前端作为独立应用部署，通过 HTTP API 与 Streamlit 后端通信：

1. 在 Streamlit 中添加 API 端点：
```python
# streamlit.app.py

import json
from fastapi import FastAPI, Request
import uvicorn
from threading import Thread
from application.research_map_service import ResearchMapService

# 创建 FastAPI 应用
api_app = FastAPI()

@api_app.get("/api/research-map")
async def get_research_map(request: Request):
    """获取研究地图数据"""
    cache_keys = request.query_params.get("cacheKeys", "").split(",") if request.query_params.get("cacheKeys") else None

    service = ResearchMapService()

    if cache_keys:
        data = service.build_from_cache_keys(cache_keys)
    else:
        # 获取当前选中的论文
        # TODO: 从 session state 获取选中的论文
        cards = []
        data = service.build_from_cards(cards)

    return data

# 在后台运行 API 服务器
def run_api():
    uvicorn.run(api_app, host="localhost", port=8001)

api_thread = Thread(target=run_api, daemon=True)
api_thread.start()

# 在 Streamlit 页面中使用 iframe
import streamlit.components.v1 as components

components.iframe(
    src="http://localhost:5173",
    height=800,
    scrolling=True
)
```

### 方案二：组件嵌入

将 Vue 构建后的静态文件嵌入 Streamlit：

1. 构建 Vue 应用：
```bash
npm run build
```

2. 在 Streamlit 中使用：
```python
import streamlit.components.v1 as components
import os

# 读取构建后的 HTML
with open("vue-frontend/dist/index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# 替换相对路径为绝对路径
html_content = html_content.replace('href="/', 'href="/@mount/vue-frontend/dist/')
html_content = html_content.replace('src="/', 'src="/@mount/vue-frontend/dist/')

# 渲染组件
components.html(html_content, height=800, scrolling=True)
```

### 方案三：自定义组件

创建 Streamlit 自定义组件：

```python
# vue-frontend/streamlit_component/__init__.py
import streamlit.components.v1 as components
import os

# 构建前端资源
_component_func = components.declare_component(
    "research_map",
    path=os.path.join(os.path.dirname(__file__), "frontend/build")
)

def research_map(data, height=800, key=None):
    """渲染研究地图组件"""
    return _component_func(data=data, height=height, key=key)
```

## API 数据格式

研究地图数据遵循 `ResearchMapSchema` 格式：

```typescript
{
  overview: {
    paper_count: number;
    entity_count: number;
    relation_count: number;
    topic_count: number;
    method_count: number;
  };
  entities: {
    id: string;
    entity_type: 'paper' | 'topic' | 'problem' | 'method' | 'dataset' | 'metric' | 'gap';
    label: string;
    aliases: string[];
    paper_ids: string[];
    mentions: number;
    metadata: Record<string, any>;
  }[];
  relations: {
    source: string;
    target: string;
    relation_type: string;
    weight: number;
    evidence_paper_ids: string[];
    metadata: Record<string, any>;
  }[];
  timeline: {
    year: string;
    paper_ids: string[];
    key_topics: string[];
    key_methods: string[];
    highlights: string[];
  }[];
  clusters: {
    id: string;
    label: string;
    paper_ids: string[];
    topic_ids: string[];
    method_ids: string[];
    summary: string;
  }[];
  gaps: {
    id: string;
    title: string;
    description: string;
    gap_type: 'explicit_gap' | 'sparse_topic' | 'missing_evaluation';
    priority: 'high' | 'medium' | 'low';
    evidence_paper_ids: string[];
    related_entity_ids: string[];
  }[];
}
```

## 性能优化

1. **虚拟滚动**：对于大型图谱，使用虚拟滚动技术减少 DOM 节点数量
2. **Web Worker**：将力导向布局计算放到 Web Worker 中
3. **按需渲染**：只渲染可视区域内的节点和边
4. **数据缓存**：使用 Pinia 管理状态，减少重复请求

## 浏览器兼容性

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## 未来扩展

- [ ] 支持自定义节点样式
- [ ] 支持导出为 PNG/SVG
- [ ] 支持协作标注
- [ ] 支持动画演示
- [ ] 支持 3D 视图

## 许可证

MIT License
