# Zotero 模块最终复审提交说明

> 提交日期：2026-03-31  
> 复审入口：`docs/FINAL_REVIEW_BOARD.md`  
> 关联实现：`domain/models.py`、`domain/schemas.py`、`infrastructure/zotero/*`、`application/zotero_integration_service.py`

---

## 1. 审查对象

- `domain/models.py`
- `domain/schemas.py`
- `infrastructure/zotero/client.py`
- `infrastructure/zotero/mapper.py`
- `application/zotero_integration_service.py`
- `docs/ZOTERO_INTEGRATION.md`
- `examples/zotero_mock_payload_basic.json`
- `examples/zotero_mock_payload_edge_cases.json`
- `examples/zotero_expected_mapping_excerpt.json`
- `examples/zotero_offline_verify.py`
- `examples/zotero_workbench_researchmap_minimal.json`
- `docs/ZOTERO_WORKBENCH_RESEARCHMAP_HANDOFF.md`
- `tests/test_zotero_mapping.py`

---

## 2. 快速结论

- **结论**：有条件通过
- **共同 P0 是否解除**：否
- **接口契约**：通过
- **数据模型闭环**：基本完整
- **兼容策略**：已明确
- **最小验证**：已提供，但仍受全仓 collect 阻塞影响，不能作为最终通过证据

### 当前不能直接转“通过”的原因

1. 仓库级 `python -m pytest --collect-only -q tests` 仍是 `30 collected / 10 errors`
2. `tests/test_zotero_mapping.py` 顶部仍存在 `sys.path.insert(...)`，命中最终复审红线
3. UI / 应用层尚未完成 Zotero 导入入口联调，因此工作流闭环仍停留在“文档+应用服务”级

---

## 3. Zotero 映射结果说明

### 3.1 item -> SmartPaper

Zotero 主条目映射为 `LibraryPaperRecord`，核心对象如下：

- `LibraryPaperRecord.paper_id`
  - 由 `doi / attachment_md5 / title_year_author / zotero_item_key` 组合生成指纹后截断
  - 用于后续与知识卡、研究地图统一关联
- `LibraryPaperRecord.metadata`
  - 使用 `PaperMetadata`
  - 包含 `title/authors/abstract/journal/year/doi/url/file_path/file_hash/keywords`
- `LibraryPaperRecord.zotero_link`
  - 使用 `ZoteroItemLink`
  - 保留 `library_id/library_type/item_key/version/uri/web_url`
- `LibraryPaperRecord.sync_state`
  - 使用 `SyncState`
  - 保留 `status/direction/remote_version/dedupe_fingerprint`

### 3.2 attachment -> SmartPaper

Zotero 子项 `itemType=attachment` 映射为 `ZoteroAttachment`：

- `key`
- `title`
- `content_type`
- `link_mode`
- `path`
- `url`
- `md5`
- `local_path`
- `parent_item_key`
- `is_primary`

其中：

- `contentType=application/pdf` 优先标记为主附件
- 若无显式 PDF 主附件，则降级将首个附件视为 `is_primary=True`
- `primary_attachment.local_path` 可作为现有 `PaperAnalysisService.analyze_file(...)` 的输入

### 3.3 tag -> SmartPaper

Zotero `tags[].tag` 映射为 `ZoteroTag.name`：

- `type=1` -> `tag_type="automatic"`
- 其余 -> `tag_type="manual"`
- 标签同时落入：
  - `LibraryPaperRecord.tags`
  - `PaperMetadata.keywords`
  - `metadata.extra["tags"]`

### 3.4 collection -> SmartPaper

Zotero `collections` 映射为 `ZoteroCollection`：

- `key`
- `name`
- `path`
- `parent_key`

其中 `path` 通过递归 `parentCollection` 展开，例如：

`Survey / PINN / Biomedical`

该路径可直接被：

- UI 文献库筛选
- 研究地图聚类先验
- 后续 Zotero collection 推荐/回写

---

## 4. 与统一 paper/card schema 的对齐

### 4.1 与统一导入 schema 的对齐

Zotero 导入结果与统一 schema 的对齐方式如下：

#### `PaperMetadata`

- 对齐统一论文主实体最小字段：
  - `title`
  - `authors`
  - `year`
  - `venue/journal`
  - `abstract`
  - `doi`
  - `keywords`

#### `ImportContextSchema`

已补强：

