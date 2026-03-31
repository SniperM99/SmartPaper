"""测试路径稳定器：确保项目根目录兼容包在 pytest 收集时优先可见。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

for package_name in ("utils", "core"):
    package_dir = ROOT / package_name
    init_file = package_dir / "__init__.py"
    if package_name not in sys.modules and init_file.exists():
        spec = importlib.util.spec_from_file_location(
            package_name,
            init_file,
            submodule_search_locations=[str(package_dir)],
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[package_name] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
