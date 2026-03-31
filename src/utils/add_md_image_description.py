"""兼容工具：为 Markdown 图片追加简单描述占位。"""

from __future__ import annotations

import re
from pathlib import Path


def add_md_image_description(file_path: str, force_add_desc: bool = False) -> str:
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    pattern = re.compile(r"(!\[[^\]]*\]\([^\)]+\))")

    def repl(match):
        image_md = match.group(1)
        if not force_add_desc and "<!-- image-description:" in image_md:
            return image_md
        return f"{image_md}\n\n<!-- image-description: TODO -->"

    updated = pattern.sub(repl, content)
    path.write_text(updated, encoding="utf-8")
    return str(path)
