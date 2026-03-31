# SmartPaper 跨模块集成契约与迁移切断点

> 目标：为解析 → 知识卡 → 研究地图 → Zotero → UI 的跨模块协作提供统一契约，作为本轮升级的收口基线。
> 适用范围：`application/`、`domain/`、`infrastructure/`、`interfaces/` 及所有仍需兼容 `src/` 旧模块的迁移代码。

---

## 1. 当前阶段的统一约束

### 1.1 第一阻塞门槛

在任何模块功能验收前，必须先满足：

- `pytest --collect-only` **可收集**
- 不新增 `sys.path` 注入
- 不新增跨层直接耦合
- 新增结构必须能被下游消费，而不是只定义半截数据

### 1.2 五项统一验收口径（所有模块必须显式自查）

#### A. 接口一致性
- 新代码不得继续依赖已删除或计划删除的旧入口，如 `core.smart_paper_core`、`core.llm_wrapper` 等。
- 接口层只能调用 application façade / use case，不得直接拼装 infrastructure 或 legacy `src/*`。
- application 不得再直接新增对 `src/*`、`core/*` 的反向耦合；若迁移期必须复用，需通过适配层隔离。
- **禁止新增**硬编码绝对路径与 `sys.path.insert(...)`。

#### B. 数据模型完整性
- 字段命名、层级、默认值、可空性必须稳定。
- 新增字段必须说明被谁消费：研究地图、Zotero、UI、导出层。
- 同一语义不得在多处使用不同字段名表达，如 `summary` / `summary_one_sentence` / `short_summary` 并存。

#### C. 回归风险
- 旧工作流仍保留时，必须写清兼容入口、兼容期限和切断点。
- 若故意切断旧入口，需在文档中明确“替代入口是什么、何时移除、谁负责迁移”。

#### D. 可测试性
- 至少保证 import 可收集。
- 优先提供纯单元测试和 schema/adapter 测试。
- 在线 LLM、外部 PDF 服务、Zotero API 不得成为最小验收闭环的必经门槛。

#### E. 工作流闭环
- 任一模块交付都必须说明自己处于闭环中的哪一段：
  `输入 -> 解析/转换 -> 结构化输出 -> 存储/展示 -> 下游消费`
- 不接受只增加类型定义、不接入存储/查询/展示的“半截落地”。

---

## 2. 目标架构中的跨模块边界

```text
Interfaces
  └─ 调用 Application façade / use cases
Application
  ├─ 编排导入、解析、知识卡生成、研究地图聚合、Zotero 同步
  ├─ 依赖 Domain 抽象与 Ports
  └─ 不直接依赖 legacy src 细节
Domain
  ├─ Paper / KnowledgeCard / ResearchMap / ZoteroLink 等核心模型
  ├─ 定义仓储接口、查询契约、同步边界
  └─ 不依赖 Streamlit、LLM SDK、Zotero SDK
Infrastructure
  ├─ 实现 PDF/LLM/Storage/Zotero/Export 等 Ports
  └─ 可包含 legacy 适配器，但不能反向污染 domain/application
Legacy src
  └─ 冻结为兼容实现，仅允许被 adapter 调用，不得继续扩散引用
```

### 强制依赖规则

- `interfaces -> application`
- `application -> domain + application ports`
- `infrastructure -> domain/application ports 的实现`
- `domain -> 不依赖任何 interfaces/infrastructure/legacy`
- `legacy src -> 只能由 adapter 包装后被调用`

### 禁止新增的耦合方式

- Streamlit / CLI 直接 import `HistoryManager`、`DocumentConverter`、`LLMClient`
- application 直接读写 `saved_analyses/*.jsonl/*.csv` 具体文件细节
- domain 暴露 Zotero 原始 API 字段、Streamlit session state 字段
- 为了解决 import 问题继续增加 `sys.path.insert(...)`
- 通过临时 dict 约定代替稳定 schema

---

## 3. 统一共享数据模型

