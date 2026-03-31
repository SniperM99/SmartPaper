"""为 Markdown 中的图片补描述的最小兼容实现。"""

from __future__ import annotations

from pathlib import Path
import re


def add_md_image_description(file_path: str, force_add_desc: bool = False) -> str:
    path = Path(file_path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    content = path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')

    def repl(match):
        alt, src = match.group(1), match.group(2)
        if alt and not force_add_desc:
            return match.group(0)
        fallback = Path(src).stem or "image"
        return f"![{fallback}]({src})"

    updated = pattern.sub(repl, content)
    path.write_text(updated, encoding="utf-8")
    return str(path)
