import re
from typing import Dict, List, Optional
from loguru import logger

class SectionSplitter:
    """
    专门用于将论文 Markdown 文本切分为标准章节的工具。
    支持对常见学术论文标题（引言、方法、实验、结论等）的识别。
    """
    
    # 章节映射关键词（正则表达式，支持中英文）
    SECTION_PATTERNS = {
        "abstract": [r"abstract", r"摘要"],
        "introduction": [r"introduction", r"引言", r"背景", r"background"],
        "related_work": [r"related work", r"相关工作"],
        "method": [r"method", r"methodology", r"approach", r"proposed", r"方法", r"方案"],
        "experiments": [r"experiment", r"evaluation", r"implementation", r"实验", r"评估"],
        "results": [r"result", r"discussion", r"结果", r"讨论"],
        "conclusion": [r"conclusion", r"future work", r"结论", r"结语"],
        "references": [r"reference", r"bibliography", r"参考文献"]
    }

    @classmethod
    def split(cls, text: str) -> Dict[str, str]:
        """
        根据 Markdown 标题将文本分割为字典。
        
        Args:
            text: 完整的 Markdown 字符串
            
        Returns:
            Dict: 键为章节名 (abstract, method等)，值为文本内容
        """
        lines = text.split("\n")
        sections = {}
        current_section = "front_matter"
        current_content = []
        
        # 预编译正则提高效率
        patterns = {k: [re.compile(p, re.IGNORECASE) for p in v] for k, v in cls.SECTION_PATTERNS.items()}

        for line in lines:
            # 识别 Markdown 标题 (h1, h2, h3)
            # 匹配如 # Introduction, ## 1. Introduction, # 2 Methodology 等
            header_match = re.match(r"^(#+)\s*(.*)$", line.strip())
            
            if header_match:
                header_text = header_match.group(2).strip()
                # 确定新章节
                found_new = False
                for sec_key, sec_patterns in patterns.items():
                    if any(p.search(header_text) for p in sec_patterns):
                        # 如果已经有该章节，则追加（针对多个Sub-methods情况）
                        if current_section:
                             sections[current_section] = sections.get(current_section, "") + "\n".join(current_content)
                        
                        current_section = sec_key
                        current_content = []
                        found_new = True
                        break
                
                # 如果没找到标准标题，视作上一章节的延续
                if not found_new:
                    current_content.append(line)
            else:
                current_content.append(line)
        
        # 保存最后一个章节
        if current_section:
            sections[current_section] = sections.get(current_section, "") + "\n".join(current_content)
            
        logger.debug(f"文档切分完成，检测到章节: {list(sections.keys())}")
        return sections

    @classmethod
    def get_essential_text(cls, sections: Dict[str, str], max_chars: int = 15000) -> str:
        """
        获取论文的核心部分（忽略参考文献、前言等）用于精简版分析
        """
        essential_keys = ["abstract", "introduction", "method", "experiments", "results", "conclusion"]
        text = ""
        for key in essential_keys:
            if key in sections:
                text += f"\n\n## {key.upper()}\n" + sections[key]
        
        return text[:max_chars]
