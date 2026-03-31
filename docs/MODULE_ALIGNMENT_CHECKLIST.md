# SmartPaper 模块实施对齐清单与迁移落地建议

> 用途：供解析/知识卡、研究地图、Zotero、UI 四个执行模块在最终交付前进行自查。
> 依据：`docs/INTEGRATION_CONTRACTS.md`
> 使用方式：每个模块提交前，逐项确认“依赖的稳定接口 / 禁止旧入口 / 必补字段 / 兼容策略 / 收口顺序 / 最小验证”。

---

# 0. 所有模块共享的前置红线

在进入模块清单前，四个模块都必须满足：

## 0.1 第一门槛
- `python -m pytest --collect-only -q tests` 不得新增错误
- 不新增 `sys.path.insert(...)`
- 不新增跨层直接耦合
- 不继续依赖已删除或待删除旧入口

## 0.2 统一驳回条件
出现任一项，可直接驳回：
- 新代码继续依赖 `core.smart_paper_core`
- 新代码继续依赖 `core.llm_wrapper`
- 继续把 `saved_analyses/*.json/jsonl/csv/history.json` 当长期系统接口
- 在 UI / application 中直接拼 Zotero、LLM、DocumentConverter 细节
- 结构化字段只定义不落地
- 没有最小验证步骤

## 0.3 统一验收维度
每个模块都要显式回答这 5 个问题：
1. 接口一致性：我是否只依赖稳定入口？
2. 数据模型完整性：我的字段是否能被下游稳定消费？
3. 回归兼容策略：旧入口保留还是切断？切断点是否写清？
4. 可测试性：collect-only、schema、adapter、纯单测是否可过？
5. 工作流闭环：我的输出是否真正进入了下一环？

---

# 1. 解析 / 知识卡模块清单

## 1.1 该模块应依赖的稳定接口

应优先依赖：
- `PaperIngestionService`（统一导入入口）
- `KnowledgeCardService`（统一知识卡生成入口）
- 稳定 schema：`Paper`、`ArtifactRef`、`KnowledgeCard`
- 解析适配层（如 legacy `DocumentConverter` adapter）
- repository / storage port（而不是文件格式细节）

允许迁移期暂时复用：
- legacy `DocumentConverter`，但必须通过 adapter 包装
- 旧历史结果导入器，但只能作为一次性迁移脚本或兼容层

## 1.2 禁止继续依赖的旧入口

禁止新增依赖：
- `core.smart_paper_core`
- 旧 CLI prompt 入口作为解析主编排核心
- `core.history_manager` 作为知识卡正式仓储接口
- `streamlit.app.py` 中直接拼接的 process 流程作为长期入口
- 任何通过 `sys.path` 暴露的旧解析工具

## 1.3 必须补齐的数据字段

### A. Paper 最低字段
- `paper_id`
- `source_type`
- `source_uri`
- `title`
- `authors`
- `year`
- `venue`
- `abstract`
- `doi`
- `keywords`
- `artifacts`
- `provenance`

### B. ArtifactRef 最低字段
- `artifact_id`
- `paper_id`
- `artifact_type`
- `uri`
- `mime_type`
- `role`

### C. KnowledgeCard 最低字段
- `card_id`
- `paper_id`
- `version`
- `metadata`
- `document`
- `analysis`
- `evidence`
- `quality`
- `trace`
- `status`

### D. 知识卡 analysis 必补字段
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

## 1.4 兼容策略要求

必须说明：
- 当前是否仍支持“仅 Markdown 报告输出”
- 若支持，它是兼容产物还是主产物
- 与旧 `HistoryManager` 的关系：
  - 只读兼容？
  - 迁移导入？
  - 何时切断？
- 当 LLM 结构化失败时，是否仍返回完整默认对象
- 当 PDF 元数据缺失时，是否能降级为最小 `Paper + KnowledgeCard(draft/failed)`

### 推荐兼容策略
- 短期：保留 Markdown 输出，但降级为派生展示物
- 中期：以 `KnowledgeCard` 为完成定义
- 长期：切断“只有 Markdown 没有知识卡”的流程

## 1.5 建议收口顺序
1. 先统一导入入口（file/url/zotero/import）
2. 再统一 `Paper + ArtifactRef` 产物
3. 再统一 `KnowledgeCard` 完整字段
4. 再补齐失败/降级对象
5. 最后迁移旧 Markdown/历史缓存兼容

## 1.6 提交前最小自查
- [ ] collect-only 无新增错误
- [ ] 最小输入可实例化完整 schema
- [ ] 缺摘要/缺年份/缺作者场景有默认值或降级对象
- [ ] 不再把 Markdown 当唯一主产物
- [ ] 输出可直接被研究地图/UI/Zotero 消费

---

# 2. 研究地图模块清单

## 2.1 该模块应依赖的稳定接口

应优先依赖：
- `ResearchMapService`
- `KnowledgeCardRepository` / card query port
- 稳定 schema：`KnowledgeCard`、`ResearchEntity`、`ResearchRelation`、`ResearchMap`
- comparison / timeline / gap 用例层接口

