# SmartPaper 工作台联调说明与页面闭环自查

> 适用范围：`streamlit.app.py` 当前落地的 Streamlit 工作台改造。
> 目标：供 QA、解析模块、研究地图模块、Zotero 模块在阶段收口时快速核对页面入口、状态流、稳定接口和闭环行为。

---

## 1. 模块结论（按统一验收口径）

- **接口一致性**：当前工作台主要依赖 `PaperAnalysisService`、`MultiPaperService`、`WorkbenchService` 与 `interfaces.web.workbench_state`，页面不再直接拼接 `HistoryManager` / `ProfileManager` 底层存储细节，也已移除 `streamlit.app.py` 顶部 `sys.path` 注入。
- **数据模型完整性**：页面消费的核心数据来自历史库增强后的 entry：`cache_key` / `title` / `year` / `venue` / `summary` / `structured_data` / `method_tags` / `dataset_tags` / `application_tags` / `reliability` / `audit_metrics`。
- **回归兼容策略**：为了兼容现有 `ask_question` / `calculate_relevance` 调用，`HistoryManager.get_analysis()` 已支持直接以 `cache_key` 读取历史记录；UI 则通过 `WorkbenchService` 获取稳定视图数据。
- **可测试性**：当前文档提供了页面级最小冒烟核对项；但仓库总体 `pytest --collect-only` 仍是全局 P0 阻塞，不能将“工作台可导入”视为全仓验收完成。
- **工作流闭环**：当前 UI 已形成“导入/解析 → 论文库 → 主论文/对比集选择 → 单篇追问/多篇对比/研究映射 → Zotero 批次记录”的可展示闭环；Zotero 实时同步仍为占位入口，待后端补齐。

---

## 2. 关键页面入口

工作台通过 `st.session_state.workspace` 在 5 个主页面间切换：

| 页面 key | 页面名称 | 入口函数 | 主要用途 |
|---|---|---|---|
| `overview` | 工作台总览 | `render_overview()` | 显示总量、近期论文、流程进度、快捷跳转 |
| `intake` | 导入与解析 | `render_import_workspace()` | 单篇解析、批量目录解析、Zotero 导入批次记录 |
| `library` | 论文库 | `render_library_workspace()` | 检索、筛选、查看卡片、选择主论文、加入对比 |
| `analysis` | 分析工作流 | `render_analysis_workspace()` | 单篇详情、追问、多篇对比、研究映射 |
| `zotero` | Zotero 集成 | `render_zotero_workspace()` | 展示连接配置与已记录批次 |

### 快捷跳转入口
- 侧边栏导航：`render_sidebar()`
- 总览页快捷按钮：
  - 去导入解析 → `goto_workspace("intake")`
  - 查看论文库 → `goto_workspace("library")`
  - 进入分析流 → `goto_workspace("analysis")`
  - 打开 Zotero → `goto_workspace("zotero")`
- 总览页近期论文：
  - 设为主论文 → 设置 `active_paper_key` 并跳转 `analysis`
  - 加入对比 → 追加到 `compare_keys`
- 论文库页卡片：
  - 设为主论文 → 设置 `active_paper_key`
  - 查看分析流 → 设置 `active_paper_key` 并跳转 `analysis`

---

## 3. 页面状态流（QA/联调核对重点）

### 3.1 顶层状态

`init_session_state()` 初始化以下统一状态：

| 状态 key | 类型 | 用途 |
|---|---|---|
| `session_id` | `str` | 当前会话解析输出命名 |
| `workspace` | `str` | 当前主页面 |
| `active_paper_key` | `Optional[str]` | 当前主论文 cache key |
| `compare_keys` | `List[str]` | 当前多篇对比集合 |
| `library_query` | `str` | 论文库搜索词 |
| `qa_messages` | `List[dict]` | 主论文追问对话历史 |
| `zotero_batches` | `List[dict]` | 已记录的 Zotero 导入批次 |
| `last_analysis_output` | `Optional[str]` | 最近一次单篇解析 Markdown 输出 |

### 3.2 统一工作流

1. **导入源进入工作台**
   - arXiv URL / 本地 PDF / 本地目录 / Zotero 导出文件
2. **解析与入库**
   - 单篇：`process_paper()` → `PaperAnalysisService.analyze_stream()` / `analyze_url_stream()`
   - 批量：`PaperAnalysisService.analyze_file()`
3. **历史库聚合**
   - `load_library_entries()` → `HistoryManager.list_history()` → `enrich_history_entry()`
4. **论文选择**
   - 单篇分析依赖 `active_paper_key`
   - 多篇对比依赖 `compare_keys`
