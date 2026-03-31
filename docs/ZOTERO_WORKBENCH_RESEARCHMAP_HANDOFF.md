# Zotero → 工作台 / 研究地图字段消费对接说明

> 目标：明确 Zotero 导入后的稳定字段如何被工作台 UI 与研究地图消费，避免 UI/研究地图直接解析 Zotero 原始 payload。  
> 复审入口：`docs/FINAL_REVIEW_BOARD.md`、`docs/ZOTERO_FINAL_REVIEW_SUBMISSION.md`

---

## 1. 适用范围

本说明面向两类消费方：

1. **工作台 UI**
   - 文献库列表
   - Zotero 列表态 / 详情态
   - “可分析 / 待补附件 / 已关联分析结果”状态提示

2. **研究地图**
   - 主题聚类
   - 论文范围筛选
   - collection/tag 先验聚合
   - 通过 `paper_id` 回到知识卡或论文详情

> 约束：UI 与研究地图都**不应**直接消费 Zotero 原始 JSON；必须基于 `LibraryPaperRecord` / `library_context` / 统一 `paper_id` 等稳定字段。

---

## 2. 上游输出对象

Zotero 导入完成后，应用层输出统一记录：

- `LibraryPaperRecord`
- 或进一步落入：
  - `ImportContextSchema`
  - `LibraryContextSchema`
  - `StructuredAnalysisData`
  - `NormalizedPaperSchema`

其中本次对接重点字段为：

- `paper_id`
- `collections`
- `tags`
- `analysis_refs`
- `library_context`

---

## 3. 字段消费总表

| 字段 | 上游位置 | 工作台消费方式 | 研究地图消费方式 | 备注 |
|---|---|---|---|---|
| `paper_id` | `LibraryPaperRecord.paper_id` / `StructuredAnalysisData.paper_id` | 作为稳定主键、选中项、跳转项 | 作为实体/关系 evidence 的主键 | 不使用 Zotero item key 替代 |
| `collections` | `LibraryPaperRecord.collections[]` | 文献库分组、筛选、展示 collection path | 作为 topic / scope 聚类先验 | 推荐消费 `path` 而非只消费 `key` |
| `tags` | `LibraryPaperRecord.tags[]` | 列表标签、筛选 chips、导入状态说明 | 作为 topic / method / application 辅助标签 | 推荐消费 `name` |
| `analysis_refs` | `LibraryPaperRecord.analysis_refs` / `library_context.analysis_refs` | 判断“已分析/待分析”状态，跳转分析结果 | 判断是否已有 ready knowledge card | 当前为结果反挂入口 |
| `library_context` | `StructuredAnalysisData.library_context` | 详情页 / Zotero 状态页统一读取 | 只取 `tags/collections/attachments/sync_state` 等稳定字段 | 不直接消费原始 Zotero payload |

---

## 4. 工作台消费说明

### 4.1 最小可消费字段

工作台若要接入 Zotero 列表态，至少消费：

```json
{
  "paper_id": "2c6f492be5aa18d9",
  "title": "Physics-Informed Biomedical Models",
  "year": 2025,
  "tags": ["PINN", "Biomedical"],
  "collections": ["Survey / PINN"],
  "analysis_refs": ["saved_analyses/analysis_001.md"],
  "has_primary_attachment": true,
  "sync_status": "pending"
}
```

### 4.2 建议 UI 字段映射

| UI 区域 | 推荐字段 | 说明 |
|---|---|---|
| 文献标题 | `title` | 主展示字段 |
| 年份 / 来源 | `metadata.year` / `metadata.journal` | 次级信息 |
| 标签 chips | `tags[].name` | 用于主题提示与筛选 |
| collection 面包屑 | `collections[].path` | 用于分组与定位 |
| 是否可分析 | `primary_attachment is not None` | 无附件时展示“待补附件” |
| 是否已分析 | `len(analysis_refs) > 0` | 有结果可跳转分析工作流 |
| 同步状态 | `library_context.sync_state.status` | 显示 pending/synced/conflict 等 |

### 4.3 UI 推荐行为

#### A. 文献库列表态

- 主键：`paper_id`
- 筛选：
  - 年份
  - tags
  - collection path
  - 是否已有 `analysis_refs`
- 状态提示：
  - `primary_attachment` 存在 → “可分析”
  - `primary_attachment` 不存在 → “仅元数据 / 待补附件”
  - `analysis_refs` 非空 → “已关联分析结果”

#### B. Zotero 详情态

推荐分 3 个区块：

1. **书目信息**
   - title / authors / year / doi / url
2. **库绑定信息**
   - library id / item key / version / sync status
3. **消费入口**
   - 打开分析结果（若 `analysis_refs` 非空）
   - 发起 PDF 解析（若 `primary_attachment` 存在）
   - 跳到研究地图（使用 `paper_id`）

---

## 5. 研究地图消费说明

### 5.1 研究地图可直接消费的 Zotero 衍生字段

研究地图不直接消费 Zotero bibliographic 原始字段，而是消费下列稳定字段：

