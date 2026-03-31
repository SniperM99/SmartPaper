# 最终复审看板（QA 维护）

> 更新时间：2026-03-31
> 用途：汇总各模块当前审查结论、共同阻塞、待验证文档与待交付模块，供最终轮复审直接使用。

---

## 1. 当前模块结论总览

| 模块 | 当前结论 | 关键依据 | 进入最终通过前的前置条件 |
|---|---|---|---|
| 架构契约 | 有条件通过 | `docs/INTEGRATION_CONTRACTS.md` 已定义统一验收口径、共享模型与边界；collect 阻塞已解除，但入口路径治理未完全收口 | 切断 `smartpaper.py` 的 `sys.path` 注入；将 compat 壳与迁移切断点收口为长期方案 |
| 解析 / 知识卡 | 有条件通过 | 统一导入链、fallback 契约与离线测试已补强，collect 阻塞已解除 | 将 `src.utils.section_splitter` 从 application 直连迁出/稳定化；明确 compat 壳保留期限 |
| 工作台 UI | 有条件通过 | `streamlit.app.py` 已移除 path hack，`WorkbenchService`/`workbench_state` 已提供 façade 与离线 smoke tests | 继续减少对 `src.core.*` 的直接依赖；等待与研究地图/Zotero 最终联调闭环 |
| 研究地图 | 有条件通过 | 生成契约、query DTO、消费契约与局部测试已补齐 | 清理 `tests/test_research_map.py` 的 path 注入；补齐到 UI 图谱展示的最终联调说明落地 |
| Zotero | 有条件通过 | 映射实现、同步预留、最终复审材料与离线测试已提交 | 清理 `tests/test_zotero_mapping.py` 的 path 注入；补齐到工作台/研究地图字段消费说明最终版 |

---

## 2. 共同阻塞（最高优先级）

### P0：`pytest --collect-only` 已恢复可收集

当前复核命令：

```bash
python -m pytest --collect-only -q tests
```

当前结果：
- `62 collected / 0 errors`
- 状态：**已解除**

#### 当前结论
- 历史 10 个 collect 错误已通过 compat 壳、tests/conftest.py 与可选依赖延迟导入治理解除。
- 最终轮复审不再把 collect 失败作为共同阻塞，但仍需警惕兼容层是否被长期固化。

#### P0 修复完成判定
- `python -m pytest --collect-only -q tests` 结果为 **0 errors**（当前已满足）
- 后续若新增模块/测试，不得重新引入 collect 错误

### P0：`sys.path` 注入仍未切断

当前命中位置：

- `smartpaper.py`
- `tests/test_research_map.py`（测试文件内）
- `tests/test_zotero_mapping.py`（测试文件内）

#### 说明
- 该问题同时命中“接口一致性”和“架构边界治理”红线。
- 在最终轮复审中，若上述 path hack 仍存在，则相关模块不能转为“通过”。

#### 解除标准
- 业务代码中不再新增/保留 `sys.path.insert(...)`
- 测试导入改为统一测试导入策略，而不是测试文件各自注入路径

---

### P1：可选依赖硬失败

当前命中：
- `tests/utils/test_download_mineru_models.py`
- `src/tools/everything_to_text/pdf_to_md_mineru.py`

问题：
- 模块顶层导入 `modelscope` / `magic_pdf`
- 未安装依赖时在 collect 阶段直接失败

解除标准：
- 改为延迟导入 / `pytest.importorskip` / 条件 skip
- 未安装可选依赖时 collect 不失败

---

## 3. 待验证文档清单

| 文档 | 状态 | 复审关注点 |
|---|---|---|
| `docs/INTEGRATION_CONTRACTS.md` | 已审 | 文档与实现是否闭环；compat 切断点是否落地 |
| `docs/MODULE_ALIGNMENT_CHECKLIST.md` | 待结合实现复核 | 是否真正被各模块收口采用 |
| `docs/WORKBENCH_INTEGRATION_CHECKLIST.md` | 已读，待结合 UI 修复复核 | 是否只是说明性文档，还是已对应代码整改 |
| 研究地图消费契约文档（任务中） | 待提交 | 最小输入输出样例、退化行为、UI/Zotero 消费说明 |
| Zotero 集成方案/映射文档 | 已提交，待结合共同 P0 复核 | `docs/ZOTERO_INTEGRATION.md`、`docs/ZOTERO_FINAL_REVIEW_SUBMISSION.md`、`docs/ZOTERO_WORKBENCH_RESEARCHMAP_HANDOFF.md`、`examples/zotero_mock_payload_basic.json`、`examples/zotero_mock_payload_edge_cases.json`、`examples/zotero_workbench_researchmap_minimal.json`、`examples/zotero_offline_verify.py` 是否与实现/测试一致，是否如实说明兼容边界 |

