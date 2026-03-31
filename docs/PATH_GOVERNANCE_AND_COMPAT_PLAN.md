# SmartPaper 路径治理与旧入口切断收口方案

> 目标：围绕当前 `pytest --collect-only -q tests` 的 P0 阻塞，给出路径治理、旧入口兼容壳、包暴露策略与测试导入统一方案。
> 背景：当前项目处于“新四层目录 + legacy src/core/utils 双轨并存”阶段，且代码与测试中仍存在 `sys.path` 注入、旧入口漂移、可选依赖顶层硬导入等问题，导致 QA 判定架构契约仅“有条件通过”。

---

# 1. 当前问题归类

根据 QA 复核结果：

- `python -m pytest --collect-only -q tests`
- 现状：**30 tests collected, 10 errors**

当前 P0 阻塞主要分为三类：

## 1.1 旧入口漂移
命中对象：
- `core.smart_paper_core`
- `core.llm_wrapper`
- 旧 `core` 包内曾存在、现已删除或迁移的入口

受影响测试：
- `tests/core/test_paper_url.py`
- `tests/core/test_stream.py`
- `tests/integration/*`

## 1.2 utils 包暴露漂移
命中对象：
- `utils.get_abs_path`
- `utils.add_md_image_description`
- 以及 tests/tools/test_pdf_to_md_mineru.py 对 `utils.*` 的依赖

受影响测试：
- `tests/utils/*`
- `tests/tools/test_pdf_to_md_mineru.py`

## 1.3 可选依赖顶层硬导入
命中对象：
- `modelscope`
- MinerU / magic_pdf 等相关链路

受影响测试：
- `tests/utils/test_download_mineru_models.py`
- 以及所有在 import 阶段就触发可选依赖的模块

---

# 2. 收口目标

本专项方案的目标不是“临时让测试过”，而是达成以下四个架构目标：

1. **去掉运行时 path hack 作为长期机制**
2. **明确哪些旧入口保留兼容壳，哪些直接切断**
3. **统一测试导入策略，使 collect-only 不依赖隐式路径**
4. **为解析 / 研究地图 / Zotero / UI 四模块提供可执行的迁移边界**

---

# 3. 总体决策：三层入口策略

为避免继续扩大双轨混用，本轮建议采用“三层入口策略”：

## 3.1 正式入口层（长期保留）

这是对外稳定入口，允许长期存在：
- `smartpaper.py`
- `interfaces/cli/paper_cli.py`
- `streamlit.app.py`
- 新增的 application façade / use case 入口

这些入口的职责：
- 接收用户交互
- 调用 application 服务
- 不做 path hack
- 不直接面向 legacy `src/*` 编程

## 3.2 兼容壳层（短中期保留）

这是为“旧测试 / 旧脚本 / 旧导入路径”提供的过渡层，允许保留一段时间，但禁止继续扩散：

建议保留的兼容壳：
- `core.smart_paper_core`：保留一个薄兼容壳，内部转发到新 façade 或明确抛弃用说明
- `core.llm_wrapper`：保留一个薄兼容壳，仅满足旧测试 import 与最小行为兼容
- `utils.get_abs_path`
- `utils.add_md_image_description`

兼容壳的强约束：
- 只能做转发、别名、弃用警告
- 不能新增业务逻辑
- 不能继续成为新代码依赖目标
- 必须在文档中标注“deprecated / planned removal”

## 3.3 切断层（不再保留真实实现）

以下入口不应继续恢复为正式长期接口，只允许：
- 通过兼容壳临时托底，或
- 直接改测试/改调用方

应切断为长期依赖的对象：
- 任意 `sys.path.insert(...)` 注入方式
- 依赖物理目录结构暴露包的做法
- tests 直接假设 `src`/项目根一定已注入到解释器路径
- 页面/服务直接读取 legacy 存储文件作为“包 API”

---

# 4. path 注入治理决策

## 4.1 原则

