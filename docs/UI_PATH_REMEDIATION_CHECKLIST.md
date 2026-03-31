# SmartPaper UI 路径治理整改清单

> 目标：面向工作台工程师，针对 `streamlit.app.py` 及相关 UI 入口，明确旧入口切断、compat 壳替代、`sys.path` 去除建议和 smoke test 落点。
> 依据：`docs/FILE_LEVEL_MIGRATION_CHECKLIST.md`、`docs/PATH_GOVERNANCE_AND_COMPAT_PLAN.md`、`docs/SYSPATH_CUTOFF_EXECUTION_GUIDE.md`

---

# 1. 本次 UI 整改目标

UI 侧本轮整改不是重写页面，而是先完成三件事：

1. **切断 `streamlit.app.py` 的 `sys.path` 注入**
2. **把 UI 对 legacy 导入的依赖收敛到显式 compat 壳**
3. **为后续 façade/query service 迁移留下稳定落点**

当前 UI 侧的首要任务不是“继续加功能”，而是先消除它作为包路径兼容修复层的职责。

---

# 2. UI 当前问题定位

## 2.1 `streamlit.app.py` 当前问题

### 问题 A：仍存在 `sys.path` 注入
当前文件中有：
- 将项目根目录插入 `sys.path`
- 将 `src` 目录插入 `sys.path`

这意味着：
- UI 启动依赖运行时路径修复
- 页面层掩盖了真正的包暴露问题
- 无法证明 UI 工作流是否真的建立在稳定入口上

### 问题 B：页面层仍直接依赖 legacy `core.*`
当前依赖包括：
- `core.prompt_manager`
- `core.history_manager`
- `core.profile_manager`
- `core.config_loader`

这些依赖短期可以保留，但必须通过 **compat 壳**，而不是继续通过 path hack 找 `src/core/*`

### 问题 C：页面仍直接编排工作流细节
当前页面里有：
- 直接 new `PaperAnalysisService`
- 直接 new `MultiPaperService`
- 直接持有历史记录与画像对象
- 直接拼接多 workspace 的工作流逻辑

这不属于本轮必须全部解决的问题，但必须确保：
- 先切掉 path 注入
- 再逐步向 façade / query service 收敛

---

# 3. UI 入口整改范围

本轮建议 UI 工程师重点处理以下入口：

## 一级整改对象（必须本轮处理）
- `streamlit.app.py`

## 二级关联对象（与 UI 导入链直接相关）
- `interfaces/cli/paper_cli.py`（用于对照正式入口边界）
- `application/paper_analysis_service.py`（UI 当前直接依赖）
- `application/multi_paper_service.py`
- `application/research_map_service.py`（如 UI 已接入研究地图）
- compat `core/*` 壳（为 UI 提供旧导入托底）

---

# 4. 旧入口切断建议

## 4.1 必须切断的 UI 旧入口使用方式

### A. 切断 `sys.path` 作为导入前提
在 `streamlit.app.py` 中删除：
- `BASE_DIR` 注入逻辑
- `SRC_DIR` 注入逻辑
- 所有 `sys.path.insert(...)`

### B. 切断“页面负责包修复”
页面文件不能再承担：
- 决定项目根路径
- 决定 legacy `src` 如何被找到
- 为 `core.*` / `utils.*` 动态补路径

### C. 切断新增底层直连
本轮之后禁止 UI 新增直接 import：
- `DocumentConverter`
- `LLMClient`
- `zotero_client`
- `src.*` 下工具实现
- 物理文件格式解析逻辑

---

# 5. compat 壳替代建议（UI 视角）

UI 工程师短期可以保留的旧导入，只能来自显式 compat 壳。

## 5.1 允许短期保留的 import

### A. 配置与 prompt
允许：
- `from core.config_loader import load_config`
- `from core.prompt_manager import get_available_options, compose_prompt`

### B. 历史与画像
允许：
- `from core.history_manager import HistoryManager`
- `from core.profile_manager import ProfileManager`

### C. 不建议但短期可接受
- UI 继续直接 import `application.paper_analysis_service.PaperAnalysisService`
- UI 继续直接 import `application.multi_paper_service.MultiPaperService`

前提：
- 不再通过 path 注入获得这些 import
- import 解析完全依赖正式包路径 + compat 壳

## 5.2 不应在 UI 侧引入的 compat 方向

UI 不应继续依赖：
- `core.smart_paper_core`
- `core.llm_wrapper`
- `utils.*` 工具函数作为页面主逻辑依赖

原因：
- 这些是为旧测试/旧脚本托底，不是给工作台长期使用的入口

---

# 6. `streamlit.app.py` 的直接整改建议

## 6.1 第一刀：删除 path 注入块

删除整段：
- 基于 `BASE_DIR` 的项目根插入
- 基于 `SRC_DIR` 的 `src` 插入

保留的 import 应改为直接依赖：
- 正式包路径
- compat `core/*`

## 6.2 第二刀：保留旧 import，但明确只走 compat 壳

