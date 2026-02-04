import argparse
import sys
import os
from loguru import logger
from typing import Optional

# 添加src目录到搜索路径
sys.path.append(os.path.join(os.getcwd(), "src"))

from core.smart_paper_core import SmartPaper
from core.prompt_manager import list_prompts

# 配置日志
logger.remove()
logger.add(sys.stderr, level="INFO")

def main():
    parser = argparse.ArgumentParser(description="Recursively analyze all PDF papers in a directory.")
    parser.add_argument("directory", help="Directory path containing PDFs")
    parser.add_argument(
        "--prompt", "-p", default="phd_analysis", choices=list_prompts().keys(), help="Prompt template name"
    )
    
    args = parser.parse_args()

    # 检查目录是否存在
    if not os.path.exists(args.directory):
        logger.error(f"Directory not found: {args.directory}")
        return

    try:
        reader = SmartPaper()
        
        logger.info(f"Starting batch analysis in: {args.directory}")
        logger.info(f"Using prompt template: {args.prompt}")
        
        # 调用 SmartPaper 的递归目录处理方法
        results = reader.process_directory(args.directory, prompt_name=args.prompt)
        
        logger.info(f"Batch processing complete. Analyzed {len(results)} papers.")
             
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")

if __name__ == "__main__":
    main()
