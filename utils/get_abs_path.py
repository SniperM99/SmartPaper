"""旧路径工具兼容实现。"""

from __future__ import annotations

import os


def get_abs_path(path: str, base_dir: str | None = None) -> str:
    if os.path.isabs(path):
        if not os.path.exists(path):
            raise ValueError(f"文件不存在: {path}")
        return path

    if base_dir is not None:
        if not os.path.isdir(base_dir):
            raise ValueError(f"基础目录不存在: {base_dir}")
        candidate = os.path.abspath(os.path.join(base_dir, path))
    else:
        candidate = os.path.abspath(path)

    if not os.path.exists(candidate):
        raise ValueError(f"文件不存在: {path}")
    return candidate
