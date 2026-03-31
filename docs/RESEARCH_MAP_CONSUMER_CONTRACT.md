# Research Map 消费契约（UI / 知识卡 / Zotero 联调版）

> 目标：把研究地图骨架进一步收口为**可消费契约**，让 UI、知识卡生成链路、Zotero 映射链路在不依赖 prompt 文本和 Markdown 解析的前提下，直接联调结构化结果。

---

## 1. 适用边界

研究地图当前只接受两类稳定输入：

1. **KnowledgeCard / StructuredAnalysisData** 风格的结构化知识卡
2. 由历史 `structured_data` 适配后的兼容 DTO

研究地图**不应**直接消费：
- 原始 Markdown 报告
- prompt 中的临时文本片段
- UI session state 中拼出来的临时字段
- Zotero 原始 JSON

---

## 2. 输入契约：研究地图最小消费字段

当前 `ResearchMapService.build_from_cards(cards)` 实际依赖以下稳定字段：

### 2.1 顶层字段
- `paper_id: str`
- `metadata: dict`
- `analysis: dict`

### 2.2 metadata 最小字段
- `metadata.title: str = ""`
- `metadata.year: str | int | None = None`
- `metadata.venue: str = ""`
- `metadata.keywords: list[str] = []`

### 2.3 analysis 最小字段
- `analysis.summary_one_sentence: str = ""`
- `analysis.research_problem: str = ""`
- `analysis.topic_tags: list[str] = []`
- `analysis.method_tags: list[str] = []`
- `analysis.dataset_tags: list[str] = []`
- `analysis.application_tags: list[str] = []`
- `analysis.limitations: list[str] = []`
- `analysis.future_work: list[str] = []`
- `analysis.method.overview: str = ""`
- `analysis.experiments.datasets: list[str] = []`
- `analysis.experiments.metrics: list[str] = []`

### 2.4 对 UI / Zotero / 解析的输入要求

#### 对解析 / 知识卡模块
- 必须保证以上字段**存在**，即使为空也要提供默认值
- 研究地图链路只把 `paper_id` 视为稳定主键，不依赖文件名或 cache key
- 若当前仍来自旧 `structured_data`，必须先适配成上述字段结构再进入研究地图

#### 对 Zotero 映射模块
- Zotero 不直接提供 `problem/method/gap` 等研究性字段
- Zotero 侧只负责把 bibliographic metadata 与附件映射进统一 `Paper/ArtifactRef/KnowledgeCard 上游`，再由知识卡产出研究地图输入
- 若 Zotero 导入后尚未形成 ready knowledge card，则**不得**触发研究地图主链路

#### 对 UI 模块
- UI 不应自己拼装知识卡字段，只应消费 application/query 层已整理好的结构

---

## 3. 输出契约：研究地图结构

当前 `ResearchMapService.build_from_cards()` 输出一个 `ResearchMapSchema.model_dump()` 风格对象，固定包含：

- `overview: dict`
- `entities: list[ResearchEntitySchema]`
- `relations: list[ResearchRelationSchema]`
- `timeline: list[ResearchTimelineEventSchema]`
- `clusters: list[ResearchClusterSchema]`
- `gaps: list[ResearchGapSchema]`

### 3.1 overview

最少包含：
- `paper_count`
- `entity_count`
- `relation_count`
- `topic_count`
- `problem_count`
- `method_count`
- `dataset_count`
- `metric_count`
- `gap_count`
- `timeline_years`
- `cluster_count`

### 3.2 entities

每个实体固定字段：
- `id`
- `entity_type`：`paper | topic | problem | method | dataset | metric | gap`
- `label`
- `aliases`
- `paper_ids`
- `mentions`
- `metadata`

### 3.3 relations

每条关系固定字段：
- `source`
- `target`
- `relation_type`
- `weight`
- `evidence_paper_ids`
- `metadata`

关系类型目前包括：
- `studies_topic`
- `addresses_problem`
- `uses_method`
- `evaluates_on_dataset`
- `evaluated_by_metric`
- `related_to`
- `evolves_from`
- `highlights_gap`

### 3.4 timeline

每个时间点固定字段：
- `year`
- `paper_ids`
- `key_topics`
- `key_methods`
- `highlights`

### 3.5 gaps

每个研究空白固定字段：
- `id`
- `title`
- `description`
- `gap_type`: `explicit_gap | sparse_topic | missing_evaluation`
- `priority`: `high | medium | low`
- `evidence_paper_ids`
- `related_entity_ids`

---

## 4. 退化行为（必须稳定）

