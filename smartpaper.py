#!/usr/bin/env python3
"""SmartPaper 主入口 - 新架构

用法:
    python smartpaper.py analyze --file paper.pdf
    python smartpaper.py analyze --url https://arxiv.org/...
    python smartpaper.py stream --file paper.pdf
    python smartpaper.py batch --directory ./papers
    python smartpaper.py prompts
"""

import sys
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from interfaces.cli.paper_cli import main

if __name__ == '__main__':
    main()
