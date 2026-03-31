# Research Map → Workbench 展示接入最终交叉检查意见

> 目标：基于研究地图生成契约、消费契约、查询契约与 UI 路径治理建议，对“研究地图接入工作台展示”做最终交叉检查。
> 适用对象：UI 工程师、研究地图工程师、QA。

---

# 1. 结论摘要

当前研究地图接入工作台展示，**架构方向可行，契约边界基本齐备，可进入联调，但仍属于“有条件可接入”而非“完全收口”状态**。

原因：
- 正向条件已具备：
  - 有生成侧结构：`ResearchMapService`
  - 有消费契约：`docs/RESEARCH_MAP_CONSUMER_CONTRACT.md`
  - 有查询 DTO：`domain/research_map_query.py`
  - 有查询契约：`docs/RESEARCH_MAP_QUERY_CONTRACT.md`
  - 有 UI 路径整改建议：`docs/UI_PATH_REMEDIATION_CHECKLIST.md`
- 限制条件仍存在：
  - UI 入口 `streamlit.app.py` 仍存在 `sys.path` 注入风险
  - 项目级 `pytest --collect-only -q tests` 的共同 P0 阻塞尚未解除
  - 研究地图当前部分接入仍保留对 legacy 数据来源的兼容路径

因此建议：
- **UI 可以开始按 query/consumer contract 接地图展示**
- **QA 不能据此判定整体正式通过**
- **研究地图与 UI 联调应以“契约联调 + 路径止血 + smoke test”三步推进**

---

# 2. 工作台接入研究地图的正确接口边界

## 2.1 生成边界

研究地图生成层应由 application 负责：
- `application.research_map_service.ResearchMapService`
- 或 `application.multi_paper_service` 中包装后的 map 构建入口

UI 不应承担：
- 从知识卡原始字段拼图谱
- 从 Markdown 报告临时提取 topic/method/problem
- 直接读取 `knowledge_base.jsonl` 生成视图模型

## 2.2 消费边界

UI 接入研究地图时，应只消费两类稳定对象：

### A. 地图主结构（生成态）
用于：
- 图谱概览
- timeline
- gap overview
- cluster summary

对应来源：
- `ResearchMapService.build_from_cards(...)`
- `MultiPaperService.build_research_map(...)`

### B. 查询 DTO（浏览态）
用于：
- 实体列表
- 关系列表
- 分页/排序/过滤
- 导出请求

对应来源：
- `domain/research_map_query.py`
- 未来 query service / workspace query façade

## 2.3 UI 不应直接碰的层

工作台禁止直接依赖：
- `saved_analyses/knowledge_base.jsonl`
- 旧 `structured_data` 物理文件结构
- `HistoryManager` 返回的原始历史记录作为图谱主契约
- Zotero 原始 JSON
- 任意 prompt 文本与 Markdown 片段

---

# 3. 视图模型交叉检查

# 3.1 图谱主视图（graph view）

## 推荐 UI 输入
优先使用：
- `ResearchMapQueryResponse(view="graph" or "entities"/"relations")`
- 或 `ResearchMapSchema.entities + relations`

## UI 应展示的节点类型
建议主图只渲染：
- `topic`
- `method`
- `problem`
- `gap`

建议弱化/可折叠：
- `paper`
- `dataset`
- `metric`

## UI 节点视图模型建议
每个节点至少需要：
- `id`
- `entity_type`
- `label/title`
- `paper_ids`
- `mentions`（若来自 query payload）
- `metadata`

## UI 边视图模型建议
每条边至少需要：
- `source`
- `target`
- `relation_type`
- `weight`
- `evidence_paper_ids`

## 风险检查
- 若 UI 直接消费 `ResearchMapSchema.entities/relations`，需要自己做分页/过滤
- 若 UI 需要浏览和筛选，优先走 query DTO，不应直接在页面里重造查询层

---

# 3.2 时间线视图（timeline view）

## 推荐 UI 输入
优先使用：
- `ResearchMapQueryResponse(view="timeline")`
- 或 `ResearchMapSchema.timeline`

## UI 最小字段
- `year`
- `paper_ids`
- `key_topics`
- `key_methods`
- `highlights`

## 退化行为检查
当前契约已允许：
- `year = "unknown"`

UI 必须支持：
- 将 unknown 年份渲染为“年份未知”
- 不因年份缺失丢弃整条 timeline

---

# 3.3 研究空白视图（gaps view）

## 推荐 UI 输入
优先使用：
- `ResearchMapQueryResponse(view="gaps")`
- 或 `ResearchMapSchema.gaps`

## UI 最小字段
- `id`
- `title`
- `description`
- `gap_type`
- `priority`
- `evidence_paper_ids`
- `related_entity_ids`

## 展示建议
- 默认按 `priority` 分组
- 再按 `gap_type` 分段
- 点击后可反查 `paper_ids` / 相关实体

## 风险检查
UI 不应自己根据 `limitations/future_work` 再计算 gap；gap 生成是研究地图侧职责。

---

# 3.4 列表浏览/检索视图（entities/relations/export）

## 推荐 UI 输入
必须优先使用：
- `ResearchMapQueryRequest`
- `ResearchMapQueryResponse`
- `ResearchMapExportRequest`
- `ResearchMapExportResponse`

## 核心价值
这层 DTO 已为 UI 提供：
- filters
- pagination
- sort
- aggregations
- 统一 `ResearchMapListItem`