## 2.2 禁止继续依赖的旧入口

禁止新增依赖：
- 原始 Markdown 报告文本作为主输入
- `MultiPaperService` 直接读取旧历史 JSON 文件的模式（可迁移，不可扩散）
- prompt 临时输出中的非稳定字段
- UI 页面状态里的选中列表作为长期领域输入格式

## 2.3 必须补齐的数据字段

### A. 研究地图节点字段
- `entity_id`
- `entity_type`
- `name`
- `aliases`
- `description`
- `evidence_paper_ids`
- `attributes`

### B. 研究地图关系字段
- `relation_id`
- `source_entity_id`
- `target_entity_id`
- `relation_type`
- `paper_ids`
- `weight`
- `evidence`

### C. ResearchMap 最低字段
- `map_id`
- `scope`
- `paper_ids`
- `entities`
- `relations`
- `timelines`
- `gaps`
- `generated_at`
- `status`

### D. 消费 KnowledgeCard 时至少依赖的上游字段
- `paper_id`
- `summary_one_sentence`
- `research_problem`
- `method.overview`
- `innovation_points`
- `limitations`
- `method_tags`
- `dataset_tags`
- `application_tags`
- `year`
- `evidence`

## 2.4 兼容策略要求

必须说明：
- 当前是否仍允许从旧 structured_data/history 导入研究地图输入
- 若允许，是否已做 DTO 归一化，而不是直接读取旧格式
- 缺年份、缺标签、缺证据时的退化逻辑是什么
- map status 如何区分 `draft/ready/failed`

### 推荐兼容策略
- 短期：允许“旧 structured_data -> KnowledgeCard DTO”适配后再聚合
- 中期：所有研究地图输入只接受 `KnowledgeCard(status=ready)`
- 长期：切断对旧历史 JSON/Markdown 的直接消费

## 2.5 建议收口顺序
1. 固化最小 `KnowledgeCard -> ResearchMap` 输入输出
2. 补齐 entity/relation/gap/timeline 结构
3. 做缺字段退化逻辑
4. 再迁移旧 `MultiPaperService` 到新 query/repository
5. 最后对接 UI 展示 DTO

## 2.6 提交前最小自查
- [ ] collect-only 无新增错误
- [ ] 不直接解析 Markdown 做研究地图主链路
- [ ] 2-3 张最小知识卡即可生成稳定地图结构
- [ ] 缺年份/缺证据可退化，不会崩溃
- [ ] 输出可被 UI 直接消费或导出

---

# 3. Zotero 模块清单

## 3.1 该模块应依赖的稳定接口

应优先依赖：
- `ZoteroIntegrationService`
- `zotero_client` + `zotero_mapper` + `checkpoint_store`
- 稳定 schema：`Paper`、`ArtifactRef`、`ZoteroItemLink`
- import/sync/report DTO

## 3.2 禁止继续依赖的旧入口

禁止新增依赖：
- 在 UI 页面事件中直接写 Zotero 解析逻辑
- 在 application 层直接操作 Zotero 原始 payload 字段
- 把 Zotero item 原始 JSON 直接下放到 domain/UI
- 用 `streamlit.session_state` 作为同步状态存储

## 3.3 必须补齐的数据字段

### A. ZoteroItemLink 最低字段
- `link_id`
- `paper_id`
- `zotero_library_id`
- `zotero_item_key`
- `zotero_version`
- `collections`
- `tags`
- `attachment_keys`
- `sync_state`
- `last_synced_at`

### B. Zotero 映射后必须能补齐的 Paper 字段
- `paper_id`
- `source_type=zotero`
- `source_uri`
- `title`
- `authors`
- `year`
- `doi`
- `keywords`

### C. Zotero 映射后必须能补齐的 ArtifactRef 字段
- `artifact_id`
- `paper_id`
- `artifact_type`
- `uri`
- `role`

## 3.4 兼容策略要求

必须说明：
- 重复导入如何去重
- 附件缺失如何降级
- tags / collections 缺失是否给默认空数组
- Zotero metadata 与 PDF metadata 冲突如何保留 provenance
- 是否预留 sync / backfill / export / 回写接口，而不是把策略写死在 UI

### 推荐兼容策略
- 短期：先完成 Zotero -> `Paper + ArtifactRef + ZoteroItemLink`
- 中期：支持增量同步与冲突标记
- 长期：再增加回写 note/tag/collection 建议，不直接耦合 UI

## 3.5 建议收口顺序
1. 先做 mapper 和 mock payload 单测
2. 再固化 `Paper/ArtifactRef/ZoteroItemLink` 输出
3. 再做导入报告与错误状态
4. 再接增量同步/checkpoint
5. 最后对接 UI 与知识卡联动