- `source_id`
- `parent_source_id`
- `zotero_item_key`
- `zotero_library_id`
- `collection_keys`
- `collection_paths`
- `tags`
- `attachment_keys`
- `analysis_refs`

#### `LibraryContextSchema`

已新增：

- `zotero`
- `tags`
- `collections`
- `attachments`
- `sync_state`
- `analysis_refs`

这使 Zotero 数据不再只停留在原始导入上下文，而能作为稳定外部文献库绑定信息被下游消费。

### 4.2 与知识卡 / 研究地图的对齐

对齐点：

- 统一主键：`paper_id`
- 主题/聚类先验：`keywords + tags + collection paths`
- 解析入口：`primary_attachment.local_path`
- 结果反挂：`analysis_refs`

当前边界：

- Zotero 模块**已完成映射与契约层对齐**
- 但**尚未在 UI 中落成导入按钮/列表态展示**
- 研究地图对 `library_context` 的直接消费仍需联调方补最后接线

---

## 5. 兼容策略与异常处理

### 5.1 重复导入

当前策略：

- 生成 `dedupe_keys`
  - `doi`
  - `attachment_md5`
  - `normalized_title`
  - `title_year_author`
  - `zotero_item_key`
  - `citation_key`
- 生成 `sync_state.dedupe_fingerprint`

用途：

- 重复导入检测
- 本地库对账
- 增量同步
- 冲突定位

当前限制：

- 已完成“去重依据定义”
- 但尚未完成“仓储层幂等 upsert / 合并策略”

### 5.2 字段缺失

当前处理：

- 缺作者：返回空列表
- 缺年份：返回 `None`
- 缺 DOI：不阻塞映射，退化使用标题/作者/条目 key 指纹
- 缺摘要/期刊：允许为空
- 缺 tags / collections：返回空列表

结论：

- Zotero 导入不会因为单字段缺失直接失败
- 仍能形成可消费的基础记录

### 5.3 附件缺失

当前处理：

- 允许无附件条目导入
- `primary_attachment` 为空时，不强行进入 PDF 解析链路
- 该记录仍可用于：
  - 文献库展示
  - Zotero 同步状态管理
  - 后续补附件/回填

### 5.4 collection 嵌套

当前处理：

- 递归解析 `parentCollection`
- 生成完整路径字符串
- 若父 collection 不完整，退化保留当前 key/name，不阻塞导入

---

## 6. sync / backfill / 回写预留

### 6.1 已预留接口

`BaseZoteroClient`：

- `list_items(since_version=...)`
- `list_collections()`
- `list_children(item_key)`
- `get_item_versions(...)`
- `upsert_item(...)`
- `create_note(...)`
- `update_tags(...)`

### 6.2 已预留应用层编排

`ZoteroIntegrationService`：

- `import_from_export(...)`
- `import_from_client(...)`
- `prepare_incremental_sync(...)`
- `attach_analysis_reference(...)`
- `prepare_writeback_payload(...)`

### 6.3 回写载荷内容

已统一输出：

- 目标 Zotero item 定位信息
- SmartPaper analysis note
- SmartPaper tags
- `analysis_refs`

这样未来实现真实 Zotero API client 时，不需要改 UI 或研究地图契约。

---

## 7. 与 UI / 研究地图的联调入口

### 7.1 UI 联调入口

建议由 UI 层通过 application façade 接入，不直接解析 Zotero payload：

1. UI 触发导入
2. 调用 `ZoteroIntegrationService.import_from_export(...)` 或 `import_from_client(...)`
3. 返回 `LibraryPaperRecord[]`
4. UI 只消费稳定字段：
   - `paper_id`
   - `title`
   - `metadata.year`
   - `tags`
   - `collections`
   - `sync_state.status`
   - `primary_attachment`

### 7.2 研究地图联调入口

建议消费：

- `paper_id`
- `metadata.keywords`
- `tags[].name`
- `collections[].path`
- `analysis_refs`

这样研究地图不需要理解 Zotero 原始 payload，只依赖稳定知识卡/文献记录字段。

---

## 8. 最小验证方式

### 已完成验证

离线单元测试：`tests/test_zotero_mapping.py`

覆盖：

1. item 映射
2. attachment 映射
3. tag 映射
4. collection 路径映射
5. `prepare_incremental_sync(...)`
6. `prepare_writeback_payload(...)`

### 验证结果

