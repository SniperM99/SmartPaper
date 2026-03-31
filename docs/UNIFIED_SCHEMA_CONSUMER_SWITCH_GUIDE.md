# 统一 Schema 下游消费切换指南

> 适用对象：工作台 UI、研究地图、Zotero 集成
> 上游对象：`NormalizedPaperSchema`、`StructuredAnalysisData`
> 目标：让各消费方直接面向稳定字段消费，减少跨模块适配与 legacy 入口依赖。

---

## 1. 总原则

### 1.1 两层对象职责

- `NormalizedPaperSchema`
  - 用于**导入/解析阶段**的统一中间表示
  - 适合消费：原始来源、正文、章节、引用、附件、导入上下文
- `StructuredAnalysisData`
  - 用于**单篇知识卡完成态**
  - 适合消费：元数据、摘要、方法/问题/实验标签、质量评分、追踪信息、外部库上下文

### 1.2 下游切换原则

- UI、研究地图、Zotero **不要再按来源类型分支读取不同 dict**
- UI 详情、研究地图、Zotero 回写优先消费 `StructuredAnalysisData`
- 仅在“论文刚导入、尚未完成知识卡抽取”时，才消费 `NormalizedPaperSchema`
- 所有模块统一以 `paper_id` 作为主键，不再依赖：
  - `cache_key`
  - 文件名
  - URL basename
  - Zotero item key 作为内部主键

---

## 2. 统一主键：paper_id

### 2.1 稳定消费建议

所有下游统一使用：
- `paper_id`

用途：
- UI：论文详情跳转、主论文选择、对比分析
- 研究地图：论文节点主键、实体/关系回溯
- Zotero：系统内论文与外部条目映射锚点

### 2.2 禁止继续依赖的旧字段

不要再把以下字段当主键：
- `cache_key`
- `source_hash`
- `original_source`
- 本地文件名
- `zotero_item_key`（它是外部主键，不是系统主键）

### 2.3 推荐做法

- UI 状态里只存 `paper_id`
- 研究地图 relation/entity 反查论文时只传 `paper_id`
- Zotero 映射层保存 `paper_id <-> zotero item key` 的绑定关系

---

## 3. collections / tags 的稳定消费方式

## 3.1 推荐优先级

如果消费方需要 collections / tags，按以下顺序读取：

### 优先读取（结构化完成态）
- `structured_data.library_context.collections`
- `structured_data.library_context.tags`
- `structured_data.library_context.analysis_refs`

### 兼容读取（导入上下文/轻量上下文）
- `structured_data.import_context.collection_keys`
- `structured_data.import_context.collection_paths`
- `structured_data.import_context.tags`
- `structured_data.import_context.analysis_refs`

### 导入阶段对象
- `normalized_paper.library_context.collections`
- `normalized_paper.library_context.tags`
- `normalized_paper.import_context.collection_keys`
- `normalized_paper.import_context.collection_paths`
- `normalized_paper.import_context.tags`

## 3.2 字段职责区分

### `library_context.collections`
完整 collection 对象列表，适合 UI/Zotero 直接展示与回写：
- `key`
- `name`
- `path`
- `parent_key`

### `import_context.collection_keys`
轻量键列表，适合导入期/兼容期使用。

### `import_context.collection_paths`
轻量路径列表，适合：
- UI breadcrumb
- 研究地图主题先验
- Zotero collection 推荐

### `library_context.tags`
结构化标签对象，适合颜色/类型/后续回写：
- `name`
- `color`
- `tag_type`

### `import_context.tags`
轻量字符串列表，适合导入期与无颜色/无类型场景。

---

## 4. analysis_refs 的稳定消费方式

## 4.1 含义

`analysis_refs` 表示该论文关联的分析产物引用，例如：
- `saved_analyses/analysis_xxx.md`
- 未来的结构化知识卡快照路径
- 对应的 Zotero note / export artifact 标识

## 4.2 推荐读取位置

优先读取：
- `structured_data.library_context.analysis_refs`

兼容读取：
- `structured_data.import_context.analysis_refs`

## 4.3 下游消费建议

### UI
用于：
- 打开最新分析结果
- 展示“已分析 / 未分析”状态
- 提供分析结果下载/预览入口

### Zotero
用于：
- 回写 note 时建立关联
- 避免重复生成 note
- 增量同步时识别哪些分析结果已挂接

### 研究地图
不建议把 `analysis_refs` 作为主数据源；
只把它作为“从地图回跳到分析结果”的辅助入口。

---

## 5. UI 消费切换建议

## 5.1 UI 列表页

### 应直接消费
- `paper_id`
- `metadata.title`
- `metadata.authors`
- `metadata.year`
- `metadata.venue`
- `document.abstract`
- `analysis.summary_one_sentence`
- `quality_control.overall_reliability`
- `library_context.collections[].path` 或 `import_context.collection_paths`
- `library_context.tags[].name` 或 `import_context.tags`

### 不应继续消费
- `cache_key`
- `history.json` 内部索引细节
- 原始 markdown 文本解析出的临时标题/标签

## 5.2 UI 详情页

### 应直接消费
- `analysis.research_problem`
- `analysis.method.overview`
- `analysis.method_tags`
- `analysis.dataset_tags`
- `analysis.application_tags`
- `analysis.innovation_points`
- `analysis.limitations`
- `analysis.future_work`
- `citations`
- `attachments`
- `trace`

