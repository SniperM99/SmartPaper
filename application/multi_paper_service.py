"""多论文综述与系统集成服务
负责跨论文的对比、演化链梳理以及创新空白发现。
"""

from typing import List, Dict, Any, Optional
from infrastructure.llm.llm_client import LLMClient
from application.research_map_service import ResearchMapService
from src.core.history_manager import HistoryManager
from src.core.prompt_manager import get_prompt
from langchain_core.messages import HumanMessage
from loguru import logger
import json

class MultiPaperService:
    """跨论文分析服务"""

    def __init__(self, config: Dict):
        """初始化服务
        
        Args:
            config: 应用配置字典
        """
        self.config = config
        self.llm_client = LLMClient(config)
        self.history_manager = HistoryManager()
        self.research_map_service = ResearchMapService(self.history_manager)


    def build_research_map(self, cache_keys: List[str]) -> Dict[str, Any]:
        """构建结构化研究地图。"""
        logger.info(f"构建研究地图: {len(cache_keys)} 篇论文")
        return self.research_map_service.build_from_cache_keys(cache_keys)

    def render_research_map(self, cache_keys: List[str]) -> str:
        """生成研究地图 Markdown 概览。"""
        research_map = self.build_research_map(cache_keys)
        if not research_map.get("entities"):
            return "❌ 未找到选定论文的结构化分析数据。"
        return self.research_map_service.render_markdown(research_map)

    def compare_papers(self, cache_keys: List[str]) -> str:
        """生成多论文横向对比矩阵
        
        Args:
            cache_keys: 论文缓存键列表
            
        Returns:
            str: Markdown 格式的对比报告
        """
        logger.info(f"执行多论文对比分析: {len(cache_keys)} 篇论文")
        structured_cards = self.history_manager.get_multiple_analyses(cache_keys)
        if not structured_cards:
            return "❌ 未找到选定论文的结构化分析数据，请确保已先进行单篇分析。"

        prompt_template = get_prompt("comparison_matrix")
        # 提取核心字段以减小 Token 压力
        minimized_cards = self._minimize_cards(structured_cards)
        prompt = prompt_template.format(text=json.dumps(minimized_cards, ensure_ascii=False, indent=2))
        
        return self.llm_client.chat([HumanMessage(content=prompt)])["content"]

    def trace_evolution(self, cache_keys: List[str]) -> str:
        """分析技术路线演化过程
        
        Args:
            cache_keys: 论文缓存键列表
            
        Returns:
            str: Markdown 格式的演化报告
        """
        logger.info(f"执行技术路线演化分析: {len(cache_keys)} 篇论文")
        structured_cards = self.history_manager.get_multiple_analyses(cache_keys)
        if not structured_cards:
            return "❌ 未找到选定论文的结构化分析数据。"

        # 按年份排序以展示时间线演化
        structured_cards.sort(key=lambda x: x.get("metadata", {}).get("year", "0"), reverse=False)
        
        prompt_template = get_prompt("evolution_trace")
        minimized_cards = self._minimize_cards(structured_cards)
        prompt = prompt_template.format(text=json.dumps(minimized_cards, ensure_ascii=False, indent=2))
        
        return self.llm_client.chat([HumanMessage(content=prompt)])["content"]

    def discover_gaps(self, cache_keys: List[str]) -> str:
        """识别研究空白与选题建议
        
        Args:
            cache_keys: 论文缓存键列表
            
        Returns:
            str: Markdown 格式的选题建议报告
        """
        logger.info(f"执行研究空白发现: {len(cache_keys)} 篇论文")
        structured_cards = self.history_manager.get_multiple_analyses(cache_keys)
        if not structured_cards:
            return "❌ 未找到选定论文的结构化分析数据。"

        prompt_template = get_prompt("research_gap_discovery")
        minimized_cards = self._minimize_cards(structured_cards)
        prompt = prompt_template.format(text=json.dumps(minimized_cards, ensure_ascii=False, indent=2))
        
        return self.llm_client.chat([HumanMessage(content=prompt)])["content"]

    def _minimize_cards(self, cards: List[Dict]) -> List[Dict]:
        """精简知识卡片内容，去除冗余的 trace 和 quality 分数，只保留对比所需的核心字段"""
        minimized = []
        for card in cards:
            meta = card.get("metadata", {})
            ana = card.get("analysis", {})
            minimized.append({
                "title": meta.get("title"),
                "year": meta.get("year"),
                "venue": meta.get("venue"),
                "summary": ana.get("summary_one_sentence"),
                "research_problem": ana.get("research_problem"),
                "method_overview": ana.get("method", {}).get("overview"),
                "method_tags": ana.get("method_tags", []),
                "innovation_points": ana.get("innovation_points", []),
                "limitations": ana.get("limitations", []),
                "dataset_tags": ana.get("dataset_tags", [])
            })
        return minimized