5. **下游消费**
   - 单篇详情 / JSON 卡片 / 追问：`PaperAnalysisService.ask_question()`
   - 多篇对比：`MultiPaperService.compare_papers()` / `trace_evolution()` / `discover_gaps()`
   - 研究映射：UI 基于结构化 tags 聚合；主论文相关性调用 `PaperAnalysisService.calculate_relevance()`
   - Zotero：当前只记录导入批次与连接配置，不发起真实同步

---

## 4. 工作台依赖的稳定接口（当前联调契约）

### 4.1 解析与单篇分析

| 接口 | 位置 | UI 用途 | 说明 |
|---|---|---|---|
| `PaperAnalysisService.analyze_stream(file_path, role, task, domain)` | `application/paper_analysis_service.py` | 本地 PDF 单篇解析 | 流式输出 Markdown chunk |
| `PaperAnalysisService.analyze_url_stream(url, role, task, domain)` | 同上 | arXiv URL 单篇解析 | 流式输出 Markdown chunk |
| `PaperAnalysisService.analyze_file(file_path, role, task, domain, use_chain)` | 同上 | 目录批量解析 | 完整执行并入历史库 |
| `PaperAnalysisService.ask_question(paper_id, question)` | 同上 | 主论文追问 | 当前 UI 传入 `cache_key` |
| `PaperAnalysisService.calculate_relevance(paper_id)` | 同上 | 主论文与科研画像相关性评估 | 返回 JSON 结构 |

### 4.2 多篇分析

| 接口 | 位置 | UI 用途 |
|---|---|---|
| `MultiPaperService.compare_papers(cache_keys)` | `application/multi_paper_service.py` | 横向对比矩阵 |
| `MultiPaperService.trace_evolution(cache_keys)` | 同上 | 技术演化梳理 |
| `MultiPaperService.discover_gaps(cache_keys)` | 同上 | 研究空白发现 |

### 4.3 工作台 façade / 历史与知识卡聚合

| 接口 | 位置 | UI 用途 | 关键说明 |
|---|---|---|---|
| `WorkbenchService.list_library_entries()` | `application/workbench_service.py` | 论文库列表 / 视图数据 | 封装历史读取、结构化卡片聚合与默认值回退 |
| `HistoryManager.list_history()` | `src/core/history_manager.py` | façade 内部依赖 | 返回基础历史索引项 |
| `HistoryManager.get_analysis(source_hash, prompt_name=None)` | 同上 | 追问/相关性读取 | 已兼容直接传 `cache_key` |
| `HistoryManager.get_multiple_analyses(cache_keys)` | 同上 | 多篇对比 | 读取结构化 JSON 卡片 |
| `prompt_manager.get_available_options()` | `src/core/prompt_manager.py` | 侧边栏角色/领域/任务选项 | 供页面显示配置控件 |
| `WorkbenchService.get_profile()/update_profile()` | `application/workbench_service.py` | 科研画像编辑 | UI 通过 façade 访问画像配置 |

### 4.4 当前 UI 直接消费的数据字段

页面增强后的论文 entry 依赖以下字段，其他模块联调时请尽量保持：

```python
{
  "cache_key": str,
  "file_name": str,
  "file_path": str,
  "original_source": str,
  "prompt_name": str,
  "timestamp": float,
  "content": str,
  "structured_data": dict | None,
  "title": str,
  "year": str | int,
  "venue": str,
  "authors": list[str],
  "keywords": list[str],
  "summary": str,
  "method_tags": list[str],
  "dataset_tags": list[str],
  "application_tags": list[str],
  "innovation_points": list[str],
  "limitations": list[str],
  "reliability": float | None,
  "audit_metrics": dict,
}
```

优先来源：`structured_data.metadata / structured_data.analysis / structured_data.quality_control`。
若 `structured_data` 缺失，UI 使用默认值兜底。

---

## 5. 页面行为说明：空态 / 错误态 / 处理中 / 完成态

### 5.1 总览页 `render_overview()`
- **空态**：论文库为空时显示“请先前往导入与解析”
- **完成态**：显示论文总数、主论文数、对比集数量、Zotero 批次数
- **跳转闭环**：所有主页面均有快捷入口

### 5.2 导入与解析 `render_import_workspace()`

#### 单篇解析
- **空态**：未填 URL / 未上传 PDF → `st.warning`
- **处理中**：`st.spinner("正在解析论文...")` + 流式 `placeholder.markdown()`
- **错误态**：
  - URL 非法 → `process_paper()` 捕获并返回 error
  - 分析异常 → `st.error("解析失败...")`
- **完成态**：`st.success("解析完成，结果已写入论文库。")` + `last_analysis_output`

#### 批量目录
- **空态**：目录为空或不存在 → `st.warning("目录中未找到 PDF 文件。")`
- **处理中**：进度条 + 当前文件名状态提示
- **完成态**：成功提示处理篇数

