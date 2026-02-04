import argparse
import sys
import os
import time
from loguru import logger
from typing import Optional

# 添加src目录到搜索路径
sys.path.append(os.path.join(os.getcwd(), "src"))

from core.history_manager import HistoryManager

# 配置日志
logger.remove()
logger.add(sys.stderr, level="INFO")

def format_timestamp(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

def main():
    parser = argparse.ArgumentParser(description="List history of analyzed papers.")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Number of records to show")
    
    args = parser.parse_args()

    try:
        history_manager = HistoryManager()
        history = history_manager.list_history()
        
        if not history:
            print("No history found.")
            return

        print(f"\nFound {len(history)} records. Showing last {min(len(history), args.limit)}:\n")
        
        # 简单的表格打印
        header_format = "{:<5} {:<20} {:<15} {:<40}"
        print(header_format.format("ID", "Date", "Prompt", "Source"))
        print("-" * 85)
        
        for idx, entry in enumerate(history[:args.limit], 1):
            source = entry['original_source']
            # 如果是本地文件，只显示文件名
            if os.path.exists(source) or "/" in source:
                 source = os.path.basename(source)
            if len(source) > 38:
                source = source[:35] + "..."
            
            print(header_format.format(
                idx,
                format_timestamp(entry['timestamp']),
                entry['prompt_name'],
                source
            ))
            
        print("\nUse 'python cli_get_prompt_mode_paper.py [source]' to view full analysis (cached).")

    except Exception as e:
        logger.error(f"Failed to list history: {str(e)}")

if __name__ == "__main__":
    main()