短期保留：
- `core.prompt_manager`
- `core.history_manager`
- `core.profile_manager`
- `core.config_loader`

要求：
- 这些模块必须来自顶层 compat 包
- 不允许再通过页面里的路径逻辑隐式解析到 `src/core/*`

## 6.3 第三刀：把 UI 直接依赖的服务收敛到 application

短期可保留：
- `PaperAnalysisService`
- `MultiPaperService`
- `ResearchMapService`（若已接入）

但必须避免新增：
- 直接访问基础设施层
- 直接访问 legacy 工具函数
- 直接解析 `saved_analyses/*.jsonl/*.csv`

## 6.4 第四刀：为后续拆分留接口位置

建议在 `streamlit.app.py` 中逐步形成以下边界：
- 页面状态管理
- façade 调用层
- DTO 展示层

即使本轮不重构，也建议 UI 工程师在代码中留注释或 TODO：
- 哪些函数未来迁出到 workspace 模块
- 哪些查询改由 query service 承担

---

# 7. 相关 UI 入口的整改落点

## 7.1 `streamlit.app.py`

### 本轮必须完成
- [ ] 删除所有 `sys.path.insert(...)`
- [ ] 改为正式包导入 + compat 壳导入
- [ ] 不新增底层直连
- [ ] 保持关键 workspace 可导入

### 本轮可暂缓
- [ ] 完全拆分为多文件 workspace
- [ ] 完全移除 `HistoryManager` / `ProfileManager` 页面直连
- [ ] 全量替换为 façade/query service

## 7.2 `interfaces/cli/paper_cli.py`

### 为什么要顺带检查
- 它和 Streamlit 一样都是正式入口
- 可以作为“UI 不做路径兼容”的对照参考

### 建议
- 保持只依赖 application + compat `core.config_loader`
- 不新增 path 注入

## 7.3 研究地图 UI 入口

如果当前页面已接入研究地图：
- 应直接依赖 `application.research_map_service` 或后续 query service
- 不应直接依赖旧历史文件
- 不应直接依赖 `knowledge_base.jsonl` 物理路径

## 7.4 Zotero UI 入口（未来/在做）

建议从一开始就遵守：
- 只通过 application / query service 接入
- 不在页面层补 compat for Zotero SDK
- 不让页面承担同步状态存储职责

---

# 8. UI smoke test 落点

UI 工程师整改后，应至少补这 3 级验证。

## 8.1 级别 1：模块导入 smoke test（必须）

建议命令：
1. 验证文件可解析
   - `python -c "import importlib.util; print(importlib.util.spec_from_file_location('sp_app','streamlit.app.py') is not None)"`
2. 验证 compat 壳可导入
   - `python -c "from core.config_loader import load_config"`
   - `python -c "from core.prompt_manager import get_available_options"`
   - `python -c "from core.history_manager import HistoryManager"`
   - `python -c "from core.profile_manager import ProfileManager"`
3. 验证 application 服务可导入
   - `python -c "from application.paper_analysis_service import PaperAnalysisService"`
   - `python -c "from application.multi_paper_service import MultiPaperService"`

## 8.2 级别 2：关键函数 smoke test（强烈建议）

建议至少验证：
- `main`
- `process_paper`
- `render_profile_editor`

做法：
- 用最小导入测试这些函数存在
- 不要求真实启动外部服务

## 8.3 级别 3：headless 启动 smoke test（推荐）

若环境允许，执行：
- `streamlit run streamlit.app.py --server.headless true`

目标仅为：
- 启动阶段不因 import/path 问题崩溃
- 不要求完成功能交互回归

---

# 9. 面向工作台工程师的最终整改清单

UI 工程师可按下面 checklist 直接执行：

## 必做项
- [ ] 删除 `streamlit.app.py` 中全部 `sys.path.insert(...)`
- [ ] 保证 `core.config_loader` / `core.prompt_manager` / `core.history_manager` / `core.profile_manager` 通过 compat 壳解析
- [ ] 保证 `PaperAnalysisService` / `MultiPaperService` / `ResearchMapService` 可直接导入
- [ ] 不新增对基础设施层与 legacy 工具函数的页面直连
- [ ] 补至少 1 组模块导入 smoke test

## 强烈建议项
- [ ] 补关键函数 smoke test
- [ ] 做 1 次 headless 启动验证
- [ ] 给研究地图页面改成依赖稳定 query/consumer contract
- [ ] 给页面中仍保留的 legacy 依赖加 TODO 标记

## 暂缓项（本轮非阻塞）
- [ ] 拆分 `streamlit.app.py`
- [ ] 全量 façade 化
- [ ] 页面状态 DTO 全量统一

---

# 10. 一句话给 UI 工程师的执行建议

**本轮 UI 不要求一次性重构工作台，但必须先把 `streamlit.app.py` 从“路径兼容修复脚本”变回“正式入口文件”：删掉 `sys.path` 注入，旧依赖只走 compat 壳，新能力只接 application。**
