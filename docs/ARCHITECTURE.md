# SmartPaper 架构文档

## 四层架构设计

SmartPaper 采用清晰的分层架构，便于维护和扩展。

```
┌─────────────────────────────────────────────────────────┐
│                   接入层 (Interfaces)                    │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐           │
│  │    CLI    │  │  Web UI   │  │   API     │           │
│  │  (未来)   │  │(Streamlit)│  │(FastAPI)  │           │
│  └───────────┘  └───────────┘  └───────────┘           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                应用编排层 (Application)                   │
│  ┌────────────────────┐  ┌────────────────────┐        │
│  │ PaperAnalysisSvc   │  │ BatchAnalysisSvc   │        │
│  │ - 单篇分析流程      │  │ - 批量分析流程      │        │
│  │ - URL 分析流程      │  │ - 目录扫描          │        │
│  └────────────────────┘  └────────────────────┘        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                领域核心层 (Domain)                        │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│  │   Models   │ │ Analyzers  │ │ Extractors │          │
│  │ - Paper    │ │ - 分析策略  │ │ - 元数据    │          │
│  │ - Result   │ │ - 验证规则  │ │ - 内容提取  │          │
│  │ - Task     │ │            │ │            │          │
│  └────────────┘ └────────────┘ └────────────┘          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│               基础设施层 (Infrastructure)                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │   LLM   │ │  PDF    │ │ Storage │ │ Zotero  │      │
│  │ 客户端   │ │ 转换器   │ │ 管理器   │ │ 集成    │      │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │
└─────────────────────────────────────────────────────────┘
```

## 各层职责

### 1. 接入层 (Interfaces)

**职责：** 处理用户交互，调用应用服务

**模块：**
- `interfaces/cli/` - 命令行接口
- `interfaces/web/` - Web 界面 (Streamlit)
- `interfaces/api/` - REST API (未来 FastAPI)
- `interfaces/zotero/` - Zotero 插件 (未来)

**特点：**
- 薄接口层，不包含业务逻辑
- 只负责参数验证和结果展示
- 易于添加新的交互方式

### 2. 应用编排层 (Application)

**职责：** 编排业务流程，协调领域对象和基础设施

**模块：**
- `application/paper_analysis_service.py` - 单篇分析服务
- `application/batch_analysis_service.py` - 批量分析服务

**流程示例（单篇分析）：**
```python
1. 创建 AnalysisTask
2. 调用 PDFConverter 转换文档
3. 创建 PaperDocument 领域对象
4. 调用 LLMClient 进行分析
5. 创建 AnalysisResult
6. 保存结果到存储
7. 返回结果
```

**特点：**
- 包含应用特定的业务逻辑
- 协调多个基础设施组件
- 事务管理和错误处理

### 3. 领域核心层 (Domain)

**职责：** 定义核心业务对象和规则

**模块：**
- `domain/models.py` - 领域模型
  - `PaperDocument` - 论文文档
  - `PaperMetadata` - 论文元数据
  - `AnalysisResult` - 分析结果
  - `AnalysisTask` - 分析任务
  - `BatchTask` - 批量任务
- `domain/analyzers/` - 分析策略 (未来)
- `domain/extractors/` - 提取器 (未来)

**特点：**
- 纯业务逻辑，不依赖外部系统
- 高内聚，低耦合
- 可独立测试

### 4. 基础设施层 (Infrastructure)

**职责：** 与外部系统交互

**模块：**
- `infrastructure/llm/` - LLM API 封装
  - `llm_client.py` - LLM 客户端
- `infrastructure/pdf/` - PDF 处理
  - `pdf_converter.py` - PDF 转换器
- `infrastructure/storage/` - 存储管理 (未来)
- `infrastructure/zotero/` - Zotero 集成 (未来)
  - `client.py` - Zotero 客户端协议与导出加载器
  - `mapper.py` - Zotero 条目/附件/标签/collections 到统一文献记录的映射

**特点：**
- 实现具体技术细节
- 易于替换实现（如切换 LLM 提供商）
- 依赖注入到应用层

## 数据流示例

### 单篇论文分析流程

```
用户 (CLI)
  ↓
interfaces/cli/paper_cli.py
  ↓
application/PaperAnalysisService.analyze_file()
  ↓
infrastructure/pdf/PDFConverter.convert_file()
  ↓
domain/PaperDocument.create()
  ↓
infrastructure/llm/LLMClient.chat()
  ↓
domain/AnalysisResult.create()
  ↓
返回结果到 CLI
```

## 扩展性

### 添加新的 LLM 提供商

只需在 `infrastructure/llm/` 添加新客户端，修改配置即可。

### 添加新的分析策略

在 `domain/analyzers/` 创建新的分析器，应用层调用即可。

### 添加 Zotero 集成

已在 `infrastructure/zotero/` 建立映射器与客户端协议，应用层可通过 `application/zotero_integration_service.py` 调用。
后续只需补真实 Zotero API / 插件桥接实现，即可接入增量同步和回写。

### 添加 API 接口

在 `interfaces/api/` 创建 FastAPI 路由，调用应用服务。

## 目录结构

```
SmartPaper/
├── application/              # 应用编排层
│   ├── __init__.py
│   ├── paper_analysis_service.py
│   └── batch_analysis_service.py
├── domain/                   # 领域核心层
│   ├── __init__.py
│   ├── models.py
│   ├── analyzers/           # (未来)
│   └── extractors/          # (未来)
├── infrastructure/           # 基础设施层
│   ├── __init__.py
│   ├── llm/
│   │   ├── __init__.py
│   │   └── llm_client.py
│   ├── pdf/
│   │   ├── __init__.py
│   │   └── pdf_converter.py
│   ├── storage/             # (未来)
│   └── zotero/              # (未来)
├── interfaces/               # 接入层
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── paper_cli.py
│   ├── web/                 # (Streamlit)
│   └── api/                 # (未来 FastAPI)
├── src/                      # 旧代码 (保留兼容)
├── config/                   # 配置文件
├── outputs/                  # 输出目录
└── docs/                     # 文档
    └── ARCHITECTURE.md
```

## 迁移计划

### 阶段 1：创建新架构 ✅

- [x] 创建四层目录结构
- [x] 定义领域模型
- [x] 创建基础设施组件
- [x] 创建应用服务

### 阶段 2：迁移现有功能

- [ ] 迁移 CLI 工具到新架构
- [ ] 迁移 Streamlit UI
- [ ] 更新测试用例

### 阶段 3：添加新功能

- [ ] FastAPI 接口
- [ ] Zotero 集成
- [x] Zotero 导入映射与同步接口预留
- [ ] 向量数据库支持
- [ ] Agent 对话模式

---

*最后更新：2026-03-09*