| 缺失项 | 当前退化行为 | 是否允许继续生成地图 |
|---|---|---|
| `metadata.year` 缺失 | 进入 `timeline.year = "unknown"` 桶 | 是 |
| `metadata.keywords` 缺失 | topic 数量减少，不报错 | 是 |
| `analysis.topic_tags` 缺失 | 回退只用 `keywords` / `application_tags` | 是 |
| `analysis.method_tags` 缺失 | 尝试回退到 `analysis.method.overview` | 是 |
| `analysis.experiments.metrics` 缺失 | 不生成 metric 节点，并可能产生 `missing_evaluation` gap | 是 |
| `limitations/future_work` 缺失 | 不生成 `explicit_gap`，但仍可产出 `sparse_topic` / `missing_evaluation` | 是 |
| 仅 1 篇论文 | cluster / timeline / gap 仍应生成最小结构 | 是 |
| 无任意标签但仍有 title/problem | 至少生成 paper + problem 节点与关系 | 是 |

### 4.1 不允许的退化
- 因年份缺失而抛异常
- 因标签为空而返回半截 dict
- 因 evidence 不完整而跳过整张地图结构
- 回退到解析 Markdown 来补齐主链路字段

---

## 5. 最小输入样例（知识卡）

见：`examples/research_map_minimal_input.json`

该样例覆盖：
- 一篇带完整 topic/method/metric 的论文
- 一篇缺年份、缺 metrics 的论文
- 一篇 Zotero 来源但已沉淀为知识卡的论文

---

## 6. 最小输出样例（研究地图）

见：`examples/research_map_minimal_output.json`

该样例可直接用于：
- UI 静态联调
- 检索/导出层字段对齐
- 回归测试中的快照比对

---

## 7. 面向不同消费方的使用说明

### 7.1 UI 工作台

建议 UI **只消费结构化字段**，不要再解析 Markdown：

- 总览卡片：使用 `overview`
- 主题/方法图谱：使用 `entities + relations`
- 时间线：使用 `timeline`
- 空白发现：使用 `gaps`
- 论文跳转：使用 `paper_ids` / `evidence_paper_ids`

#### UI 最小展示建议
- 左侧概览：`paper_count / topic_count / method_count / gap_count`
- 中间图谱：仅筛 `entity_type in [topic, method, problem, gap]`
- 右侧时间线：按 `timeline.year` 渲染
- 底部空白列表：按 `priority` 和 `gap_type` 分组

### 7.2 检索 / 导出

建议直接复用 ResearchMap 结构，不额外发明导出 DTO：

- 主题检索：遍历 `entities(entity_type=topic)`
- 方法检索：遍历 `entities(entity_type=method)`
- 论文反查：由 `entity.paper_ids` 和 `relation.evidence_paper_ids` 回到论文
- 导出：直接导出 `ResearchMapSchema.model_dump()` 的 JSON

### 7.3 Zotero 联调

Zotero 后续可复用研究地图结果做：
- collection 推荐（按 `paper_ids` / `topic` 聚合）
- tag 建议（按高频 topic/method）
- 研究空白 note 草案（按 `gaps`）

但 Zotero **不直接**消费研究地图内部图结构做主数据源；研究地图只作为派生视图和推荐层。

---

## 8. 接口调用说明

### 8.1 从知识卡直接构建

```python
from application.research_map_service import ResearchMapService

service = ResearchMapService()
research_map = service.build_from_cards(cards)
```

### 8.2 从历史 cache key 构建

```python
from application.multi_paper_service import MultiPaperService

service = MultiPaperService(config)
research_map = service.build_research_map(cache_keys)
```

### 8.3 生成 Markdown 概览（仅展示，不作为主契约）

```python
markdown = service.render_markdown(research_map)
```

> 注意：`render_markdown()` 只是展示层辅助输出，**不是**下游主消费契约。

---

## 9. 当前兼容策略与后续切断点

### 当前兼容策略
- 允许通过旧 `HistoryManager.get_multiple_analyses()` 读取 `structured_data`
- 但研究地图逻辑只消费其中的稳定知识卡字段，不依赖旧 Markdown 文件
- `MultiPaperService.render_research_map()` 当前是兼容入口，便于工作台先接入

### 后续切断点
- 中期：研究地图输入只接受 `KnowledgeCard(status=ready)` DTO
- 中期：UI 改为通过 query/service 消费结构化 `ResearchMap`，不再通过 Markdown 展示主链路
- 长期：切断 `MultiPaperService` 对旧 history 文件格式的直接依赖，改为 repository / query port

---

## 10. 联调验收最小清单

- [ ] 2-3 张最小知识卡可生成稳定 `overview/entities/relations/timeline/gaps`
- [ ] 缺年份、缺标签、缺 metrics 时不崩溃
- [ ] 输出 JSON 可直接被 UI 读取
- [ ] 输出 JSON 可直接用于检索/导出
- [ ] Zotero 只通过知识卡上游进入，不直接写研究字段
- [ ] `render_markdown()` 不是唯一输出