---

## 4. 待交付 / 待复审模块

### A. 正在补强中的模块

1. **解析 / 知识卡**
   - 待看：路径治理、字段降级测试、统一契约测试
   - 最终轮复审重点：
     - `PaperAnalysisService` path 注入是否移除
     - schema 校验失败是否仍下放裸 dict
     - 与研究地图 / UI / Zotero 的消费字段是否稳定

2. **工作台 UI**
   - 待看：去 path hack、ViewModel/ façade 下沉、UI 离线状态测试
   - 最终轮复审重点：
     - 不再直接读 `HistoryManager` 底层文件细节
     - Zotero 是否仍为纯占位
     - 页面空态/错误态/处理中/完成态是否有测试支撑

3. **架构**
   - 待看：路径治理与旧入口切断方案落地
   - 最终轮复审重点：
     - collect 阻塞是否实质下降
     - 是否仍存在旧入口漂移
     - 文档与实现是否一致

### B. 已完成但待下一轮复审的模块

4. **研究地图**
   - 当前结论：有条件通过
   - 待看：消费契约文档、退化行为说明、测试路径治理

### C. 尚未完成交付的模块

5. **Zotero**
   - 当前状态：已完成首轮提交，待最终轮复审
   - 最终轮复审重点：
     - item / attachment / tag / collection 映射模型
     - 统一 paper/card schema 对齐
     - sync/backfill/export 预留
     - 离线 mock 测试
     - `tests/test_zotero_mapping.py` path 注入是否切断

---

## 5. 最终轮复审入口检查单

在进入最终轮复审前，至少满足：

- [x] `python -m pytest --collect-only -q tests` 为 0 errors
- [ ] `sys.path.insert(...)` 从业务代码中切除
- [x] MinerU 可选依赖不再导致 collect 失败
- [ ] 解析 / UI / 架构补强任务已提交
- [ ] 研究地图消费契约文档已提交
- [ ] Zotero 模块已提交实现与最小验证

---

## 6. QA 最终结论输出模板（预留）

- 审查对象：
- 结论：通过 / 有条件通过 / 驳回
- 共同 P0 是否解除：是 / 否
- 接口契约：通过 / 不通过
- 数据模型闭环：完整 / 部分缺失
- 兼容策略：明确 / 不明确
- 最小验证：已提供 / 缺失
- 仍存阻塞：
- 补强建议：


---

## 7. UI 最终轮复审入口（针对已驳回项整改）

### 7.1 复审对象
- `streamlit.app.py`
- UI 拆分后的新模块（如有）
- `docs/WORKBENCH_INTEGRATION_CHECKLIST.md`
- 新增 UI 测试文件（如有）

### 7.2 必查整改项（来源于首轮驳回）
1. **path 注入是否切断**
   - `streamlit.app.py` 顶部不得再保留 `BASE_DIR/SRC_DIR -> sys.path.insert(...)`
   - 不接受以其他等价 path hack 替代
2. **底层读取是否下沉**
   - UI 不应继续直接读取 `HistoryManager.history_index`、`storage_dir`、`json_file_name` 等底层细节
   - 应改为消费 application façade / ViewModel / 稳定查询接口
3. **工作流闭环是否增强**
   - 导入 → 入库 → 主论文 → 对比 → 研究映射 → Zotero 的页面跳转与状态流仍需成立
   - Zotero 若仍为占位，必须明确切断点与提示文案
4. **最小验证是否补齐**
   - 至少补 1 组无外部依赖的 UI 状态测试或轻量集成验证
   - 至少覆盖：空库/未选择主论文/对比集不足/错误态 之一