下列模型为跨模块共享语义边界。实现可分散，但字段语义必须一致。

## 3.1 Paper（论文主实体）

代表一个被导入/解析/索引的文献对象，是知识卡与 Zotero 映射的上游主键来源。

### 最低必备字段
- `paper_id: str`：系统内部稳定 ID；对文件导入和 URL 导入都必须可复现
- `source_type: Literal[file, url, zotero, manual]`
- `source_uri: str`：原始来源路径/URL/Zotero item key
- `title: str = ""`
- `authors: list[str] = []`
- `year: str | None = None`
- `venue: str = ""`
- `abstract: str = ""`
- `doi: str = ""`
- `keywords: list[str] = []`
- `artifacts: list[ArtifactRef] = []`
- `provenance: Provenance`

### 下游消费要求
- 知识卡生成必须至少能读取 `paper_id/title/authors/year/abstract`
- Zotero 映射必须至少能读取 `source_type/source_uri/doi/title`
- UI 列表页必须至少能读取 `paper_id/title/year/venue`

## 3.2 ArtifactRef（附件/载体引用）

表示 Paper 关联的 PDF、Markdown、中间抽取结果、图片等。

### 最低必备字段
- `artifact_id: str`
- `paper_id: str`
- `artifact_type: Literal[pdf, markdown, structured_json, image, note, attachment]`
- `uri: str`
- `mime_type: str = ""`
- `role: Literal[primary, derived, supplementary] = "derived"`
- `created_at: str | None = None`

### 下游消费要求
- 解析模块必须产出至少一个 `primary pdf` 或 `markdown`
- Zotero 导入模块必须能够把附件映射为 ArtifactRef
- UI 详情页必须基于 ArtifactRef 决定下载/预览入口

## 3.3 KnowledgeCard（单篇结构化知识卡）

它是“单篇论文沉淀完成”的完成态，不等于原始分析 Markdown。

### 最低必备字段
- `card_id: str`
- `paper_id: str`
- `version: str`
- `metadata: CardMetadata`
- `document: CardDocument`
- `analysis: CardAnalysis`
- `evidence: list[Evidence] = []`
- `quality: QualityReport`
- `trace: TraceInfo`
- `status: Literal[draft, ready, failed]`

### CardMetadata 最低字段
- `title`
- `authors`
- `year`
- `venue`
- `keywords`

### CardDocument 最低字段
- `abstract`
- `sections: list[str]`
- `references: list[str]`

### CardAnalysis 最低字段
- `summary_one_sentence`
- `research_problem`
- `background`
- `method.overview`
- `experiments.datasets`
- `experiments.metrics`
- `contributions`
- `innovation_points`
- `limitations`
- `method_tags`
- `dataset_tags`
- `application_tags`
- `future_work`

### 下游消费要求
- 研究地图只能消费 `status=ready` 的 KnowledgeCard
- 对比分析至少依赖：`summary_one_sentence/research_problem/method_tags/innovation_points/limitations`
- UI 的论文详情、对比、筛选都优先使用 KnowledgeCard，而不是原始 Markdown
- Zotero 回写若未来需要生成 note，也以 KnowledgeCard 为上游

## 3.4 ResearchEntity（研究地图节点）

研究地图中的统一节点抽象。

### 最低必备字段
- `entity_id: str`
- `entity_type: Literal[topic, problem, method, dataset, metric, finding, gap, venue, author]`
- `name: str`
- `aliases: list[str] = []`
- `description: str = ""`
- `evidence_paper_ids: list[str] = []`
- `attributes: dict = {}`

### 下游消费要求
- 研究地图工程师可扩展 `attributes`，但不得破坏固定头部字段
- UI 可按 `entity_type/name/description/evidence_paper_ids` 直接渲染

## 3.5 ResearchRelation（研究地图边）