### 原则 A：禁止新增
本轮开始，任何新提交不得再新增：
- `sys.path.insert(...)`
- `sys.path.append(...)`
- 硬编码绝对路径注入

### 原则 B：存量分级处理
现有 path 注入分两类：

#### 必须尽快移除
- `smartpaper.py` 中对项目根与 `src` 的直接注入
- `application/paper_analysis_service.py` 中的绝对路径注入
- `infrastructure/*` 中为调用 `src` 而做的路径注入

#### 可短暂容忍但要列入迁移批次
- 若某些旧测试依赖兼容壳，短期可通过包暴露/兼容模块解决，而不是继续注入 path

### 原则 C：用包结构替代 path hack
解决导入的正确方式只能是：
- 保证项目根是包根
- 明确 `src` 是否继续作为包空间的一部分
- 提供兼容模块而不是运行时插路径

## 4.2 具体治理方案

### 方案 1：项目根作为统一导入根
测试和运行统一从项目根导入：
- `application.*`
- `domain.*`
- `infrastructure.*`
- `interfaces.*`
- `src.*`（仅迁移期）

### 方案 2：停止使用裸 `core.*` / `utils.*` 作为真实实现来源
后续只允许两种情况：
- 旧测试暂时 import `core.*` / `utils.*`，由兼容壳提供
- 新代码一律 import 新包路径或 `src.*` 明确路径

### 方案 3：测试导入不依赖隐式 path
建议通过以下方式统一：
- 项目安装为 editable package，或
- 保证在项目根执行测试，并使用明确包路径

**不建议**通过 `conftest.py` 继续偷偷改 `sys.path` 作为长期方案。

---

# 5. 包暴露策略

## 5.1 目标状态

最终应收敛为：
- 新实现暴露在：`application/ domain/ infrastructure/ interfaces/`
- legacy 实现显式暴露在：`src/`
- 兼容壳暴露在：`core/`、`utils/`（如确有必要可新增顶层兼容包）

## 5.2 兼容包建议

为快速降低 collect 阻塞，建议允许新增两个“纯兼容包”：

### A. 顶层 `core/` 兼容包
用途：满足旧测试 `from core.xxx import ...`

建议只暴露：
- `smart_paper_core.py`（compat）
- `llm_wrapper.py`（compat）
- `document_converter.py`（compat，必要时）
- `prompt_manager.py`（compat 转发）
- `history_manager.py`（compat 转发）
- `profile_manager.py`（compat 转发）
- `config_loader.py`（compat 转发）

兼容实现策略：
- 优先转发到新 façade 或 `src/core/*`
- 文件头加 deprecated 注释
- 不新增复杂逻辑

### B. 顶层 `utils/` 兼容包
用途：满足旧测试 `from utils.xxx import ...`

建议只暴露：
- `get_abs_path.py`
- `add_md_image_description.py`
- 若必要，再补最少别名模块

兼容实现策略：
- 若真实实现仍在 `src/utils/*`，则直接转发
- 若真实实现已删除，则补薄实现或将对应测试迁移/废弃

## 5.3 为什么建议“兼容壳包”而不是“继续 path 注入”

原因：
- path 注入是运行时隐式行为，无法形成稳定边界
- 兼容壳是显式代码资产，可测试、可标记 deprecated、可逐步删除
- QA 可明确审查“壳是否缩小依赖面”而不是追踪隐藏的解释器状态

---

# 6. 哪些入口应保留兼容壳，哪些应切断

## 6.1 应保留兼容壳（短中期）

### core.smart_paper_core
保留原因：
- 多个旧测试与集成脚本直接依赖
- 可通过 compat SmartPaper 类转发到新 application façade

策略：
- 保留 import 能力
- 行为只需满足旧测试最小闭环
- 标注 deprecated

### core.llm_wrapper
保留原因：
- `tests/core/test_stream.py` 依赖
- 可作为轻量包装器转发到新 `LLMClient` 或兼容 stub

