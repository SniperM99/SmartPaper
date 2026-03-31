# SmartPaper 文件级迁移与兼容壳处理清单

> 用途：把 `docs/PATH_GOVERNANCE_AND_COMPAT_PLAN.md` 细化到文件/目录级执行清单，供后续实际修复 `pytest --collect-only -q tests` 与 `sys.path` 问题时直接执行。
> 目标：明确 compat 壳保留范围、旧入口切断对象、测试导入迁移点、目录级迁移建议，以及 smoke test 验证顺序。

---

# 0. 当前执行目标

当前不是继续讨论方案，而是进入“按文件执行”的准备阶段。第一目标仍然是：

1. `python -m pytest --collect-only -q tests` 从 **30 collected / 10 errors** 降到 **0 errors**
2. 移除正式代码中的 `sys.path.insert(...)`
3. 用显式 compat 壳替代旧入口漂移

---

# 1. 顶层目录治理决策

## 1.1 建议新增/保留目录

### A. 新增顶层 `core/` compat 包
用途：托底旧测试与旧脚本中的 `from core.xxx import ...`

建议目录结构：

```text
core/
  __init__.py
  smart_paper_core.py
  llm_wrapper.py
  config_loader.py
  prompt_manager.py
  history_manager.py
  profile_manager.py
  document_converter.py   # 如旧测试仍需要
```

### B. 新增顶层 `utils/` compat 包
用途：托底旧测试中的 `from utils.xxx import ...`

建议目录结构：

```text
utils/
  __init__.py
  get_abs_path.py
  add_md_image_description.py
```

### C. 保留 `src/` 作为 legacy 实现目录
原则：
- `src/` 保留，但只作为 legacy 实现
- 新代码不再新增对 `src/*` 的直接依赖，除非在 adapter/compat 中过渡调用

---

# 2. 必须保留的 compat 壳文件清单

## 2.1 `core/__init__.py`

### 动作
- 新增/保留

### 责任
- 导出最少兼容符号
- 若旧测试需要 `from core import SMART_PATH`，可在此定义：
  - `SMART_PATH = Path(__file__).resolve().parent.parent`

### 备注
- 只做兼容，不承载业务逻辑

## 2.2 `core/smart_paper_core.py`

### 动作
- 新增 compat 壳

### 责任
- 提供旧测试所需 `SmartPaper` 类
- 内部转发到新 façade 或现有 `application.paper_analysis_service.PaperAnalysisService`

### 最小兼容接口建议
- `SmartPaper(output_format="markdown")`
- `process_paper(path, prompt_name=None, ...)`
- `process_paper_url(url, prompt_name=None, mode=None, description=None, ...)`

### 不要做的事
- 不要在此文件新增复杂业务逻辑
- 不要再写 `sys.path.insert`

## 2.3 `core/llm_wrapper.py`

### 动作
- 新增 compat 壳

### 责任
- 满足 `tests/core/test_stream.py` 对 `LLMWrapper` 的 import 需求

### 最小兼容接口建议
- `LLMWrapper(config)`
- `_stream_chat(messages)`

### 实现建议
- 直接薄包装 `infrastructure.llm.llm_client.LLMClient`
- 或仅提供最小流式转发能力

## 2.4 `core/config_loader.py`

### 动作
- 新增 compat 转发壳

### 责任
- 将旧导入：`from core.config_loader import load_config`
- 转发到：`src.core.config_loader` 或未来新位置

## 2.5 `core/prompt_manager.py`

### 动作
- 新增 compat 转发壳

### 责任
- 转发：`get_prompt` / `compose_prompt` / `get_available_options`
- 若旧测试仍使用 `list_prompts`，可在 compat 层补别名

## 2.6 `core/history_manager.py`

### 动作
- 新增 compat 转发壳

### 责任
- 满足仍使用旧 import 的代码与测试
- 实际实现转发到 `src.core.history_manager`

## 2.7 `core/profile_manager.py`

### 动作
- 新增 compat 转发壳

### 责任
- 转发到 `src.core.profile_manager`

## 2.8 `core/document_converter.py`

### 动作
- 新增 compat 转发壳（必要）

### 责任
- 满足 `tests/tools/test_document_converter.py` / `tests/tools/test_arxiv_download_read.py`
- 转发到 `src.core.document_converter`

## 2.9 `utils/get_abs_path.py`

### 动作
- 新增 compat 壳或恢复纯函数实现

### 责任
- 满足 `tests/utils/test_get_abs_path.py`
- 若真实实现已删，可直接补纯函数

## 2.10 `utils/add_md_image_description.py`

### 动作
- 新增 compat 壳或恢复最小实现

### 责任
- 满足 `tests/utils/test_add_md_image_description.py`
- 若真实实现仍在 legacy 目录，直接转发

---