- `paper_id`
- `metadata.keywords`
- `tags[].name`
- `collections[].path`
- `analysis_refs`

### 5.2 推荐映射方式

| 研究地图维度 | 推荐输入字段 | 说明 |
|---|---|---|
| 主题聚类 | `metadata.keywords + tags[].name + collections[].path` | 作为 topic 候选集合 |
| 论文范围筛选 | `paper_id` | 作为 map scope / query scope |
| 已有知识卡判定 | `analysis_refs` | 非空时可进一步取 ready card |
| Zotero 来源标记 | `library_context.zotero.item_key` | 仅用于 provenance，不参与主题建模 |
| 同步状态可视化 | `library_context.sync_state.status` | 作为边栏状态，不进入图谱主实体 |

### 5.3 研究地图侧边界

#### 可以直接使用

- `paper_id`
- `keywords`
- `tags`
- `collections.path`

#### 不建议直接使用

- `zotero_link.version`
- `library_id`
- `item_key`
- `raw_item`

这些字段属于外部系统绑定信息，不应成为研究语义节点。

---

## 6. `library_context` 消费说明

### 6.1 结构

`library_context` 当前固定包含：

```json
{
  "zotero": {
    "library_id": "7",
    "library_type": "user",
    "item_key": "ITEM1",
    "version": 21
  },
  "tags": [
    {"name": "PINN", "tag_type": "manual"},
    {"name": "Biomedical", "tag_type": "automatic"}
  ],
  "collections": [
    {"key": "C2", "name": "PINN", "path": "Survey / PINN", "parent_key": "C1"}
  ],
  "attachments": [
    {"key": "ATT1", "local_path": "paper.pdf", "is_primary": true}
  ],
  "sync_state": {
    "provider": "zotero",
    "status": "pending",
    "direction": "import_only",
    "remote_version": 21
  },
  "analysis_refs": ["saved_analyses/analysis_001.md"]
}
```

### 6.2 UI 消费建议

- UI Zotero 页面：可完整消费 `library_context`
- UI 文献库列表：只取轻量字段：
  - `tags`
  - `collections`
  - `sync_state.status`
  - `analysis_refs`

### 6.3 研究地图消费建议

- 研究地图只取：
  - `tags`
  - `collections`
  - `analysis_refs`
- 不把 `zotero.item_key/library_id/version` 变成图谱实体

---

## 7. 最小示例数据

完整示例见：

- `examples/zotero_workbench_researchmap_minimal.json`

建议工作台/UI 先消费该示例中的：

- `zotero_records[]`

建议研究地图先消费该示例中的：

- `research_map_seed_cards[]`

---

## 8. 推荐接入顺序

### 第一步：工作台列表态接入

目标：

- 在 UI 中先显示 Zotero 导入结果
- 不要求先打通真实同步

最小字段：

- `paper_id`
- `title`
- `metadata.year`
- `tags[].name`
- `collections[].path`
- `analysis_refs`
- `primary_attachment`
- `sync_state.status`

### 第二步：分析工作流接入

目标：

- 允许从 Zotero 记录直接发起分析

触发条件：

- `primary_attachment.local_path` 非空

动作：

- 调用现有 `PaperAnalysisService.analyze_file(...)`
- 分析完成后反挂 `analysis_refs`

### 第三步：研究地图接入

目标：

- 让研究地图基于 Zotero 导入记录已有字段获得初步聚类能力

推荐输入：

- `paper_id`
- `keywords`
- `tags`
- `collections.path`

进一步增强：

- 若 `analysis_refs` 存在，再读取 ready knowledge card 构建正式研究地图

### 第四步：真实同步 / 回写

目标：

- 最后再接 `sync/backfill/export`

原因：

- 不让同步能力阻塞 UI 展示与研究地图联调
- 先建立可消费字段闭环，再接入真实外部系统

---

## 9. 边界与兼容说明

### 重复导入

- UI 不应直接自行 dedupe
- 应信任上游 `dedupe_keys + dedupe_fingerprint`
- 若存在多个疑似重复项，UI 可提示“待合并”，但合并决策应留在 application/storage

### 无附件条目

- UI 允许展示
- 研究地图可把它作为 bibliographic 范围项
- 但不应直接进入 PDF 解析入口

### collection 嵌套不完整

- 消费 `collections[].path`
- 若 path 中含 `MISSING_PARENT / ...` 也应允许展示
- 不应因父 collection 缺失导致整条记录丢弃

---

## 10. QA 复核建议

QA 可直接使用：

```bash
python -m examples.zotero_offline_verify
```

然后对照：

- `examples/zotero_workbench_researchmap_minimal.json`
- `docs/ZOTERO_FINAL_REVIEW_SUBMISSION.md`
- 本文档

重点核验：

1. `paper_id` 是否贯穿 UI / 研究地图
2. `collections/tags/analysis_refs/library_context` 是否足够支撑消费
3. 无附件 / 重复导入 / collection 嵌套缺失是否有明确兼容边界