策略：
- 只支持旧测试所需的最小接口
- 不做长期功能扩展

### utils.get_abs_path / utils.add_md_image_description
保留原因：
- 直接命中 collect 阻塞
- 修复成本低，兼容收益高

策略：
- 如果真实实现还在，则转发
- 如果实现已删但测试仍有效，补纯函数实现并挂 deprecated 标记

## 6.2 应直接切断长期依赖

### smartpaper.py 内部 path 注入
结论：应移除

理由：
- 这是正式入口，不应再依赖运行时插路径
- 正式入口应基于明确包结构运行

### application/paper_analysis_service.py 内 path 注入
结论：应移除

理由：
- application 层是新架构核心，不应继续扩散 legacy 导入模式
- 若必须复用 legacy 逻辑，应通过 adapter/import 重构解决

### Streamlit 页面直接依赖 legacy 内部模块
结论：应切断

理由：
- UI 应只消费 façade / query service
- 不应通过页面层弥补包边界问题

### MultiPaperService 直接依赖旧文件结构作为长期输入
结论：应逐步切断

理由：
- 研究地图已开始成型，应迁移到稳定 DTO / repository

---

# 7. 测试导入统一方案

## 7.1 测试导入原则

### 原则 A：旧测试先兼容，新增测试只用新入口
- 旧测试：允许暂时继续 import `core.*` / `utils.*`，由 compat 壳托底
- 新测试：只允许 import 新架构包路径或明确的 façade

### 原则 B：collect-only 修复优先于测试内容重构
当前第一批不必立即重写所有旧测试逻辑，优先顺序应为：
1. 先让 import 可收集
2. 再决定哪些旧测试保留、迁移、删除

### 原则 C：测试不得再依赖在线外部服务作为 collect 前提
- MinerU / modelscope / magic_pdf 相关测试必须延迟导入或显式 skip
- import 阶段不得触发可选依赖硬失败

## 7.2 建议的统一落地方式

### 第一批：加兼容壳，修 collect
- 通过 `core/`、`utils/` compat 包让旧测试先 import 成功
- 调整 MinerU/modelscope 模块为函数内导入或 optional import

### 第二批：迁移测试指向新入口
- `tests/core/test_paper_url.py`、`tests/integration/*` 迁移到 façade/use case
- `tests/core/test_stream.py` 若功能已迁出，可重写为 `LLMClient`/compat wrapper smoke test

### 第三批：清理过时测试
删除或重写以下类型测试：
- 只验证旧路径存在、无实际产品价值的测试
- 强绑定已废弃入口、且不再代表真实用户工作流的测试

## 7.3 smoke test 建议

为弥补“文档契约已写但落地不足”，建议增加一组 smoke test：

### A. 入口导入 smoke test
- `import smartpaper`
- `import interfaces.cli.paper_cli`
- `import application.paper_analysis_service`
- `import application.research_map_service`

### B. 兼容壳 smoke test
- `import core.smart_paper_core`
- `import core.llm_wrapper`
- `import utils.get_abs_path`
- `import utils.add_md_image_description`

### C. 可选依赖 smoke test
- 在未安装 modelscope 的环境中，MinerU 相关模块 import 不应失败
- 相关测试应 skip 而不是 collect error

---

# 8. 四个执行模块的具体落地建议

# 8.1 解析模块

## 要做什么
- 停止在 application/service 中使用 path 注入
- 把 legacy `DocumentConverter` 的复用收敛到 adapter
- 若旧测试依赖 `core.smart_paper_core`，由 compat 壳转发到新解析 façade

## 不该做什么
- 不要继续让 `PaperAnalysisService` 直接承担 legacy 路径兼容
- 不要再让测试通过 `sys.path` 找解析模块

## 架构建议
- 新链路：`PaperIngestionService` / `KnowledgeCardService`
- 旧链路：`core.smart_paper_core` compat 壳
- 切断点：当 façade 覆盖旧测试后，逐步移除 compat 实现中的旧逻辑