#### Zotero 导入入口
- **空态**：允许无文件记录批次，但会保留空文件列表
- **完成态**：批次写入 `zotero_batches`
- **说明**：当前为占位入口，不触发真实 Zotero 后端请求

### 5.3 论文库 `render_library_workspace()`
- **空态**：无历史记录 → 提示先完成导入解析
- **筛选态**：支持搜索、年份、任务过滤
- **交互完成态**：
  - 加入/移除对比集
  - 设为主论文
  - 跳转到分析工作流
- **查看态**：
  - 卡片详情
  - 追溯与质量（含 `audit_metrics`）
  - Markdown / Structured JSON 结果查看

### 5.4 分析工作流 `render_analysis_workspace()`

#### 单篇工作台
- **空态**：未选择主论文 → 提示先去论文库选择
- **追问处理中**：`st.spinner("正在生成回答...")`
- **完成态**：展示问答历史

#### 跨论文对比
- **空态**：对比集少于 2 篇 → `st.warning`
- **处理中**：`st.spinner("正在生成综合报告...")`
- **完成态**：展示 Markdown 报告并支持下载

#### 研究映射
- **空态**：无主论文且无对比集且论文库为空 → `st.info("暂无可用于映射的论文。")`
- **降级策略**：
  - 优先使用 `compare_entries`
  - 否则使用 `[active_entry]`
  - 再否则使用 `entries[:10]`
- **相关性评估错误态**：`calculate_relevance()` 返回 error 时显示错误；若有 `raw_content` 一并展示
- **完成态**：展示 timeline / method / dataset / application 聚合结果与主论文相关性报告

### 5.5 Zotero 集成 `render_zotero_workspace()`
- **空态**：无批次 → 提示到导入页记录
- **占位态**：明确提示当前不会发起真实同步请求
- **完成态**：展示已记录批次、连接配置与映射勾选项

---

## 6. 与解析 / 研究地图 / Zotero 的联调闭环清单

### 6.1 解析模块联调清单

#### 目标
保证 UI 从输入到结构化历史记录的链路稳定。

#### 联调检查项
- [ ] `analyze_stream()` 与 `analyze_url_stream()` 能返回可连续渲染的文本 chunk
- [ ] 解析完成后历史库出现新记录（`HistoryManager.list_history()` 可见）
- [ ] 结构化 JSON 若存在，字段至少覆盖：
  - [ ] `metadata.title`
  - [ ] `metadata.year`
  - [ ] `analysis.summary_one_sentence`
  - [ ] `analysis.method_tags`
  - [ ] `analysis.dataset_tags`
  - [ ] `quality_control.overall_reliability`
- [ ] 若结构化失败，UI 仍可使用默认值显示论文卡，不应整页报错
- [ ] `ask_question(cache_key, question)` 与 `calculate_relevance(cache_key)` 能读取到对应历史记录

#### 当前已知切断点 / 风险
- UI 仍通过 `streamlit.app.py` 内部的 `process_paper()` 组织单篇流式解析，尚未完全收敛到单独 application façade
- 页面历史聚合已下沉到 `WorkbenchService`，但工作台仍需继续拆分以降低单文件复杂度

### 6.2 研究地图模块联调清单

#### 目标
保证结构化知识卡可被当前研究映射页直接消费。

#### 联调检查项
- [ ] `structured_data.analysis.method_tags` 可为空但必须存在为 list
- [ ] `structured_data.analysis.dataset_tags` 可为空但必须存在为 list
- [ ] `structured_data.analysis.application_tags` 可为空但必须存在为 list
- [ ] `structured_data.metadata.year` 缺失时 UI 会回退为“未知”
- [ ] 即使只有 1 篇论文，也可生成最小映射结果
- [ ] 主论文相关性接口 `calculate_relevance()` 返回结构：
  - [ ] `relevance_score`
  - [ ] `matching_points`
  - [ ] `gap_points`
  - [ ] `usage_suggestion`

#### 当前边界说明
- 研究映射页当前是 **UI 聚合版轻量映射**，使用 tags 和年份聚合，不依赖独立研究地图 service
- 若研究地图模块后续提供稳定 service，建议替换 `render_research_map_panel()` 内部聚合逻辑，而不是直接让页面解析 Markdown
- 研究地图结构化联调样例、退化行为与字段说明见 `docs/RESEARCH_MAP_CONSUMER_CONTRACT.md` 与 `examples/research_map_minimal_output.json`
- 图谱展示接入说明、节点/边视图模型与最小 graph DTO 样例见 `docs/RESEARCH_MAP_UI_GRAPH_CONTRACT.md` 与 `examples/research_map_graph_view_minimal.json`