### 最低必备字段
- `relation_id: str`
- `source_entity_id: str`
- `target_entity_id: str`
- `relation_type: Literal[studies, uses, compares, improves, evaluates_on, measured_by, contradicts, extends, cites, belongs_to, indicates_gap]`
- `paper_ids: list[str] = []`
- `weight: float = 1.0`
- `evidence: list[Evidence] = []`

### 下游消费要求
- 任一 relation 都必须可追溯到至少一篇 `paper_id` 或 evidence
- UI 图谱与时间线都不得消费“无来源关系”

## 3.6 ResearchMap（跨论文聚合结果）

### 最低必备字段
- `map_id: str`
- `scope: MapScope`
- `paper_ids: list[str]`
- `entities: list[ResearchEntity]`
- `relations: list[ResearchRelation]`
- `timelines: list[TimelinePoint] = []`
- `gaps: list[GapHypothesis] = []`
- `generated_at: str`
- `status: Literal[draft, ready, failed]`

### 下游消费要求
- UI 地图页只消费 `status=ready`
- Zotero 集成不直接消费 ResearchMap，但可用 `paper_ids` 做 collection 推荐

## 3.7 ZoteroItemLink（系统论文与 Zotero 条目映射）

### 最低必备字段
- `link_id: str`
- `paper_id: str`
- `zotero_library_id: str`
- `zotero_item_key: str`
- `zotero_version: int | None = None`
- `collections: list[str] = []`
- `tags: list[str] = []`
- `attachment_keys: list[str] = []`
- `sync_state: Literal[pending, imported, synced, conflict, failed]`
- `last_synced_at: str | None = None`

### 下游消费要求
- UI 的 Zotero 状态展示只依赖该模型，不直接依赖 Zotero 原始响应
- 同步/回写逻辑必须通过此映射查找系统内 `paper_id`

---

## 4. Application 层统一接口契约

以下是推荐的 façade / use case 边界。接口名可调整，但职责边界必须稳定。

## 4.1 解析导入：PaperIngestionService

### 输入
- 文件路径、URL、或 Zotero 导入请求
- 解析策略、是否覆盖、可选 profile/context

### 输出
- `Paper + ArtifactRef[] + ImportReport`

### 责任
- 统一文献导入入口
- 负责 source normalization、附件落地、导入记录
- **不负责** 生成 KnowledgeCard 或 ResearchMap

## 4.2 知识卡生成：KnowledgeCardService

### 输入
- `paper_id`
- 可选分析 profile / prompt preset / overwrite 标志

### 输出
- `KnowledgeCard`

### 责任
- 消费已解析的 Paper/Artifact
- 生成单篇稳定结构化卡片
- 写入卡片仓储并产出质量报告
- **不负责** Zotero API 调用与 UI 展示

## 4.3 研究地图聚合：ResearchMapService

### 输入
- `paper_ids[]` 或查询条件
- 聚合模式：主题图、方法图、问题图、时间线、空白发现

### 输出
- `ResearchMap`

### 责任
- 只消费 KnowledgeCard，不回头消费原始 Markdown
- 保证关系可追溯和可解释
- 联调样例、退化行为与 UI/Zotero 消费说明见 `docs/RESEARCH_MAP_CONSUMER_CONTRACT.md`
- 查询 DTO、过滤/分页/排序语义与导出接口草案见 `docs/RESEARCH_MAP_QUERY_CONTRACT.md`

## 4.4 Zotero 导入与同步：ZoteroIntegrationService

### 输入
- Zotero library/collection/item 范围
- 导入模式：首次导入 / 增量同步 / 回写预演

### 输出
- `ImportBatchReport + ZoteroItemLink[] + Paper[]/Artifact[]`

### 责任
- 从 Zotero 原始对象映射到系统内部模型
- 管理同步状态、冲突和 checkpoint
- **不允许** 把 Zotero 原始 JSON 直接作为 domain 模型向下传

## 4.5 工作台查询：WorkspaceQueryService

### 输入
- 搜索条件、筛选条件、paper_id/map_id

