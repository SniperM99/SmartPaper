# Research Map → 工作台图谱展示对接说明

> 目标：在研究地图消费契约与 query DTO 基础上，为工作台图谱展示提供可直接接入的稳定视图模型、最小展示数据集、空态/退化态建议与字段映射说明。

---

## 1. 推荐接入层次

推荐链路：

`KnowledgeCard -> ResearchMap -> Query DTO -> Graph View DTO -> Streamlit / 前端图谱组件`

UI 图谱组件**不应**直接消费：
- 原始 `structured_data`
- 原始 Markdown
- 临时 node/edge dict
- Zotero 原始 payload

UI 图谱组件应消费稳定视图 DTO：
- `domain/research_map_view.py`
- 主对象：`ResearchMapGraphViewSchema`

---

## 2. 节点/边视图模型

### 2.1 节点 `GraphNodeViewSchema`

最小字段：
- `id`
- `kind`
- `label`
- `subtitle`
- `size`
- `color_token`
- `paper_ids`
- `tags`
- `collections`
- `analysis_refs`
- `badges`
- `metadata`

#### 字段语义
- `id`：直接对齐 research map entity id
- `kind`：`paper/topic/problem/method/dataset/metric/gap`
- `subtitle`：给 UI 卡片/tooltip 的二级说明
- `size`：前端推荐节点大小，可由 mentions/paper_count 映射
- `tags`：用于前端高亮、筛选芯片，不等于 Zotero tags 的全部原始集合
- `collections`：关联 collection path 或 key，用于 Zotero 联动提示
- `analysis_refs`：反查到知识卡或分析记录
- `metadata`：例如 `year`、`venue`、`priority`、`mentions`

### 2.2 边 `GraphEdgeViewSchema`

最小字段：
- `id`
- `kind`
- `source`
- `target`
- `label`
- `weight`
- `paper_ids`
- `analysis_refs`
- `metadata`

#### 字段语义
- `source/target`：必须可与节点 `id` 对齐
- `label`：建议给前端直接展示中文关系文案，如“使用方法”“指出空白”
- `weight`：前端可映射为边粗细/透明度
- `paper_ids`：支持点击边后反查论文
- `analysis_refs`：支持跳转知识卡或分析详情

---

## 3. Graph View 根对象

`ResearchMapGraphViewSchema` 最少包含：
- `map_id`
- `state`
- `layout_hint`
- `nodes`
- `edges`
- `legend`
- `empty_state`
- `filters_applied`
- `stats`

### 3.1 state 语义
- `ready`：正常图谱
- `empty`：当前筛选条件下无结果
- `degraded`：已有部分图谱，但因字段缺失降级
- `failed`：查询/构图失败

### 3.2 layout_hint 建议
- `force`：常规关系图
- `timeline`：年份主导布局
- `cluster`：聚类簇优先布局
- `radial`：以主论文为中心展开

---

## 4. 最小展示数据集

建议工作台至少支持以下最小展示集合：

### 4.1 最小节点集
- 1 个 `paper` 节点
- 1 个 `problem` 节点
- 1 个 `method` 或 `topic` 节点

### 4.2 最小边集
- `paper -> problem`
- `paper -> method/topic`

### 4.3 最小顶栏统计
- `paper_count`
- `node_count`
- `edge_count`
- `gap_count`

### 4.4 最小 tooltip 建议

#### Paper 节点 tooltip
- 标题
- 年份 / venue
- summary（若有）
- `paper_id`

#### Topic/Method/Problem 节点 tooltip
- label
- mentions / paper count
- 相关论文数
- 关联 tags / collections（若有）

#### Gap 节点 tooltip
- title
- priority
- gap_type
- evidence paper count

---

## 5. 空态 / 退化态展示建议

### 5.1 空态 `state=empty`

适用场景：
- 当前筛选条件没有命中结果
- 当前论文集合为空

建议文案：
- 标题：`暂无可展示的研究地图结果`
- 描述：`当前筛选条件下没有匹配的节点或关系。`
- 建议动作：
  - 放宽年份或标签过滤
  - 至少选择 1 篇已完成知识卡的论文
  - 切换到 timeline/gaps 视图查看可用信息

