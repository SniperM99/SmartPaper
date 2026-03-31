"""旧 SmartPaper 入口兼容壳。"""

from __future__ import annotations

from typing import Optional

from application.paper_analysis_service import PaperAnalysisService
from core.config_loader import load_config


class SmartPaper:
    def __init__(self, output_format: str = "markdown", config: Optional[dict] = None):
        self.output_format = output_format
        self.config = config or load_config()
        self.service = PaperAnalysisService(self.config)

    def process_paper(self, paper_path: str, prompt_name: Optional[str] = None, **kwargs):
        result = self.service.analyze_file(paper_path, prompt_name=prompt_name, **kwargs)
        return self._adapt_result(result)

    def process_paper_url(self, url: str, prompt_name: Optional[str] = None, description: Optional[str] = None, mode: str = "prompt", **kwargs):
        result = self.service.analyze_url(url, prompt_name=prompt_name, description=description, **kwargs)
        return self._adapt_result(result)

    def _adapt_result(self, result: dict) -> dict:
        structured = result.get("structured_data") or {}
        analysis = structured.get("analysis") or {}
        return {
            "result": result.get("content", ""),
            "structured_analysis": analysis,
            "structured_data": structured,
            "metadata": result.get("metadata", {}),
            "file_path": result.get("file_path", ""),
            "parsed_document": result.get("parsed_document"),
        }