### 输出
- UI-friendly DTO（列表、详情、统计）

### 责任
- 为 Streamlit/未来 API 提供读模型
- 负责把 domain 模型整形成展示视图
- **不反向写入** 分析流程

---

## 5. 各模块上下游契约

## 5.1 解析模块 → 知识卡模块

### 上游必须提供
- 可稳定定位的 `paper_id`
- 至少一个主附件 ArtifactRef（PDF 或 Markdown）
- 基础 metadata（title 可为空，但 paper_id/source_uri 不能为空）
- 导入/转换失败状态

### 下游不得假设
- 摘要一定存在
- 章节一定完整
- 作者、年份一定可信

### 交付判定
- 若仅能输出 Markdown，但不能形成 Paper + ArtifactRef，则不算完成解析契约

## 5.2 知识卡模块 → 研究地图模块

### 上游必须提供
- `status=ready` 的 KnowledgeCard
- 标准化 `method_tags/dataset_tags/application_tags`
- 至少一条 `summary/research_problem/method overview`
- evidence/quality/trace 三类信息

### 下游不得假设
- 所有标签都已标准词汇化
- 卡片质量分永远高于阈值

### 交付判定
- 若只输出自由文本报告，不输出稳定 KnowledgeCard，则不能接入研究地图

## 5.3 Zotero 模块 → 解析/知识卡模块

### 上游必须提供
- Zotero item 到 `Paper` 的映射结果
- 附件到 `ArtifactRef` 的映射结果
- `ZoteroItemLink`
- collection/tag/item key 等可追溯信息

### 下游不得假设
- Zotero 附件一定可下载
- Zotero metadata 一定优于 PDF 抽取元数据

### 交付判定
- 若只完成 Zotero API 打通，但不能生成 `Paper + ArtifactRef + ZoteroItemLink`，不算集成完成

## 5.4 知识卡/研究地图/Zotero 模块 → UI 模块

### 上游必须提供
- 稳定 DTO 或 query service
- 明确字段默认值，避免 UI 层到处判空
- 失败状态、处理中状态、空结果状态

### UI 不得直接做的事
- 直接解析 JSONL/CSV 文件
- 直接调用 LLMClient / Zotero client / DocumentConverter
- 直接从 session state 推导领域状态

---

## 6. Zotero 集成位置与字段映射边界

## 6.1 架构位置

- `infrastructure/zotero/`
  - `zotero_client.py`：原始 API 访问
  - `zotero_mapper.py`：Zotero -> Paper/Artifact/ZoteroItemLink 映射
  - `zotero_checkpoint_store.py`：同步游标/版本
- `application/zotero_integration_service.py`
  - 编排导入、增量同步、冲突处理
- `domain/`
  - 只保留 `ZoteroItemLink`、导入报告、同步状态等系统内部概念

## 6.2 字段映射规则

### 可以进入 domain 的 Zotero 信息
- item key / library id
- tags
- collections
- attachment keys
- version / sync state
- 标准化 bibliographic metadata（title, authors, year, doi）

### 不应直接泄漏到 domain 的信息
- Zotero 原始响应结构
- HTTP/SDK 响应对象
- Zotero 特有嵌套 JSON 细节（应在 mapper 内消化）

## 6.3 冲突处理原则

当 Zotero metadata 与 PDF/LLM 抽取结果冲突时：
- bibliographic truth（标题、作者、年份、DOI）优先保留来源级 provenance
- 研究性字段（problem/method/contribution/gap）只由 KnowledgeCard 生成，不由 Zotero 填充
- 任何冲突必须记录来源，不允许静默覆盖

---

## 7. 旧入口兼容策略与切断点

## 7.1 兼容原则

迁移期允许保留旧实现，但必须遵守：
- 旧实现只能存在于 adapter/legacy 兼容层
- 新代码只面向新 façade 和新模型编程
- 不允许“为了兼容”继续扩大对 `src/*` 的依赖面