### 5.2 退化态 `state=degraded`

适用场景：
- 年份缺失，只能放入 `unknown` 时间桶
- metrics 缺失，关系图中没有 metric 节点
- tags / collections / analysis_refs 不完整

建议文案：
- 标题：`研究地图已降级生成`
- 描述：`部分字段缺失，已使用最小可用结构生成图谱。`
- 建议动作：
  - 补齐年份、method tags、metrics
  - 回到知识卡页检查结构化字段完整度

### 5.3 失败态 `state=failed`

适用场景：
- query service / graph adapter 异常

建议文案：
- 标题：`图谱加载失败`
- 描述：`研究地图视图构建失败，请稍后重试或切换到列表视图。`
- 建议动作：
  - 查看日志
  - 切换到 entities/gaps 列表视图

---

## 6. 与 `paper_id / tags / collections / analysis_refs` 的映射关系

### 6.1 `paper_id`
- 是图谱中最稳定的跨模块主键
- 节点和边都应保留 `paper_ids`
- UI 点击节点/边后，应通过 `paper_ids` 跳转论文库或详情页

### 6.2 `tags`
建议来源优先级：
1. research map 的 topic/method/application 聚合标签
2. knowledge card 中的 `metadata.keywords`
3. Zotero `tags`

使用建议：
- `tags` 用于前端高亮、筛选和 badge 展示
- 不要求把 Zotero tags 原样全部铺开到图谱；可只保留与当前节点直接相关的标签子集

### 6.3 `collections`
建议来源：
- `ImportContextSchema.collection_paths`
- `ImportContextSchema.collection_keys`
- `LibraryPaperRecord.collections[].path`

使用建议：
- 图谱中不必把 collection 单独建成节点
- 但可在 paper/topic/method 节点上显示来源 collection path，用于 Zotero 联动提示
- 当多个 paper 来自同一 collection 时，可作为 cluster/timeline 的辅助说明

### 6.4 `analysis_refs`
建议来源：
- `ImportContextSchema.analysis_refs`
- `LibraryPaperRecord.analysis_refs`
- 历史 `cache_key` / analysis result id

使用建议：
- 作为“从图谱反查知识卡/分析详情”的稳定引用
- UI 点击节点/边后可展示“查看知识卡”“打开分析结果”入口
- `analysis_refs` 可为空，但字段必须存在为 list

---

## 7. 节点/边到 UI 组件的建议映射

### 7.1 节点颜色建议
- `paper`：中性色
- `topic`：蓝色系
- `problem`：橙色系
- `method`：绿色系
- `dataset`：紫色系
- `metric`：青色系
- `gap`：红色系

### 7.2 节点大小建议
- `paper`：按是否主论文 / 是否对比集高亮
- 其他节点：按 `mentions` 或 `len(paper_ids)` 映射

### 7.3 边样式建议
- `evolves_from`：虚线 + 方向箭头
- `highlights_gap`：高亮色边
- `related_to`：低对比度连线
- `uses_method` / `studies_topic`：常规实线

---

## 8. 最小展示样例

见：`examples/research_map_graph_view_minimal.json`

该样例覆盖：
- 1 个 paper 节点
- 1 个 topic 节点
- 1 个 method 节点
- 2 条最小边
- `paper_id/tags/collections/analysis_refs` 完整映射
- `ready` 状态和空态建议字段

---

## 9. 与现有 query DTO 的关系

- `docs/RESEARCH_MAP_QUERY_CONTRACT.md`：定义查询请求/响应
- 本文：定义图谱展示视图 DTO

推荐 UI 接入方式：
1. 用 query DTO 获取 entities/relations/gaps/timeline
2. 在 application/query adapter 层转成 `ResearchMapGraphViewSchema`
3. 前端只渲染 graph view DTO

---

## 10. 联调最小清单

- [ ] 至少 1 组 graph view DTO 样例可被 UI 直接读取
- [ ] 空态 / 退化态 / 失败态文案明确
- [ ] `paper_ids/tags/collections/analysis_refs` 字段始终存在
- [ ] 节点/边可反查论文或分析详情
- [ ] UI 不直接读取 Zotero 原始 payload 或 structured_data 原始树
