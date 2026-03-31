"""LLM 客户端 - 基础设施层

封装各种 LLM 提供商的 API 调用
"""

from typing import Dict, Optional, Generator, List, Any
from langchain_core.messages import HumanMessage, BaseMessage
from src.utils.llm_adapter import create_llm_adapter
from loguru import logger


class LLMClient:
    """LLM 客户端 - 负责与 LLM API 交互"""

    def __init__(self, config: Dict):
        """初始化 LLM 客户端

        Args:
            config: LLM 配置字典
        """
        self.config = config
        self.llm = create_llm_adapter(config["llm"])
        self.request_count = 0
        self.max_requests = config["llm"].get("max_requests", 10)

        provider = config["llm"]["provider"]
        model_index = config["llm"].get("default_model_index", 0)
        model = config["llm"][provider]["models"][model_index]

        logger.info(f"LLM 客户端初始化：{provider} / {model}")

    def chat(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """普通聊天请求

        Args:
            messages: 消息列表

        Returns:
            Dict: 包含 content, usage, model 等信息
        """
        if self.request_count >= self.max_requests:
            raise Exception(f"已达到最大请求次数限制 ({self.max_requests}次)")

        self.request_count += 1
        response = self.llm(messages)
        
        # 尝试从适配器响应中提取元数据
        usage = getattr(response, "response_metadata", {}).get("token_usage", {})
        model = getattr(response, "response_metadata", {}).get("model_name", "unknown")
        
        return {
            "content": response.content,
            "usage": usage,
            "model": model
        }

    def chat_stream(self, messages: List[BaseMessage]) -> Generator[str, None, None]:
        """流式聊天请求

        Args:
            messages: 消息列表

        Yields:
            流式响应文本片段
        """
        if self.request_count >= self.max_requests:
            raise Exception(f"已达到最大请求次数限制 ({self.max_requests}次)")

        self.request_count += 1
        for chunk in self.llm.stream(messages):
            yield chunk

    def update_api_key(self, api_key: str):
        """更新 API 密钥"""
        self.llm.update_api_key(api_key)

    def reset_request_count(self):
        """重置请求计数"""
        self.request_count = 0

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "provider": self.config["llm"]["provider"],
            "request_count": self.request_count,
            "max_requests": self.max_requests,
        }
