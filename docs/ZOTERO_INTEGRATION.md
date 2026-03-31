# Zotero 集成设计

本文档描述 SmartPaper 当前落地的 Zotero 集成边界，以及未来双向同步/回写的扩展方式。

## 本次已落地内容

- `domain.models`
  - `ZoteroItemLink`
  - `ZoteroAttachment`
  - `ZoteroTag`
  - `ZoteroCollection`
  - `SyncState`
  - `LibraryPaperRecord`
- `domain.schemas`
  - 在 `StructuredAnalysisData` / `NormalizedPaperSchema` 增加 `library_context`
  - 在 `ImportContextSchema` 增加 collection 路径、附件 key、analysis refs
- `infrastructure/zotero/mapper.py`
  - 将 Zotero 条目映射为 SmartPaper 统一记录
- `infrastructure/zotero/client.py`
  - 定义未来真实客户端的契约
- `application/zotero_integration_service.py`
  - 提供离线导入、增量同步游标生成、分析回写载荷生成

## 映射规则

### 条目

Zotero 主条目映射为 `LibraryPaperRecord`：

- `PaperMetadata` 承载论文核心元数据
- `ZoteroItemLink` 承载外部标识和版本
- `SyncState` 承载同步状态、方向和去重指纹

### 附件 PDF

子项 `itemType=attachment` 映射为 `ZoteroAttachment`：

- `contentType=application/pdf` 优先作为主附件
- `path/url/md5/linkMode` 全部保留
- `primary_attachment.local_path` 可直接复用现有 `PaperAnalysisService.analyze_file(...)`

### 标签

- `tags[].tag -> ZoteroTag.name`
- `type=1 -> automatic`
- 同步写入 `PaperMetadata.keywords`

### Collections

- 根据 `parentCollection` 递归展开层级路径
- 例如：`Survey / PINN / Biomedical`
- 可直接用于文献库筛选和研究地图聚合

## 去重策略

映射器会生成以下去重键：

- `doi`
- `attachment_md5`
- `normalized_title`
- `title_year_author`
- `zotero_item_key`
- `citation_key`

并进一步生成 `sync_state.dedupe_fingerprint`，供以下场景复用：

- Zotero 导入去重
- 本地知识库对账
- 增量同步
- 冲突检测

## 未来同步/回写接口

`BaseZoteroClient` 已预留：

- `list_items(since_version=...)`
- `list_collections()`
- `list_children(item_key)`
- `get_item_versions(...)`
- `upsert_item(...)`
- `create_note(...)`
- `update_tags(...)`

`ZoteroIntegrationService.prepare_writeback_payload(...)` 已统一未来回写载荷：

- 分析摘要 note
- SmartPaper 分析标签
- `analysis_refs`

## 推荐接入点

1. **工作台导入入口**
   - 在 Streamlit「论文库管理」中加入 Zotero 导入按钮
   - 导入后保存 `LibraryPaperRecord`

2. **解析链路**
   - 优先使用 `record.primary_attachment.local_path`
   - 复用现有 PDF 解析和分析服务

3. **分析结果关联**
   - 分析完成后调用 `attach_analysis_reference(...)`
   - 同步写入 `library_context.analysis_refs`

4. **研究地图**
   - 以 `collections`、`tags`、`keywords` 作为主题聚类先验
   - 与已有结构化分析卡统一使用 `paper_id`