- `pytest -q tests/test_zotero_mapping.py`：通过
- `pytest -q tests/test_zotero_mapping.py tests/test_schemas.py tests/test_history_exports.py`：通过

### 当前不足

1. 测试文件仍含 `sys.path.insert(...)`
2. 全仓 `pytest --collect-only` 共同阻塞未解除
3. 尚无 UI 联调验证或研究地图消费验证

因此该最小验证只能证明：

- **Zotero 映射器与应用服务离线可工作**

尚不能证明：

- **整个仓库已达到最终复审“通过”状态**

---

## 9. 离线复审证据（新增）

### 9.1 本地 mock payload

已补充两组本地样例：

1. `examples/zotero_mock_payload_basic.json`
   - 覆盖正常主流程：
     - 1 个 item
     - 1 个 PDF attachment
     - 2 个 tag
     - 2 层 collection

2. `examples/zotero_mock_payload_edge_cases.json`
   - 覆盖边界场景：
     - 重复 DOI 的两个主条目
     - 无附件 metadata-only 条目
     - 父 collection 缺失的嵌套 collection

### 9.2 期望映射摘录

`examples/zotero_expected_mapping_excerpt.json` 提供 QA 复核时的字段锚点：

- `metadata.authors/doi/keywords/file_path`
- `zotero_link.item_key/library_id/version`
- `collections[].path`
- `attachments[].local_path/is_primary`
- `sync_state.remote_version/status/direction`

### 9.3 最小离线验证脚本

脚本：`examples/zotero_offline_verify.py`

运行方式：

```bash
python -m examples.zotero_offline_verify
```

该脚本不依赖在线 Zotero 服务，直接验证：

1. item/attachment/tag/collection 映射
2. 重复 DOI 的 dedupe key 一致
3. metadata-only 条目允许无附件
4. 父 collection 缺失时的退化路径行为

### 9.4 QA 最小核验步骤

建议 QA 在仓库根目录执行：

```bash
python -m examples.zotero_offline_verify
pytest -q tests/test_zotero_mapping.py
```

预期：

- 第一条命令输出 basic / edge 两段通过信息和关键 JSON 摘录
- 第二条命令离线通过

注意：

- 第二条测试命令当前仍受 `tests/test_zotero_mapping.py` 中 `sys.path.insert(...)` 影响，因此它只能作为“映射逻辑正确”的证据，不能作为“最终复审 fully pass”的证据

### 9.5 与统一 schema / 研究地图 / UI 的对齐证据

#### 与统一 schema 的对齐证据

QA 可对照以下字段链路：

- `record.paper_id` -> 统一主键
- `record.metadata.title/authors/year/doi/keywords` -> 统一 paper/card 基础字段
- `record.tags / record.collections / record.attachments / record.sync_state`
  -> `library_context`
- `record.primary_attachment.local_path`
  -> 解析链路入口

#### 与研究地图的对齐证据

从 mock payload 映射后即可稳定取得：

- `paper_id`
- `keywords`
- `tags[].name`
- `collections[].path`

这些字段可直接作为主题聚类、范围筛选和 collection 维度分组输入。

#### 与 UI 的对齐证据

从 mock payload 映射后即可稳定取得：

- `paper_id`
- `title`
- `metadata.year`
- `tags`
- `collections`
- `primary_attachment`
- `sync_state.status`

这些字段已足够支撑 Zotero 列表态、详情态和“可分析/待补附件”提示。

### 9.6 与工作台 / 研究地图的专门对接材料

已新增：

- `docs/ZOTERO_WORKBENCH_RESEARCHMAP_HANDOFF.md`
- `examples/zotero_workbench_researchmap_minimal.json`

内容覆盖：

1. `paper_id / collections / tags / analysis_refs / library_context` 的消费位置
2. UI 列表态 / 详情态推荐字段
3. 研究地图可直接消费的稳定字段
4. 推荐接入顺序
5. 最小示例数据

---

## 10. 补强建议

1. 移除 `tests/test_zotero_mapping.py` 中的 `sys.path.insert(...)`
2. 由 UI 同学接入 Zotero 导入列表态，补 1 个无外部依赖状态验证
3. 由研究地图同学补 `library_context` / `collection path` 消费说明或测试
4. 在存储层补幂等 upsert，真正落地重复导入策略
5. 待共同 P0 解除后，再进行 Zotero 最终“通过/驳回”裁决