# 3. 应切断/移除的文件级入口

## 3.1 `smartpaper.py`

### 当前问题
- 存在 `sys.path.insert(0, str(PROJECT_ROOT))`
- 存在 `sys.path.insert(0, str(PROJECT_ROOT / "src"))`

### 动作
- 移除 path 注入

### 替代方式
- 保证从项目根运行
- 通过明确包导入：`from interfaces.cli.paper_cli import main`

### 验证
- `python smartpaper.py --help` 或最小 CLI import smoke test

## 3.2 `application/paper_analysis_service.py`

### 当前问题
- 存在绝对路径形式的 `sys.path.insert`
- application 层直接承担 legacy 路径兼容

### 动作
- 移除 path 注入

### 替代方式
- 对 `core.*` / `src.*` 依赖改为：
  - compat 包导入，或
  - 新 adapter 导入

### 验证
- `import application.paper_analysis_service`
- 单篇分析最小 smoke test

## 3.3 `streamlit.app.py`

### 当前问题
- 存在项目根与 `src` 的 `sys.path` 注入
- UI 直接承担包路径修复责任

### 动作
- 移除 path 注入

### 替代方式
- 依赖正式包导入
- 若需旧模块兼容，由 compat 壳解决，而非页面脚本注入路径

### 验证
- `import streamlit.app.py` 对应的页面模块 smoke test（至少验证关键函数可导入）

## 3.4 `infrastructure/llm/llm_client.py`

### 当前问题
- 通过 `sys.path.insert(.../src)` 间接依赖 `utils.llm_adapter`

### 动作
- 移除 path 注入

### 替代方式
- 显式改成：
  - 从 `src.utils.llm_adapter` 导入（迁移期）
  - 或迁移到正式包路径

## 3.5 `infrastructure/pdf/pdf_converter.py`

### 当前问题
- 通过 path 注入依赖 `core.document_converter`

### 动作
- 移除 path 注入

### 替代方式
- 直接 import compat `core.document_converter`
- 或直接 import `src.core.document_converter`

---

# 4. 目录级迁移建议

## 4.1 `application/`

### 原则
- 不再承担 legacy 包路径兼容
- 只依赖正式包路径或 adapter/compat 壳

### 文件级建议
- `application/paper_analysis_service.py`
  - 去掉 path 注入
  - 将 `from core.*` 保留为 compat import（短期）
  - 将 `from src.utils.section_splitter` 记录为下轮迁移目标
- `application/multi_paper_service.py`
  - 短期允许保留 `core.history_manager` compat import
  - 中期切到 repository/query service
- `application/research_map_service.py`
  - 不得新增对 `core.*` / `utils.*` 依赖

## 4.2 `interfaces/`

### 原则
- 只依赖 application 层
- 不直接承担导入兼容

### 文件级建议
- `interfaces/cli/paper_cli.py`
  - 允许短期保留 `core.config_loader` compat import
  - 中期切到 application façade +正式配置模块
- `streamlit.app.py`
  - 第一批必须去掉 path 注入
  - 后续再切页面直连 legacy 模块

## 4.3 `infrastructure/`

### 原则
- 通过显式 import 或 adapter 调用 legacy
- 不做路径注入

### 文件级建议
- `infrastructure/llm/llm_client.py`
  - 修正对 `llm_adapter` 的路径依赖
- `infrastructure/pdf/pdf_converter.py`
  - 修正对 `DocumentConverter` 的路径依赖
- `infrastructure/zotero/`
  - 新增能力时不得重走 compat/path hack 路线

## 4.4 `src/`

### 原则
- 明确保留为 legacy
- 不再新增“对外推荐”导出

### 文件级建议
- `src/core/*`
  - 作为 compat 壳的真实转发目标
- `src/utils/*`
  - 对应 `utils/` compat 包的转发目标
- 未来逐步减少被直接消费面

---

# 5. 测试文件级调整清单

## 5.1 先通过 compat 壳修复 collect 的测试

### A. `tests/core/test_SMART_PATH.py`

#### 当前依赖
- `from core import SMART_PATH`

#### 动作
- 通过 `core/__init__.py` 提供 `SMART_PATH`

#### 后续迁移
- 可保留为 smoke test

### B. `tests/core/test_paper_url.py`

#### 当前依赖
- `from core.smart_paper_core import SmartPaper`
- `from core.prompt_manager import list_prompts`

#### 动作
- 先由 compat 壳托底 import
- `list_prompts` 可在 compat prompt_manager 中补别名

#### 后续迁移
- 改写为 façade / service 测试

### C. `tests/core/test_stream.py`

#### 当前依赖
- `from core.llm_wrapper import LLMWrapper`

#### 动作
- 先由 compat `core/llm_wrapper.py` 托底

#### 后续迁移
- 改为 `LLMClient` 或 stream façade smoke test

