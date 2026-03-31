# Research Map 查询契约与检索接口草案

> 目标：在已有研究地图消费契约基础上，补一层面向 UI 图谱浏览、后续检索和导出的稳定查询契约。

---

## 1. 设计目标

该查询契约服务于三类消费方：

1. **UI 工作台**：图谱浏览、时间线浏览、空白列表、筛选器联动
2. **检索/导出**：主题/方法/问题/空白检索，JSON/CSV/Markdown 导出
3. **后续 API**：FastAPI 或其他接口层可直接复用 DTO

查询层只做**读模型**整形，不反向写入研究地图生成流程。

---

## 2. DTO 定义位置

查询 DTO 定义在：
- `domain/research_map_query.py`

关键对象：
- `ResearchMapQueryRequest`
- `ResearchMapQueryResponse`
- `ResearchMapExportRequest`
- `ResearchMapExportResponse`
- `ResearchMapQueryServiceDraft`

---

## 3. 查询请求语义

### 3.1 Scope

```json
{
  "scope": {
    "map_id": "rm:demo-001",
    "paper_ids": ["paper-1", "paper-2"],
    "source": "ready_cards"
  }
}
```

语义：
- `map_id`：已有研究地图快照 ID；为空时可按 `paper_ids` 动态查询
- `paper_ids`：把查询范围限制在指定论文集合
- `source`：
  - `ready_cards`：只读稳定知识卡
  - `legacy_structured_data`：兼容旧 structured_data
  - `mixed`：迁移期兼容视图

### 3.2 View

支持视图：
- `graph`：图谱浏览
- `timeline`：时间线
- `gaps`：研究空白
- `entities`：实体列表
- `relations`：关系列表
- `export`：导出预览/导出查询

### 3.3 Filters

统一过滤条件包括：
- 文本：`text_query`
- 类型：`entity_types` / `relation_types`
- 年份：`years`
- 主题/方法标签：`topic_labels` / `method_labels`
- 空白：`gap_types` / `priorities`
- 范围：`paper_ids`
- 阈值：`min_mentions` / `min_relation_weight`
- 图谱特殊项：`include_isolated_nodes`

#### 过滤行为说明
- 空数组表示“不限制”
- `years` 可包含 `unknown`
- `text_query` 为大小写不敏感模糊匹配
- 多个过滤条件默认 **AND** 组合
- 同一字段内多个值默认 **OR** 组合

---

## 4. 分页与排序语义

### 4.1 分页
- `page` 从 1 开始
- `page_size` 默认 20，上限 200
- `page_info.total` 表示总命中数
- `page_info.returned` 表示当前页返回数
- `page_info.has_next` 由服务端根据总数计算

### 4.2 排序

统一字段：
- `sort.sort_by`
- `sort.sort_order`

建议支持：

| 视图 | 默认排序 | 常用可选排序 |
|---|---|---|
| `entities` | `mentions desc` | `label asc`, `entity_type asc` |
| `relations` | `weight desc` | `relation_type asc` |
| `timeline` | `year asc` | `year desc` |
| `gaps` | `priority asc` | `title asc` |
| `graph` | 前端可复用 `entities` 的默认排序 | |

> `priority asc` 的建议语义：`high -> medium -> low`

---

## 5. 响应语义

查询响应统一为 `ResearchMapQueryResponse`：

- `scope`
- `view`
- `filters`
- `sort`
- `page_info`
- `items`
- `aggregations`

### 5.1 items

每个 `items[]` 元素统一包装为 `ResearchMapListItem`，包含：
- `item_type`
- `id`
- `title`
- `subtitle`
- `paper_ids`
- `sort_value`
- `payload`

这样 UI 可以：
- 用统一列表组件渲染不同视图
- 同时保留 `payload` 做详情展开
- 不必为 entity/relation/timeline/gap 各写一套完全不同的列表 DTO

### 5.2 aggregations

建议返回轻量 facet，用于 UI 筛选器：

```json
{
  "entity_type_counts": {"topic": 12, "method": 8},
  "year_counts": {"2023": 4, "2024": 7, "unknown": 1},
  "gap_type_counts": {"explicit_gap": 3, "missing_evaluation": 2}
}
```

---

## 6. 最小接口草案

推荐由 `WorkspaceQueryService` 或未来的 `ResearchMapQueryService` façade 暴露：

```python
list_entities(request: ResearchMapQueryRequest) -> ResearchMapQueryResponse
list_relations(request: ResearchMapQueryRequest) -> ResearchMapQueryResponse
list_timeline(request: ResearchMapQueryRequest) -> ResearchMapQueryResponse
list_gaps(request: ResearchMapQueryRequest) -> ResearchMapQueryResponse
export_map(request: ResearchMapExportRequest) -> ResearchMapExportResponse
```

