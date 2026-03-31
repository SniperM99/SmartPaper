"""旧 LLMWrapper 的兼容壳，仅保留测试所需最小接口。"""

from typing import Iterable, List

from langchain_core.messages import BaseMessage

from utils.llm_adapter import create_llm_adapter


class LLMWrapper:
    def __init__(self, config):
        self.config = config
        self.adapter = create_llm_adapter(config.get("llm", config))

    def _stream_chat(self, messages: List[BaseMessage]) -> Iterable[str]:
        yield from self.adapter.stream(messages)