5. **共同阻塞是否同时改善**
   - 全仓 `pytest --collect-only -q tests` 不能继续维持 10 errors

### 7.3 文档入口
- 主看板：`docs/FINAL_REVIEW_BOARD.md`
- UI 联调说明：`docs/WORKBENCH_INTEGRATION_CHECKLIST.md`
- 若有新文档：提交时需在 summary 中显式列出

### 7.4 阻塞核对项
- [ ] `streamlit.app.py` 不再出现 `sys.path.insert(...)`
- [ ] UI 不再直接访问 `HistoryManager` 底层文件/索引细节
- [ ] UI 新增测试可独立运行
- [ ] `python -m pytest --collect-only -q tests` 错误数下降至 0

### 7.5 预期结论模板
- 审查对象：UI 整改提交
- 结论：通过 / 有条件通过 / 驳回
- 驳回项是否全部关闭：是 / 否
- path 注入是否切断：是 / 否
- façade / ViewModel 是否到位：是 / 否
- UI 最小验证：已提供 / 缺失
- 共同 P0 是否解除：是 / 否
- 仍存问题：
- 补强建议：

---

## 8. 研究地图 query DTO 草案最终轮复审入口

### 8.1 复审对象
- 研究地图 query DTO/请求对象定义文件（待提交）
- `application/research_map_service.py`
- `domain/research_map.py`
- 研究地图消费契约文档（待提交）
- 新增 query DTO 测试（待提交）

### 8.2 必查检查点
1. **DTO 是否为稳定契约**
   - query DTO 必须是稳定结构，不得使用松散 dict 临时约定
   - 字段命名、默认值、可空性需明确
2. **输入边界是否清晰**
   - 至少说明支持哪些查询维度：paper_ids / topic / method / year range / gap only / limit / sort 等（以实际提交为准）
   - 缺省值与非法输入退化行为要明确
3. **服务消费方式是否合理**
   - `ResearchMapService` 应消费 DTO 或稳定 query 参数对象，而不是 UI 直接拼接自由字段
   - 不得回退为解析 Markdown 或依赖不稳定 prompt 文本
4. **与 UI / Zotero / 解析的消费契约是否闭环**
   - DTO 输出或查询结果需可被 UI 使用
   - 若与 Zotero 联动无关，应明确边界；若有关，应说明如何引用 `paper_id` 范围
5. **测试与路径治理**
   - 新增测试不得继续使用 `sys.path.insert(...)`
   - 局部测试可跑，且全仓 collect 错误数应下降而不是维持原状

### 8.3 文档入口
- 主看板：`docs/FINAL_REVIEW_BOARD.md`
- 研究地图消费契约文档（待提交）
- 若新增 DTO 设计文档：提交时需显式列出路径

### 8.4 阻塞核对项
- [ ] query DTO 字段定义完整且有默认/可空性说明
- [ ] `ResearchMapService` 已对齐 DTO 消费方式
- [ ] 新增测试不含 `sys.path.insert(...)`
- [ ] `python -m pytest --collect-only -q tests` 错误数下降至 0
- [ ] 与 UI 消费契约/样例已补齐

### 8.5 预期结论模板
- 审查对象：研究地图 query DTO 草案
- 结论：通过 / 有条件通过 / 驳回
- DTO 契约稳定性：通过 / 不通过
- 输入退化行为：明确 / 不明确
- 服务层接入：完成 / 未完成
- 测试与路径治理：通过 / 不通过
- 共同 P0 是否解除：是 / 否
- 仍存问题：
- 补强建议：

---

## 9. 解析模块补强结果最终轮复审入口

### 9.1 复审对象
- `application/literature_ingestion_service.py`
- `application/paper_analysis_service.py`
- `domain/schemas.py`
- 解析补强说明文档（待提交）
- 新增解析测试文件（待提交）

### 9.2 必查检查点
1. **共同 P0 是否解除**
   - 全仓 `python -m pytest --collect-only -q tests` 必须为 0 errors
2. **path 注入是否切断**
   - `application/paper_analysis_service.py` 不得再保留硬编码 `sys.path.insert(...)`
3. **统一导入链是否稳定**
   - `LiteratureIngestionService` 继续作为统一入口，且不回退为多源分叉输出
   - 需要明确 PDF / URL / arXiv / zotero_item / zotero_attachment / markdown/text 的退化行为