# 8.2 研究地图模块

## 要做什么
- 研究地图新增代码一律使用新包路径，不接 legacy `core/*`
- `MultiPaperService` 如需兼容旧数据，只通过 DTO 适配，不直接靠 path hack 找旧模块
- 补入口 smoke test，证明地图服务可独立导入

## 不该做什么
- 不要把旧 history/jsonl 文件依赖再固化为包暴露策略
- 不要为了兼容 UI 再加隐式导入路径

## 架构建议
- 输入长期收敛到 `KnowledgeCardRepository`
- 短期可保留 `knowledge_base.jsonl -> DTO` adapter
- CLI/Streamlit 新入口都应直接指向新 map service

# 8.3 Zotero 模块

## 要做什么
- Zotero 从一开始就避免依赖 legacy `core/*`
- 所有同步状态、映射对象走 `application + infrastructure/zotero`
- 可选依赖/SDK 若未来引入，也必须 optional import，不得顶层硬失败

## 不该做什么
- 不要复用 `streamlit.session_state` 或旧 history 结构做 Zotero 主状态
- 不要把 Zotero 逻辑塞进 compat 壳

## 架构建议
- Zotero 是新能力，应直接站在新边界上，不要背 legacy 包袱
- 若需要旧测试支撑，只补 mapper / payload 单测，不补旧入口壳

# 8.4 UI 模块

## 要做什么
- Streamlit 页面逐步切断对 legacy 模块和底层实现的直接 import
- 改为只消费 façade/query service
- 若旧数据显示必须保留，则通过 query adapter 做兼容

## 不该做什么
- 不要在页面里直接 import `core.smart_paper_core`、`DocumentConverter`、`zotero_client`
- 不要把页面层当作路径兼容修复层

## 架构建议
- 页面不负责包暴露兼容
- UI 只依赖 application 层稳定入口
- 旧页面逻辑迁移优先于继续扩展单文件 `streamlit.app.py`

---

# 9. 第一执行批次建议（面向 collect 阻塞修复）

建议把后续执行切成三批：

## 批次 1：先清 collect P0
1. 新建 `core/` compat 包，补：
   - `smart_paper_core.py`
   - `llm_wrapper.py`
   - 必要的 config/prompt/history/profile 转发壳
2. 新建 `utils/` compat 包，补：
   - `get_abs_path.py`
   - `add_md_image_description.py`
3. 将 MinerU/modelscope 相关模块改为 optional import / lazy import
4. 增加 import smoke test

## 批次 2：移除正式代码中的 path 注入
1. 移除 `smartpaper.py` path 注入
2. 移除 `application/paper_analysis_service.py` path 注入
3. 移除 `infrastructure/*` 中为 legacy 而加的 path 注入
4. 用 adapter / compat 包替代

## 批次 3：迁移旧测试与删除过时壳
1. 重写旧测试到 façade / new services
2. 删除不再有产品价值的旧测试
3. 缩减 compat 壳暴露面
4. 最终移除 compat 包中无必要模块

---

# 10. 最终架构判定标准

本专项方案完成后，才能认为“架构契约从有条件通过接近正式通过”：

- `pytest --collect-only -q tests` 为 0 错误
- 正式入口不再包含 `sys.path` 注入
- compat 壳存在但依赖面停止扩大
- 新代码不再新增对 `core.*` / `utils.*` / legacy 文件结构的依赖
- 四个执行模块都按新边界接入，不再把路径兼容问题继续向下游扩散

---

# 11. 一句话决策

**SmartPaper 当前不应再靠 path 注入“维持可运行”，而应通过显式 compat 壳 + 新旧入口分层 + 测试导入统一策略完成收口：旧测试先用 compat 壳止血，正式代码同步移除 path hack，新模块一律只站在新架构边界上。**