### D. `tests/integration/test_single_url.py`
### E. `tests/integration/test_single_local_papers.py`
### F. `tests/integration/test_multiple_urls.py`

#### 当前依赖
- `from core.smart_paper_core import SmartPaper`

#### 动作
- 先由 compat 壳托底 import

#### 后续迁移
- 改写到 application façade

### G. `tests/tools/test_pdf_to_md_mineru.py`

#### 当前依赖
- `from utils.get_abs_path import get_abs_path`

#### 动作
- 由 compat `utils/get_abs_path.py` 托底

### H. `tests/utils/test_get_abs_path.py`

#### 动作
- compat `utils/get_abs_path.py` 托底

### I. `tests/utils/test_add_md_image_description.py`

#### 动作
- compat `utils/add_md_image_description.py` 托底

### J. `tests/utils/test_download_mineru_models.py`

#### 当前问题
- `modelscope` 顶层硬导入导致 collect error

#### 动作
- 将对应实现模块改为 lazy import / optional import
- 测试中若依赖缺失应 `pytest.skip`，不能 import 阶段报错

---

# 6. 建议直接修改的导入路径清单

## 6.1 正式代码中建议替换

### `infrastructure/llm/llm_client.py`
- 现状：依赖 path 注入后 `from utils.llm_adapter import create_llm_adapter`
- 建议替换为：`from src.utils.llm_adapter import create_llm_adapter`
  - 或未来迁到正式包路径

### `infrastructure/pdf/pdf_converter.py`
- 现状：依赖 path 注入后 `from core.document_converter import DocumentConverter`
- 建议短期：保留 `from core.document_converter import DocumentConverter`，但由 compat 包托底
- 建议中期：迁成 `from src.core.document_converter import DocumentConverter`
  - 或迁到正式 infrastructure adapter

### `application/paper_analysis_service.py`
- 现状：通过 path 注入再 import `core.*`
- 建议短期：删除 path 注入，直接 import compat `core.*`
- 建议中期：把 `core.*` 逐步迁到正式模块/adapter

### `streamlit.app.py`
- 现状：通过 path 注入使用 `core.*`
- 建议短期：删除 path 注入，直接 import compat `core.*`
- 建议中期：改为 façade/query service

---

# 7. smoke test 建议顺序

建议按“先包存在，再正式入口，再兼容壳，再可选依赖”的顺序验证。

## 第一步：compat 包存在性
1. `import core`
2. `import utils`
3. `from core import SMART_PATH`
4. `import core.smart_paper_core`
5. `import core.llm_wrapper`
6. `import utils.get_abs_path`
7. `import utils.add_md_image_description`

## 第二步：正式入口导入
1. `import smartpaper`
2. `import interfaces.cli.paper_cli`
3. `import application.paper_analysis_service`
4. `import application.multi_paper_service`
5. `import application.research_map_service`

## 第三步：基础设施导入
1. `import infrastructure.llm.llm_client`
2. `import infrastructure.pdf.pdf_converter`

## 第四步：UI 导入
1. 验证 `streamlit.app.py` 关键函数可导入
2. 至少做一次页面级轻量 smoke test

## 第五步：可选依赖链路
1. 在未安装 `modelscope` 情况下 import MinerU 相关模块
2. 断言不会 collect error
3. 如依赖缺失，则测试 skip

## 第六步：collect-only 总验证
1. `python -m pytest --collect-only -q tests`
2. 目标：0 errors

---

# 8. 推荐执行批次

## 批次 A：compat 壳止血
- 新建 `core/`
- 新建 `utils/`
- 补齐 compat 文件
- 先把旧测试 import 托底

## 批次 B：切正式代码 path 注入
- `smartpaper.py`
- `application/paper_analysis_service.py`
- `streamlit.app.py`
- `infrastructure/llm/llm_client.py`
- `infrastructure/pdf/pdf_converter.py`

## 批次 C：修可选依赖硬失败
- MinerU / modelscope / magic_pdf 相关模块
- 改 lazy import / optional import / skip

## 批次 D：迁移旧测试到新入口
- 重写 `tests/core/*`
- 重写 `tests/integration/*`
- 删除失效旧测试

---

# 9. 文件级完成标准

当以下条件满足时，才算本清单执行完成：

- compat 壳已补齐，旧测试 import 不再报模块不存在
- 正式代码中的 `sys.path.insert(...)` 已从关键入口移除
- MinerU/modelscope 不再在 import 阶段硬失败
- smoke test 顺序验证通过
- `pytest --collect-only -q tests` 为 0 errors

---

# 10. 一句话执行口令

**先补 compat 壳止血旧测试导入，再切正式代码 path 注入，再修可选依赖顶层硬导入，最后迁移旧测试到新入口；不要反过来。**
