"""兼容工具：将输入路径转换为绝对路径。"""

from __future__ import annotations

import os
from typing import Optional


def get_abs_path(path: str, base_dir: Optional[str] = None) -> str:
    if os.path.isabs(path):
        abs_path = path
    else:
        if base_dir is not None:
            if not os.path.isdir(base_dir):
                raise ValueError("基础目录不存在")
            abs_path = os.path.abspath(os.path.join(base_dir, path))
        else:
            abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise ValueError("文件不存在")
    return abs_path