### 边界要求
- **只读**：不触发地图重建、不调用 LLM、不写存储
- **稳定 DTO**：UI / API / 导出统一依赖同一套请求响应模型
- **兼容迁移**：若底层仍读取旧数据，也必须先转成新 DTO 再返回

---

## 7. 示例请求 / 响应

### 7.1 UI 图谱浏览请求

```json
{
  "scope": {
    "map_id": "rm:materials-demo",
    "paper_ids": [],
    "source": "ready_cards"
  },
  "view": "entities",
  "filters": {
    "text_query": "physics",
    "entity_types": ["topic", "method"],
    "relation_types": [],
    "years": ["2023", "2025"],
    "topic_labels": [],
    "method_labels": [],
    "gap_types": [],
    "priorities": [],
    "paper_ids": [],
    "include_isolated_nodes": false,
    "min_mentions": 1,
    "min_relation_weight": 0.0
  },
  "pagination": {
    "page": 1,
    "page_size": 20
  },
  "sort": {
    "sort_by": "mentions",
    "sort_order": "desc"
  },
  "include_fields": []
}
```

### 7.2 UI 图谱浏览响应

```json
{
  "scope": {
    "map_id": "rm:materials-demo",
    "paper_ids": [],
    "source": "ready_cards"
  },
  "view": "entities",
  "filters": {
    "text_query": "physics",
    "entity_types": ["topic", "method"],
    "relation_types": [],
    "years": ["2023", "2025"],
    "topic_labels": [],
    "method_labels": [],
    "gap_types": [],
    "priorities": [],
    "paper_ids": [],
    "include_isolated_nodes": false,
    "min_mentions": 1,
    "min_relation_weight": 0.0
  },
  "sort": {
    "sort_by": "mentions",
    "sort_order": "desc"
  },
  "page_info": {
    "page": 1,
    "page_size": 20,
    "total": 2,
    "returned": 2,
    "has_next": false
  },
  "items": [
    {
      "item_type": "entity",
      "id": "topic:physics-informed-ml",
      "title": "Physics-Informed ML",
      "subtitle": "topic · 2 papers",
      "paper_ids": ["paper-1", "paper-2"],
      "sort_value": "2",
      "payload": {
        "entity_type": "topic",
        "mentions": 2
      }
    }
  ],
  "aggregations": {
    "entity_type_counts": {
      "topic": 1,
      "method": 1
    },
    "year_counts": {
      "2023": 1,
      "2025": 1
    }
  }
}
```

### 7.3 导出请求

```json
{
  "query": {
    "scope": {"map_id": "rm:materials-demo", "paper_ids": [], "source": "ready_cards"},
    "view": "gaps",
    "filters": {
      "text_query": "",
      "entity_types": [],
      "relation_types": [],
      "years": [],
      "topic_labels": [],
      "method_labels": [],
      "gap_types": ["explicit_gap"],
      "priorities": ["high", "medium"],
      "paper_ids": [],
      "include_isolated_nodes": false,
      "min_mentions": 0,
      "min_relation_weight": 0.0
    },
    "pagination": {"page": 1, "page_size": 100},
    "sort": {"sort_by": "priority", "sort_order": "asc"},
    "include_fields": []
  },
  "export_format": "json",
  "flatten": false
}
```

---

## 8. UI / 导出消费建议

### UI
- 列表页：直接消费 `ResearchMapQueryResponse.items`
- facet 筛选器：消费 `aggregations`
- 分页器：消费 `page_info`
- 详情抽屉：消费 `items[].payload`

### 导出
- JSON：优先直接导出 `ResearchMapQueryResponse` 或 `ResearchMapExportResponse.content`
- CSV：建议在 `flatten=true` 时导出 `items[]` 展平记录
- Markdown：仅用于展示型导出，不作为主检索契约

---

## 9. 与现有研究地图消费契约的关系

- `docs/RESEARCH_MAP_CONSUMER_CONTRACT.md` 关注 **ResearchMap 生成输入/输出契约**
- 本文关注 **ResearchMap 查询/检索/导出契约**

二者组合后形成完整闭环：

`KnowledgeCard -> ResearchMap -> Query DTO -> UI / Export / Search`

---

## 10. 当前兼容策略与后续演进

### 当前
- 允许查询层从兼容 ResearchMap 结果构造 DTO
- 若底层仍来自 `HistoryManager` 或旧 structured_data，必须在 query adapter 层归一化

### 后续
- 中期：引入独立 `WorkspaceQueryService / ResearchMapQueryService`
- 中期：分页/排序语义在 API 层复用，不再散落在 UI
- 长期：以 repository / read model 直接支持查询，不再让 query 层关心旧历史文件