### 6.3 Zotero 模块联调清单

#### 目标
保证 Zotero 后端接入后可无缝替换占位入口。

#### 当前 UI 已准备内容
- [ ] 连接配置表单：API Key / User or Group ID / 库类型 / 同步内容
- [ ] 导入入口：支持上传 JSON/CSV/RIS/BIB/TXT/ZIP 作为批次记录
- [ ] 批次状态面板：显示 `library` / `mapping_mode` / `files` / `status`

#### Zotero 后端接入时需满足
- [ ] 提供 application/infrastructure 层接口，不把 Zotero 解析逻辑直接写回页面事件
- [ ] 返回可映射到论文库 entry 或统一 card schema 的结果
- [ ] 对 `item / attachment / tag / collection` 提供稳定映射字段
- [ ] 支持“导入后自动进入论文库”的工作流延续
- [ ] 至少有失败态：认证失败 / payload 为空 / 附件缺失 / collection 缺失

#### 当前切断点
- `render_zotero_workspace()` 与导入页 Zotero tab **仅记录批次，不执行业务同步**
- 若需要联调真接口，建议新增 `ZoteroImportService` 一类稳定 façade，再由页面消费

---

## 7. QA 最小核对路径（建议按顺序）

### 路径 A：单篇解析闭环
1. 打开工作台总览
2. 跳转“导入与解析”
3. 输入 arXiv URL 或上传 PDF
4. 点击“开始解析并入库”
5. 确认出现处理中流式输出
6. 结束后跳到“论文库”核对新论文卡
7. 设为主论文并进入“分析工作流”
8. 查看 Markdown / JSON 卡片
9. 发起一次追问
10. 在研究映射页生成一次相关性评估

### 路径 B：多篇对比闭环
1. 论文库中勾选至少 2 篇论文进入对比集
2. 进入“分析工作流”→“跨论文对比”
3. 分别测试：横向对比矩阵 / 技术演化 / 研究空白
4. 确认报告可展示且可下载

### 路径 C：研究映射闭环
1. 选择主论文，或至少准备 2 篇对比论文
2. 进入“研究映射”页
3. 核对 timeline / method / dataset / application 聚合是否展示
4. 若已选主论文，点击生成相关性报告

### 路径 D：Zotero 占位闭环
1. 进入“导入与解析”→“Zotero 导入入口”
2. 录入一个批次
3. 进入“Zotero 集成”页
4. 确认该批次被展示
5. 核对页面清楚提示“当前不会发起真实同步请求”

---

## 8. 当前已知问题 / 风险 / 后续建议

### P0 / P1 之外的 UI 侧已知问题
1. **`streamlit.app.py` 仍偏大**：虽然状态与历史聚合已部分拆分，但页面仍需继续模块化。
2. **研究映射为 UI 轻聚合**：尚未切换到独立、可复用的地图 service。
3. **Zotero 为占位入口**：未形成真实导入→映射→入库闭环。
4. **collect 已转绿但需防回归**：当前全仓 collect 已通过，后续仍需防止旧入口/兼容壳回归。

### 建议的后续拆分方向
- 将 `streamlit.app.py` 拆为：
  - `interfaces/web/workbench_state.py`
  - `interfaces/web/workbench_data.py`
  - `interfaces/web/views/overview.py`
  - `interfaces/web/views/intake.py`
  - `interfaces/web/views/library.py`
  - `interfaces/web/views/analysis.py`
  - `interfaces/web/views/zotero.py`
- 将 `process_paper()` 下沉为独立 application façade
- 将研究映射聚合逻辑抽为稳定 service
- Zotero 接入新增 application façade，避免页面直接耦合

---

## 9. 提交/评审时可直接复用的快速结论

- **审查对象**：`streamlit.app.py` / `docs/WORKBENCH_INTEGRATION_CHECKLIST.md`
- **结论**：有条件通过
- **P0 阻塞**：本轮已验证 `python -m pytest --collect-only -q tests` 可 0 错误收集；后续仍需防止新增回归
- **契约检查**：基本通过；当前主要稳定依赖为 `PaperAnalysisService` / `MultiPaperService` / `WorkbenchService` / `interfaces.web.workbench_state`
- **数据模型闭环**：基本完整；Zotero 真正同步数据结构仍待后端落地
- **兼容策略**：已通过 `HistoryManager.get_analysis(cache_key)` 兼容现有追问/相关性流程
- **最小验证**：已提供页面级核对路径，并新增 `tests/test_workbench_ui_smoke.py` 进行离线 UI 状态 smoke test
- **补强建议**：
  1. 拆分 `streamlit.app.py`
  2. 继续拆分单文件页面
  3. 为 Zotero 与研究映射补独立 façade/service

