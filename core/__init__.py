"""兼容层：对外暴露历史 core 包入口，内部转发到 src.core。"""

from src.core import SMART_PATH, get_smartpaper_root_path

__all__ = ["SMART_PATH", "get_smartpaper_root_path"]