4. **结构化降级是否安全**
   - `StructuredAnalysisData` 校验失败时不得继续向下游下放裸 dict
   - 需提供标准降级对象、错误标记或安全回退策略
5. **下游消费字段是否闭环**
   - 研究地图 / UI / Zotero 所需字段是否稳定存在
   - 至少核对：`source` / `document` / `citations` / `attachments` / `import_context` / `metadata` / `analysis`
6. **最小验证是否补齐**
   - 至少补齐字段缺失降级、异常 citation / attachment、非法来源输入等离线测试
   - 新增测试不得继续使用 `sys.path.insert(...)`

### 9.3 文档入口
- 主看板：`docs/FINAL_REVIEW_BOARD.md`
- 解析补强说明文档（待提交）
- 集成契约：`docs/INTEGRATION_CONTRACTS.md`
- 模块对齐清单：`docs/MODULE_ALIGNMENT_CHECKLIST.md`

### 9.4 阻塞核对项
- [ ] 全仓 collect 为 0 errors
- [ ] `application/paper_analysis_service.py` path 注入已删除
- [ ] `StructuredAnalysisData` 失败回退不再是裸 dict
- [ ] 解析新增测试不含 path hack
- [ ] 下游消费字段契约测试已补齐

### 9.5 预期结论模板
- 审查对象：解析模块补强提交
- 结论：通过 / 有条件通过 / 驳回
- 共同 P0 是否解除：是 / 否
- path 注入是否切断：是 / 否
- 统一导入链稳定性：通过 / 不通过
- 结构化降级安全性：通过 / 不通过
- 下游字段闭环：完整 / 部分缺失
- 最小验证：已提供 / 缺失
- 仍存问题：
- 补强建议：

---

## 10. Zotero 最终轮复审入口（证据驱动）

### 10.1 复审对象
- Zotero 实现代码（待提交）
- Zotero 映射 / 同步预留文档（待提交）
- Zotero mock / fixture / 离线测试（待提交）
- 如有 UI 接入口：相关页面或应用服务文件（待提交）

### 10.2 必查检查点
1. **映射模型是否完整**
   - 是否覆盖 item / attachment / tag / collection
   - 是否存在稳定的系统内映射对象（如 link / import record / attachment ref）
2. **与统一 paper/card schema 是否对齐**
   - Zotero 导入后是否能映射到统一 `paper_id` / `source` / `attachments` / `import_context`
   - 不接受在 Zotero 路径上另起一套独立字段体系
3. **同步 / 回写预留是否明确**
   - 是否说明 sync/backfill/export/冲突处理边界
   - 是否避免把未来策略写死在 UI 或脚本中
4. **失败与重复导入策略是否明确**
   - 附件缺失、tag 缺失、collection 嵌套、重复导入、library/item key 冲突如何处理
5. **最小验证证据是否充分**
   - 至少应有离线 mock payload 或 fixture
   - 至少验证：无附件 Zotero item、带附件 item、tag/collection 映射、重复导入或冲突场景之一
6. **共同阻塞与路径治理**
   - 不得新增 `sys.path.insert(...)`
   - 不得让 Zotero 模块引入新的 collect 错误

### 10.3 复审证据占位（待提交后填写）
- 实现文件：
- 文档文件：
- 测试文件：
- Mock/fixture 位置：
- 本地验证命令：
- 关键样例：

### 10.4 阻塞核对项
- [ ] 全仓 collect 为 0 errors
- [ ] Zotero 不新增 path hack
- [ ] item / attachment / tag / collection 映射齐全
- [ ] 与统一 paper/card schema 对齐
- [ ] sync/backfill/export 预留已说明
- [ ] 离线 mock 测试已提供

### 10.5 预期结论模板
- 审查对象：Zotero 最终提交
- 结论：通过 / 有条件通过 / 驳回
- 共同 P0 是否解除：是 / 否
- 映射模型完整性：通过 / 不通过
- schema 对齐：通过 / 不通过
- 同步预留：明确 / 不明确
- 失败/冲突策略：明确 / 不明确
- 最小验证证据：充分 / 不足
- 仍存问题：
- 补强建议：