因此 UI 不应再自己发明：
- entity list DTO
- relation list DTO
- timeline list DTO
- gap list DTO

## 风险检查
如果 UI 仍直接遍历 `entities` / `relations` 本体来实现分页排序，则说明查询契约没有真正接入。

---

# 4. 残留旧入口风险检查

## 4.1 UI 侧风险

### 风险 A：`streamlit.app.py` 仍有 `sys.path` 注入
影响：
- 研究地图在 UI 中的导入成功，不能证明真实边界成立
- QA 不能据此判定工作台已正式收口

### 风险 B：UI 仍直接依赖 legacy `core.*`
短期可接受，但前提是：
- 通过 compat 壳解析
- 不新增依赖面

### 风险 C：UI 若直接读旧历史文件来驱动地图
这会破坏 query/consumer contract，必须禁止。

## 4.2 研究地图侧风险

### 风险 A：输入仍可来自 legacy `structured_data`
短期可接受，但必须：
- 先转 DTO
- 再构图
- 不让 UI 感知 legacy 来源

### 风险 B：当前 query service 还是 draft
`domain/research_map_query.py` 目前提供 DTO 和 draft 接口描述，
这意味着：
- query contract 已明确
- 但 application/query façade 的真正实现仍需落地

### 风险 C：`ResearchMapService` 仍直接依赖 `src.core.history_manager`
从架构长期看，这属于未完全切断 legacy 的迹象。
短期可接受，长期应切到 repository/query 层。

## 4.3 QA 侧风险

QA 在复审时需区分：
- “研究地图模块契约可联调”
- “项目整体已正式通过”

前者可以成立，后者目前仍不能成立，因为共同 P0 阻塞还在。

---

# 5. 推荐接入顺序

建议 UI 与研究地图联调按下面顺序进行，而不是一次性把图谱全上页面。

## 阶段 1：先接静态 overview/gaps/timeline

优先接：
- `overview`
- `timeline`
- `gaps`

原因：
- 这些结构稳定
- 分页/交互复杂度低
- 更容易验证 consumer contract 是否正确

## 阶段 2：再接 graph 主视图

接入：
- `entities`
- `relations`

但建议：
- 初版先限制实体类型
- 不要一上来把所有 paper/dataset/metric 都画进去
- 先保证 topic/problem/method/gap 图能读懂

## 阶段 3：再接 query DTO 驱动的浏览/筛选

接入：
- filters
- pagination
- sort
- aggregations

这一步完成后，工作台上的研究地图才算真正从“静态展示”进入“可浏览查询”。

## 阶段 4：最后接导出与 Zotero 推荐联动

接入：
- `ExportRequest/Response`
- 研究地图结果驱动的 collection/tag/note 推荐

但注意：
- 这是派生能力，不应阻塞 UI 主图谱联调

---

# 6. 给 UI / 研究地图 / QA 的最终建议

# 6.1 给 UI 工程师

## 现在可以做
- 直接按 `RESEARCH_MAP_CONSUMER_CONTRACT` 接 `overview/timeline/gaps`
- 按 `RESEARCH_MAP_QUERY_CONTRACT` 规划 graph/list/filter UI
- 将研究地图页面视为 application/query 消费页，而不是数据拼装页

## 现在不要做
- 不要直接读 `knowledge_base.jsonl`
- 不要自己实现 gap 推断
- 不要依赖 `sys.path` 注入保持导入可用
- 不要跳过 query DTO 直接在页面手写分页/排序逻辑

## UI 最小验收建议
- 页面能渲染 `overview`
- 页面能渲染 `timeline(含 unknown 年份)`
- 页面能渲染 `gaps(priority + gap_type)`
- graph 页至少能展示 topic/method/problem/gap 节点和 relations

# 6.2 给研究地图工程师

## 现在可以做
- 继续保持生成契约、消费契约、查询契约三层一致
- 优先补真实 query service façade
- 保证 UI 永远不需要回退到原始地图本体做复杂筛选

## 现在不要做
- 不要新增对 legacy 文件结构的 UI 级暴露
- 不要让 query DTO 与生成 DTO 脱节
- 不要让 UI 感知“数据来自 ready_cards 还是 legacy_structured_data”之外的底层差异

## 研究地图最小验收建议
- `ResearchMapService.build_from_cards` 输出稳定
- `ResearchMapQueryRequest/Response` 对 graph/timeline/gaps/entities/relations/export 语义稳定
- 退化行为在契约测试中可验证

# 6.3 给 QA

## 复审时建议分两层判断

### A. 模块层通过条件（研究地图→工作台联调）
可判“通过/有条件通过”的依据：
- 文档契约齐备
- DTO 稳定
- 联调样例齐备
- query 契约测试通过
- UI 已按契约接入，不再解析 Markdown/旧文件

### B. 项目层正式通过条件
仍必须额外满足：
- `pytest --collect-only -q tests` 的 10 个错误清零
- `streamlit.app.py` 的 `sys.path` 注入已删除
- 相关正式入口 smoke test 成功

---

# 7. 最终交叉检查结论

**研究地图到工作台展示的接口边界现在已经足够明确：UI 应消费 ResearchMap 结构与 Query DTO，而不是 legacy 文件和 Markdown；研究地图应继续把生成、消费、查询三层契约保持一致；QA 可开始按“模块联调通过”标准审查这条链路，但在 `sys.path` 注入和 collect-only P0 阻塞解除前，仍不应把它视为项目级正式收口完成。**