## 7.2 明确切断的旧入口

以下旧入口应视为待移除对象，不得新增依赖：

- `core.smart_paper_core`
- `core.llm_wrapper`
- 任何通过 `sys.path.insert` 暴露出来的隐式入口
- UI 直接调用 `core.history_manager` / `core.profile_manager` 作为长期方案
- 直接读取 `saved_analyses/history.json/jsonl/csv` 作为长期查询接口

## 7.3 迁移切断顺序

### 切断点 1：入口统一
- 保留 `smartpaper.py`、`interfaces/cli/paper_cli.py`、`streamlit.app.py` 作为外部入口
- 但这些入口内部必须逐步改为只调用 application façade

### 切断点 2：存储统一
- 将 `HistoryManager` 的缓存/索引/导出职责拆到 repository + export service
- 切断 UI 和 multi-service 对物理文件格式的直接感知

### 切断点 3：知识卡统一
- 单篇分析的完成定义从“生成 Markdown”切到“生成 KnowledgeCard”
- Markdown 降级为派生展示物，而非主数据源

### 切断点 4：研究地图统一
- `MultiPaperService` 从直接拼 prompt 消费历史 JSON，迁移为消费 KnowledgeCard repository

### 切断点 5：Zotero 统一
- Zotero 不再直接与 UI 或旧历史文件耦合，只通过 `ZoteroIntegrationService` 进入系统

## 7.4 兼容期允许的临时做法

仅在迁移期、且需文档说明时允许：
- application 通过 adapter 调用 legacy `DocumentConverter`
- 读旧历史文件后转换为新 DTO 再返回
- 对旧 saved_analyses 做一次性导入脚本

不允许：
- 继续在新服务中直接引用 legacy 文件结构作为永久仓储接口
- 为兼容而复制多套 schema

---

## 8. 对 UI 的统一消费要求

## 8.1 UI 只允许消费三类对象
- façade/use case 返回结果
- query service DTO
- 明确版本化的 schema

## 8.2 UI 页面对应的数据来源

- 论文解析页：`PaperIngestionService` + `KnowledgeCardService`
- 论文库管理页：`WorkspaceQueryService.list_papers/list_cards`
- 对比分析页：`ResearchMapService` 或 comparison query
- 研究问题追问页：面向 `paper_id` 的 query + QA façade
- 研究映射页：`ResearchMapService` / relevance façade
- Zotero 页：`ZoteroIntegrationService` + `WorkspaceQueryService.list_zotero_links`

## 8.3 UI 需要的失败态/空态约定
- `not_started`
- `processing`
- `ready`
- `failed`
- `partial`

任何 application 输出给 UI 的对象都应能映射到以上状态之一。

---

## 9. 测试与验收建议（面向各模块收口）

## 9.1 最小测试集合

每个模块至少补齐以下之一：
- schema 校验测试
- mapper/adapter 单元测试
- repository/query service 的纯本地测试
- use case 的无外部依赖编排测试

## 9.2 禁止把以下能力设为最小闭环前提
- 在线 LLM 真调用
- 真实 Zotero 联网同步
- 外部 OCR / PDF 平台服务可用

## 9.3 推荐的阶段验收顺序
1. `pytest --collect-only` 无错误
2. 核心 schema/adapter 单元测试通过
3. 单篇导入 -> KnowledgeCard 闭环走通
4. 多篇 KnowledgeCard -> ResearchMap 闭环走通
5. Zotero 导入 -> Paper/Artifact/ZoteroLink 闭环走通
6. Streamlit 仅通过 façade/query service 消费新链路

---

## 10. 各角色交付时应对齐的最小清单

### 解析与知识抽取
- 输出 `Paper + ArtifactRef + KnowledgeCard`
- 明确原始解析结果到 KnowledgeCard 的映射
- 不把 Markdown 报告当唯一主产物

