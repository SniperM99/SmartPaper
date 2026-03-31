# SmartPaper 四处 sys.path 注入切断执行建议

> 目标：针对 `smartpaper.py`、`application/paper_analysis_service.py`、`streamlit.app.py`、`tests/test_research_map.py` 四处 `sys.path` 注入，给出逐文件切断顺序、compat 壳替代方案和最小 smoke test 建议。
> 适用对象：解析模块、研究地图模块、UI 模块、架构收口实现成员。

---

# 1. 总体执行原则

这四处 `sys.path` 注入的整改必须遵守以下原则：

1. **先保证替代导入路径存在，再删除注入**
   - 即先补 compat 壳 / 正式导入链
   - 再删 `sys.path.insert(...)`
2. **正式代码不再承担路径兼容责任**
   - 兼容应由 `core/`、`utils/` compat 壳承担
3. **测试文件也不得再用 path hack 自救**
   - 测试应验证真实包边界，而不是绕过它
4. **每切一个文件，都应做最小 import smoke test**

---

# 2. 切断顺序（推荐严格按此顺序执行）

## 第 1 顺位：`tests/test_research_map.py`

### 为什么先切
- 这是测试文件，修改成本最低
- 它不应继续成为“允许 path 注入”的例外
- 先切它可以验证研究地图真实导入链是否成立

## 第 2 顺位：`smartpaper.py`

### 为什么第二个切
- 它是正式 CLI 根入口
- 不应该再依赖项目根/`src` 的运行时插路径
- 切掉后能尽早暴露正式入口是否真的稳定

## 第 3 顺位：`application/paper_analysis_service.py`

### 为什么第三个切
- 它是新架构核心服务
- 继续保留 path 注入会把 legacy 兼容污染扩散到 application 层
- 但在 compat 壳没准备好前直接切风险较大，所以放在 smartpaper.py 之后

## 第 4 顺位：`streamlit.app.py`

### 为什么最后切
- 它依赖最复杂，牵涉 UI、application、legacy `core.*`
- 应在 compat 壳和 application 层导入链稳定后再切
- 否则页面容易一次性大面积导入失败

---

# 3. 逐文件整改建议

# 3.1 `tests/test_research_map.py`

## 当前问题
- 测试通过 `sys.path.insert(...)` 修正导入路径
- 这会掩盖研究地图真实包边界是否成立

## 切断动作
- 删除所有 `sys.path.insert(...)`
- 改成直接从项目根可见的正式路径导入

## 替代导入建议
优先使用：
- `from application.research_map_service import ...`
- `from domain.research_map import ...`

如果测试当前依赖其他 legacy 模块：
- 不要在测试里再补 path hack
- 应由 compat 壳或正式包导出解决

## 最小 smoke test
1. `python -m pytest --collect-only -q tests/test_research_map.py`
2. 断言单测可收集
3. 运行契约测试最小子集：
   - `python -m pytest -q tests/test_research_map.py`

## 通过标准
- 无 `sys.path` 注入
- 单文件 collect 成功
- 不新增对 `core.*` / `utils.*` 的依赖

---

# 3.2 `smartpaper.py`

## 当前问题
- 注入项目根与 `src`
- 正式 CLI 根入口通过 path hack 才能运行

## 切断动作
删除：
- `sys.path.insert(0, str(PROJECT_ROOT))`
- `sys.path.insert(0, str(PROJECT_ROOT / "src"))`

保留：
- `from interfaces.cli.paper_cli import main`

## compat 壳替代方案
`smartpaper.py` 本身不应依赖 compat 壳。
它的前提应是：
- `interfaces.cli.paper_cli` 可直接导入
- `paper_cli` 里若还需旧配置/prompt/history，则通过 `core/*` compat 壳解决，而不是在 `smartpaper.py` 里插路径

## 最小 smoke test
1. `python -c "import smartpaper"`
2. `python smartpaper.py --help`
3. 如 CLI 参数结构稳定，可补：
   - `python smartpaper.py prompts`

## 通过标准
- `smartpaper.py` 无 `sys.path` 注入
- import 成功
- CLI 帮助信息可输出

---

# 3.3 `application/paper_analysis_service.py`

## 当前问题
- 存在绝对路径形式 `sys.path.insert`
- application 层直接承担 legacy 路径兼容

## 切断动作
- 删除绝对路径 `sys.path.insert(...)`

## compat 壳替代方案
短期替代：
- 允许继续 import `core.prompt_manager`
- 允许继续 import `core.history_manager`
- 允许继续 import `core.task_manager`（若需 compat，可补）
- 允许继续 import `core.profile_manager`

但前提是：
- 这些 `core.*` 必须来自显式 compat 包，而不是靠 path 注入找到 `src/core/*`

对于 `SectionSplitter`：
- 短期可保留 `from src.utils.section_splitter import SectionSplitter`
- 不需要再为它插路径

