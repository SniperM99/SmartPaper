# Zotero → 统一 Schema 消费闭环复核说明

> 复核对象：工作台 UI、研究地图、Zotero 映射到统一 schema 后的消费闭环
> 关注字段：`paper_id`、`collections`、`tags`、`analysis_refs`、`library_context`

---

## 1. 快速结论

### 结论
**基本闭环，但仍是“上游映射完整、下游消费部分切换”的状态。**

### 当前状态拆分

#### 已基本稳定
- Zotero → `paper_id`
- Zotero → `library_context`
- Zotero → `import_context`
- Zotero → `analysis_refs` 回写载荷
- Zotero → `collections/tags/attachments` 结构化映射

#### 仍需下游继续切换
- 工作台仍以 `cache_key` 为主视图键，尚未切到 `paper_id`
- 工作台当前未稳定消费 `library_context.collections/tags/analysis_refs`
- 研究地图当前主消费字段仍是 `metadata.keywords` / `analysis.*tags`，尚未直接利用 `library_context` 作为辅助先验
- 研究地图实现中仍保留 `paper_id or cache_key` 的兼容回退，说明切换未完全完成

---

## 2. paper_id 闭环复核

## 2.1 上游是否稳定

是。

来源：
- `NormalizedPaperSchema.paper_id`
- `StructuredAnalysisData.paper_id`
- `LibraryPaperRecord.paper_id`
- `ZoteroItemMapper.map_item()` 会为 Zotero 条目生成稳定 `paper_id`

## 2.2 工作台消费状态

### 现状
工作台主视图仍以 `cache_key` 为主：
- `interfaces/web/workbench_state.py`
  - `active_paper_key`
  - `compare_keys`
- `application/workbench_service.py`
  - 返回的库条目仍显式暴露 `cache_key`
  - 未把 `paper_id` 提升为主展示/主跳转字段

### 风险
- UI 若继续以 `cache_key` 为主，会导致 Zotero 导入记录与普通解析记录的统一定位成本升高
- `paper_id` 无法成为工作台、研究地图、Zotero 间的唯一锚点

### 建议
- 工作台状态主键切换为 `paper_id`
- `cache_key` 仅保留为历史记录读取兼容字段，不再作为 UI 主键
- 详情跳转、对比选择、研究地图反查统一传 `paper_id`

---

## 3. collections / tags 闭环复核

## 3.1 上游映射是否稳定

是，且分两层：

### 轻量上下文
- `import_context.collection_keys`
- `import_context.collection_paths`
- `import_context.tags`

### 完整外部库上下文
- `library_context.collections[]`
- `library_context.tags[]`

Zotero mapper 侧：
- `tags[].tag -> ZoteroTag.name`
- `collections -> ZoteroCollection.path`

## 3.2 工作台消费状态

### 现状
工作台当前库条目主要消费：
- `title/year/venue/authors/keywords/summary/method_tags/...`

尚未见稳定消费：
- `library_context.collections`
- `library_context.tags`
- `import_context.collection_paths`

### 风险
- Zotero 导入的 collection 层级和 tag 语义虽然已进入统一 schema，但未真正进入工作台筛选/展示闭环
- UI 仍更像“分析卡工作台”，而非“统一文献库工作台”

### 建议
工作台切换顺序：
1. 优先读 `library_context.collections[].path`
2. 回退读 `import_context.collection_paths`
3. 标签优先读 `library_context.tags[].name`
4. 回退读 `import_context.tags`
5. 最后才回退 `metadata.keywords`

### 缺省/降级要求
- `collections` 必须允许为空列表
- `tags` 必须允许为空列表
- UI 筛选器应支持“无 collection / 无 tag”状态，不应报错或隐藏记录

---

## 4. analysis_refs 闭环复核

## 4.1 上游映射是否稳定

基本稳定。

当前存在位置：
- `import_context.analysis_refs`
- `library_context.analysis_refs`
- `LibraryPaperRecord.analysis_refs`
- `ZoteroIntegrationService.attach_analysis_reference()`
- `ZoteroIntegrationService.prepare_writeback_payload()`

说明：
- Zotero 回写载荷已经可以携带 `analysis_refs`
- schema 侧也已经预留稳定字段

## 4.2 工作台消费状态