### 附件展示建议

优先展示：
- `attachments`
- `library_context.attachments`

若两者同时存在：
- `attachments` 作为通用附件入口
- `library_context.attachments` 作为 Zotero 外部附件视图

## 5.3 UI 工作流状态

建议用以下规则判断：
- 已导入未分析：有 `NormalizedPaperSchema.paper_id`，但无 `StructuredAnalysisData.analysis.summary_one_sentence`
- 已分析：存在 `StructuredAnalysisData` 且 `analysis_refs` 非空或 `summary_one_sentence` 非空
- 可疑质量：`quality_control.overall_reliability < 阈值`

---

## 6. 研究地图消费切换建议

## 6.1 研究地图只消费完成态知识卡

推荐输入：
- `StructuredAnalysisData[]`

最小稳定字段：
- `paper_id`
- `metadata.title`
- `metadata.year`
- `metadata.keywords`
- `analysis.research_problem`
- `analysis.topic_tags`
- `analysis.method_tags`
- `analysis.dataset_tags`
- `analysis.application_tags`
- `analysis.method.overview`
- `analysis.experiments.datasets`
- `analysis.experiments.metrics`
- `analysis.limitations`
- `analysis.future_work`

## 6.2 collections / tags 的使用建议

研究地图不要把 Zotero collections / tags 当主契约字段，但可以作为辅助先验：

优先辅助字段：
- `library_context.collections[].path`
- `library_context.tags[].name`

兼容辅助字段：
- `import_context.collection_paths`
- `import_context.tags`

用途：
- 主题聚类命名提示
- collection 推荐
- 研究域筛选初值

## 6.3 analysis_refs 的使用建议

研究地图不要解析 `analysis_refs` 内容本身；
只把它作为：
- 从地图卡片跳回分析结果页面的链接源

---

## 7. Zotero 消费切换建议

## 7.1 主消费对象

Zotero 集成优先消费：
- `StructuredAnalysisData.library_context`
- `StructuredAnalysisData.import_context`
- `StructuredAnalysisData.metadata`
- `StructuredAnalysisData.attachments`

## 7.2 关键字段读取建议

### 论文绑定
- 内部主键：`paper_id`
- 外部条目标识：`library_context.zotero.item_key` 或 `import_context.zotero_item_key`
- 外部库标识：`library_context.zotero.library_id` 或 `import_context.zotero_library_id`

### 标签
优先：
- `library_context.tags[].name`

兼容：
- `import_context.tags`
- `metadata.keywords`

### collections
优先：
- `library_context.collections[].path`
- `library_context.collections[].key`

兼容：
- `import_context.collection_paths`
- `import_context.collection_keys`

### 分析结果反挂
优先：
- `library_context.analysis_refs`

用于：
- note 回写
- 增量同步去重
- 分析结果关联状态

## 7.3 不应继续依赖的旧入口

不要继续在 UI / application 层直接消费原始 Zotero payload：
- `item.data.tags`
- `item.data.collections`
- `attachment.data.*`

这些应先经 mapper 归一化到：
- `library_context`
- `import_context`
- `attachments`

---

## 8. 切换期兼容策略

## 8.1 推荐兼容读取顺序

如果下游要读取标签/集合/分析引用，建议使用统一 helper 逻辑：

1. 先读 `library_context.*`
2. 再读 `import_context.*`
3. 最后才做 legacy fallback

## 8.2 legacy fallback 仅限过渡期

允许的过渡期 fallback：
- `cache_key -> paper_id`（仅迁移脚本）
- `metadata.extra["tags"] -> import_context.tags`
- `metadata.extra["collections"] -> import_context.collection_paths`

不建议长期保留：
- UI 直接读 `saved_analyses/history.json`
- 研究地图直接解析 markdown 报告正文
- Zotero 模块直接把 raw payload 透传给页面层

---

## 9. 建议新增的稳定 helper（供后续实现）

建议后续统一提供一组只读 helper，减少各模块重复 fallback：

- `get_paper_id(card) -> str`
- `get_collection_paths(card) -> list[str]`
- `get_tag_names(card) -> list[str]`
- `get_analysis_refs(card) -> list[str]`
- `get_primary_attachment(card) -> dict | None`
- `is_analysis_ready(card) -> bool`

建议这些 helper 面向：
- `StructuredAnalysisData`
- `NormalizedPaperSchema`

而不是面向 legacy dict 任意拼字段。

---

## 10. 最终切换清单

### UI
- [ ] 统一用 `paper_id` 作为页面状态主键
- [ ] 标签/集合切换到 `library_context` / `import_context`
- [ ] 分析结果入口切换到 `analysis_refs`
- [ ] 不再直接读底层历史索引字段

### 研究地图
- [ ] 输入统一为 `StructuredAnalysisData[]`
- [ ] 仅把 collections/tags 作为辅助先验，不作为主契约
- [ ] 论文回跳统一使用 `paper_id`
- [ ] 不再直接消费原始 markdown 文本

### Zotero
- [ ] `paper_id` 作为系统内稳定主键
- [ ] tags/collections/attachments 全部经 mapper 归一化
- [ ] `analysis_refs` 作为分析结果反挂入口
- [ ] 不再把 raw Zotero payload 直接暴露给 UI / service