## 3.6 提交前最小自查
- [ ] collect-only 无新增错误
- [ ] 本地 mock payload 可完整映射 item/attachment/tag/collection
- [ ] 不把 Zotero 原始 JSON 暴露给 domain/UI
- [ ] 附件缺失/重复导入/字段缺损有兼容策略
- [ ] 输出可接解析链路或直接落 Paper 仓储

---

# 4. UI / 工作台模块清单

## 4.1 该模块应依赖的稳定接口

应优先依赖：
- `WorkspaceQueryService`
- `PaperIngestionService`
- `KnowledgeCardService`
- `ResearchMapService`
- `ZoteroIntegrationService`
- 明确版本化的 UI-friendly DTO

## 4.2 禁止继续依赖的旧入口

禁止新增依赖：
- `core.history_manager`
- `core.profile_manager` 作为长期页面核心编排器
- `DocumentConverter`、`LLMClient`、`zotero_client` 的直接页面调用
- 在单一 `streamlit.app.py` 中继续堆底层业务逻辑
- 页面直接读取 `saved_analyses/*.json/jsonl/csv`

## 4.3 必须补齐的数据字段/状态

### A. 页面最少状态
- `not_started`
- `processing`
- `ready`
- `failed`
- `partial`

### B. 论文库页面最少字段
- `paper_id`
- `title`
- `year`
- `venue`
- `status`
- `available_artifacts`

### C. 知识卡详情页最少字段
- `paper_id`
- `summary_one_sentence`
- `research_problem`
- `method.overview`
- `contributions`
- `limitations`
- `quality`
- `trace`

### D. 研究地图页最少字段
- `map_id`
- `entities`
- `relations`
- `timelines`
- `gaps`
- `status`

### E. Zotero 页最少字段
- `paper_id`
- `zotero_item_key`
- `collections`
- `tags`
- `sync_state`
- `last_synced_at`

## 4.4 兼容策略要求

必须说明：
- 当前页面是否仍暂时兼容旧历史记录展示
- 若兼容，旧记录是否已转换为新 DTO 再渲染
- 新工作流是否已能串起：论文解析 → 论文库 → 对比分析 → 研究映射 → Zotero
- 页面错误态、空态、处理中状态是否齐全

### 推荐兼容策略
- 短期：旧数据通过 query adapter 转成新 DTO 再展示
- 中期：页面只调用 façade/query service
- 长期：拆分 `streamlit.app.py`，按 workspace 组件化

## 4.5 建议收口顺序
1. 先切断页面对底层基础设施的直接调用
2. 再补 query service / façade
3. 再统一状态 DTO
4. 再把五个 workspace 串成闭环
5. 最后拆分单文件页面结构

## 4.6 提交前最小自查
- [ ] collect-only 无新增错误
- [ ] 关键页面函数可导入
- [ ] 至少 1 个无外部依赖 UI 状态测试/轻量集成验证
- [ ] 页面不再直接操作 LLM/Zotero/DocumentConverter
- [ ] 工作流状态完整：空态/错误态/处理中/完成态

---

# 5. 模块间推荐收口顺序

建议整体按以下顺序收口：

## 阶段 1：先清红线
1. 修复 pytest collect P0/P1 阻塞
2. 停止新增 `sys.path` 注入
3. 停止新增旧入口依赖

## 阶段 2：先固化上游稳定产物
1. 解析模块先产出稳定 `Paper + ArtifactRef`
2. 再产出完整 `KnowledgeCard`

## 阶段 3：再接中游聚合
1. 研究地图只消费 KnowledgeCard
2. Zotero 只映射到统一 Paper/ArtifactRef/ZoteroItemLink

## 阶段 4：最后收 UI
1. UI 改为只消费 façade/query service
2. 串起完整工作流闭环
3. 切断旧页面直连旧模块

---

# 6. 四个模块提交时可直接复制的简版自查模板

## 6.1 解析/知识卡
- 我依赖的稳定接口：
- 我已切断的旧入口：
- 我补齐的关键字段：
- 我的降级/兼容策略：
- 我的最小验证：
- 我的下游消费对象：

## 6.2 研究地图
- 我依赖的稳定接口：
- 我不再直接依赖的旧输入：
- 我补齐的结构：
- 我的退化逻辑：
- 我的最小验证：
- 我的 UI/导出消费对象：

## 6.3 Zotero
- 我依赖的稳定接口：
- 我不再扩散的旧/底层入口：
- 我补齐的映射字段：
- 我的重复导入/附件缺失/冲突策略：
- 我的最小验证：
- 我的下游消费对象：

## 6.4 UI
- 我依赖的 façade/query service：
- 我已切断的底层直连：
- 我补齐的状态/字段：
- 我的旧数据兼容展示策略：
- 我的最小验证：
- 我的工作流闭环范围：

---

# 7. 一句话执行标准

**四个模块在最终交付前，都必须完成“稳定接口收敛、旧入口止血、关键字段补齐、兼容策略写清、collect-only 可过、下游能消费”的自查；任何只完成局部结构定义、但无法进入下一环闭环的提交，都不算收口完成。**