### 现状
工作台当前未显式消费 `analysis_refs`。

### 风险
- UI 无法稳定展示“该论文是否已有分析产物、有哪些分析结果可回跳”
- Zotero 导入论文与 SmartPaper 分析结果的联结关系在页面层不可见

### 建议
工作台应新增：
- `analysis_refs` 读取
- “已分析 / 未分析” 状态判断
- 从论文卡片跳转到分析结果详情的入口

### 缺省/降级要求
- `analysis_refs` 必须始终存在为 `list`
- 空列表表示“尚未挂接分析结果”，而不是异常

---

## 5. library_context 闭环复核

## 5.1 schema 侧是否完整

是。

`library_context` 当前已包含：
- `zotero`
- `tags`
- `collections`
- `attachments`
- `sync_state`
- `analysis_refs`

这意味着 Zotero 外部库信息已经不再只是导入期临时信息，而是统一 schema 的稳定组成部分。

## 5.2 工作台消费状态

### 现状
未形成稳定消费闭环。

`application/workbench_service.py` 当前构建条目时，未把 `library_context` 投影为页面可直接消费的字段。

### 建议
至少新增以下视图字段：
- `paper_id`
- `collection_paths`
- `tag_names`
- `analysis_refs`
- `library_sync_status`
- `zotero_item_key`

## 5.3 研究地图消费状态

### 现状
研究地图主链路尚未直接读 `library_context`。
当前主要使用：
- `metadata.keywords`
- `analysis.topic_tags`
- `analysis.method_tags`
- `analysis.application_tags`
- `analysis.dataset_tags`

### 风险
- Zotero collection/tag 无法作为研究地图的稳定辅助先验进入聚类/筛选
- 文献库视角与研究地图视角仍是弱耦合

### 建议
研究地图可按“辅助先验”而非“主字段”接入：
1. `library_context.collections[].path`
2. `library_context.tags[].name`
3. 回退 `import_context.collection_paths/tags`
4. 再回退 `metadata.keywords`

### 降级要求
- 即使 `library_context` 为空，也必须可正常构建地图
- `library_context` 不完整时，不得回退去解析原始 Markdown 或 Zotero raw payload

---

## 6. 仍需注意的兼容与降级点

## 6.1 工作台侧

### 仍需注意
- 当前主键仍偏 `cache_key`
- 尚未稳定消费 `paper_id`
- 尚未稳定消费 `library_context.*`
- 与 Zotero 的闭环更多停留在文档/服务层，而非页面层

### 最低补强建议
- 工作台条目统一补出：
  - `paper_id`
  - `collection_paths`
  - `tag_names`
  - `analysis_refs`
  - `zotero_item_key`
  - `library_sync_status`

## 6.2 研究地图侧

### 仍需注意
- 实现里仍有 `paper_id or cache_key` 回退
- 尚未显式接入 `library_context` 作为辅助先验
- 对 `analysis_refs` 的消费更多停留在契约文档层

### 最低补强建议
- 研究地图内部主键只认 `paper_id`
- 若需要展示/筛选 Zotero 语义，优先读 `library_context`
- `analysis_refs` 仅用于回跳分析详情，不作为地图构建主输入

## 6.3 Zotero 侧

### 仍需注意
- `import_context.tags` 与 `library_context.tags` 可能并存，消费方应优先结构化对象
- `collection_keys` 与 `collection_paths` 语义不同，不能混用
- `analysis_refs` 为空必须视为正常状态
- 无主附件 PDF 时，应允许记录仅作为文献库条目存在，不强行进入解析链路

---

## 7. QA 最终综合复审建议

### 可判“基本闭环”的部分
- Zotero → 统一 schema 的字段映射
- `paper_id` 的统一主键设计
- `analysis_refs` 的写回预留
- `library_context` 的结构化承载能力

### 仍建议作为最终复审提醒项保留
1. 工作台是否已切到 `paper_id` 主键
2. 工作台是否已真正展示 `collections/tags/analysis_refs`
3. 研究地图是否已把 `library_context` 作为辅助先验接入
4. `paper_id or cache_key` 的兼容回退是否有明确切断计划
5. 空 `collections/tags/analysis_refs/library_context` 是否都能稳定降级为默认空结构