## 风险提示
这是最容易“删了 path 就引发连锁导入失败”的文件，因此必须在切之前先确保：
- `core/` compat 包存在
- `src` 可作为显式包路径被正常导入

## 最小 smoke test
1. `python -c "import application.paper_analysis_service"`
2. 若构造对象不触发外部服务：
   - `python - <<'PY'
from core.config_loader import load_config
from application.paper_analysis_service import PaperAnalysisService
cfg = load_config()
svc = PaperAnalysisService(cfg)
print(type(svc).__name__)
PY`
3. `python -m pytest --collect-only -q tests/test_research_map.py tests/test_schemas.py`

## 通过标准
- 无绝对路径 `sys.path` 注入
- application 层不再承担路径兼容
- import / 初始化最小对象成功

---

# 3.4 `streamlit.app.py`

## 当前问题
- 注入项目根与 `src`
- UI 脚本承担了包路径修复职责
- 仍直接依赖 `core.*` 与部分 legacy 逻辑

## 切断动作
删除：
- `BASE_DIR` 注入逻辑
- `SRC_DIR` 注入逻辑

## compat 壳替代方案
短期允许：
- `from core.prompt_manager import ...`
- `from core.history_manager import ...`
- `from core.profile_manager import ...`
- `from core.config_loader import ...`

这些都应由 compat `core/` 托底。

中期建议：
- 逐步改成 façade / query service
- 页面不再直接依赖 history/profile/prompt 的 legacy 细节

## 风险提示
该文件受影响范围最大：
- Streamlit 页面导入失败会直接阻塞 UI 验证
- 因此必须在 `smartpaper.py` 与 `application/paper_analysis_service.py` 稳定后再切

## 最小 smoke test
1. `python -c "import importlib.util; print(importlib.util.spec_from_file_location('sp_app','streamlit.app.py') is not None)"`
2. 关键函数导入/执行 smoke：
   - `main`
   - `process_paper`
3. 若环境允许：
   - `streamlit run streamlit.app.py --server.headless true`
   - 仅验证启动阶段不因 import 失败崩溃

## 通过标准
- 无 `sys.path` 注入
- 页面模块可导入
- 启动阶段不因导入失败崩溃

---

# 4. compat 壳替代映射表

| 被切文件 | 删除的 path 注入用途 | 替代方式 |
|---|---|---|
| `tests/test_research_map.py` | 让测试能找到 application/domain | 直接用正式包路径导入 |
| `smartpaper.py` | 让 CLI 找到 interfaces/src | 依赖正式包导入；legacy 兼容下沉到 compat 壳 |
| `application/paper_analysis_service.py` | 让 service 找到 core/src | `core/*` compat 壳 + 显式 `src.*` 导入 |
| `streamlit.app.py` | 让 UI 找到 core/application/src | `core/*` compat 壳 + 正式 application 导入 |

---

# 5. 最小 smoke test 执行顺序

建议实现成员按下面顺序执行，而不是一次性全删后再排错。

## 步骤 1：先验证 compat 壳存在
1. `python -c "import core"`
2. `python -c "import utils"`
3. `python -c "import core.smart_paper_core"`
4. `python -c "import core.llm_wrapper"`

## 步骤 2：切 `tests/test_research_map.py`
1. 删除 path 注入
2. `python -m pytest --collect-only -q tests/test_research_map.py`
3. `python -m pytest -q tests/test_research_map.py`

## 步骤 3：切 `smartpaper.py`
1. 删除 path 注入
2. `python -c "import smartpaper"`
3. `python smartpaper.py --help`

## 步骤 4：切 `application/paper_analysis_service.py`
1. 删除 path 注入
2. `python -c "import application.paper_analysis_service"`
3. 最小实例化 smoke test

## 步骤 5：切 `streamlit.app.py`
1. 删除 path 注入
2. 模块导入 smoke test
3. 如环境允许，再做 headless 启动 smoke test

## 步骤 6：回到项目级 collect
1. `python -m pytest --collect-only -q tests`
2. 观察是否从 10 errors 下降

---

# 6. 推荐负责人分工建议

## 解析模块 / 架构协同
负责：
- `smartpaper.py`
- `application/paper_analysis_service.py`
- 相关 compat `core/*`

## 研究地图模块
负责：
- `tests/test_research_map.py`
- `application.research_map_service` 导入链稳定性

## UI 模块
负责：
- `streamlit.app.py`
- 页面 smoke test

## QA / 评审
负责复核：
- 项目级 `pytest --collect-only -q tests`
- 四文件 `sys.path` 是否已完全移除

---

# 7. 一句话执行标准

**先切 `tests/test_research_map.py`，再切 `smartpaper.py`，再切 `application/paper_analysis_service.py`，最后切 `streamlit.app.py`；每切一个文件都必须有 compat 替代与最小 smoke test 托底，不能一次性裸删。**
