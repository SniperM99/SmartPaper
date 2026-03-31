"""兼容层：旧 core.prompt_manager -> src.core.prompt_manager。"""

from src.core.prompt_manager import *  # noqa: F401,F403
from src.core.prompt_manager import get_available_prompts


def list_prompts():
    return get_available_prompts()