### 研究地图
- 只消费 `KnowledgeCard(status=ready)`
- 输出 `ResearchMap + entities + relations + evidence`
- 关系可追溯，不能只给自由文本总结

### Zotero 集成
- 输出 `Paper + ArtifactRef + ZoteroItemLink + SyncReport`
- 不泄漏 Zotero 原始 JSON 给 domain/UI

### 工作台 UI
- 只调用 façade/query service
- 不直接访问 legacy 文件或基础设施实现
- 页面状态能表达 processing/failed/partial

### 评审与质量
- 先看 collect-only
- 再看 schema 稳定性、兼容说明、闭环是否完整

---

## 11. 一句话版本的收口标准

**SmartPaper 本轮升级的“完成”不等于新建几个目录或新写几个模型，而是：在不新增 sys.path 注入和跨层耦合的前提下，使 Paper / KnowledgeCard / ResearchMap / ZoteroLink 形成稳定契约，并让 UI 通过 application façade 走通可收集、可测试、可追溯的闭环工作流。**

---

## 8. 解析/知识卡模块当前契约对齐说明（阶段补充）

### 8.1 统一导入入口

当前统一导入入口为：
- `application.literature_ingestion_service.LiteratureIngestionService.import_source()`

支持输入：
- 本地 PDF
- URL / arXiv URL
- 本地 Markdown / Text
- `zotero_item`
- `zotero_attachment`

所有来源都先归一化为：
- `NormalizedPaperSchema`

随后单篇结构化知识卡统一落到：
- `StructuredAnalysisData`

禁止下游按来源分别消费不同 dict 结构。

### 8.2 解析输出给下游的直接消费方式

#### 研究地图
研究地图仅应消费下列稳定字段：
- `paper_id`
- `metadata.title/authors/year/venue/keywords`
- `analysis.summary_one_sentence`
- `analysis.research_problem`
- `analysis.method.overview`
- `analysis.method_tags`
- `analysis.dataset_tags`
- `analysis.application_tags`
- `analysis.innovation_points`
- `analysis.limitations`
- `analysis.future_work`
- `citations`

不得直接解析原始 Markdown 报告正文作为主数据源。

#### UI / 工作台
UI 列表与详情页应优先消费：
- `metadata`：展示标题、作者、年份、venue
- `document.abstract`：摘要预览
- `analysis.*`：详情卡片与对比分析
- `quality_control.*`：质量提示/异常提示
- `trace.*`：模型与执行信息展示
- `attachments`：原文/附件下载与预览入口

#### Zotero 映射
Zotero 侧应优先消费：
- `source`
- `attachments`
- `import_context.zotero_item_key/zotero_library_id/collection_keys/tags`
- `metadata.title/authors/year/doi`

不得在 UI 层重新拼装 Zotero 原始 payload 才能理解论文对象。

### 8.3 缺字段降级策略

当出现以下情况时，必须输出完整结构化对象，而不是裸 dict：
- LLM 未返回合法 JSON
- schema 校验失败
- 缺摘要 / 缺作者 / 缺年份 / 缺引用

当前降级规则：
- 使用 `StructuredAnalysisData` 默认值补齐所有 block
- `analysis.summary_one_sentence` 可回填为分析正文前 300 字符
- `quality_control`、`trace`、`source`、`document`、`citations`、`attachments`、`import_context` 均保留结构

### 8.4 当前兼容策略与切断点

当前为保证 collect 和旧测试可收集，保留了以下兼容壳：
- `core.*` -> 转发到 `src.core.*` / 新 application 服务
- `utils.*` -> 提供最小兼容实现

这些兼容壳的目标是：
- 收敛旧导入路径漂移
- 不再扩大旧入口依赖面
- 为后续彻底迁移提供缓冲层

后续切断点：
- 新代码不得继续新增对 `core.smart_paper_core`、`core.llm_wrapper`、`utils.*` 兼容壳的业务依赖
- 新功能只允许面向 `application/*` 和 `domain/schemas.py` 契约开发
