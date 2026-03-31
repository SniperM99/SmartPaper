import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger
from domain.models import AnalysisTask, AnalysisStatus

class TaskManager:
    """
    任务管理器：负责批量任务的状态持久化、断点续存和统计分析。
    """
    
    def __init__(self, storage_path: str = "tasks.json"):
        self.storage_path = storage_path
        self.tasks: Dict[str, Dict[str, Any]] = self._load_tasks()

    def _load_tasks(self) -> Dict[str, Dict[str, Any]]:
        """从文件加载任务状态"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载任务文件失败: {e}")
        return {}

    def save_tasks(self):
        """保存任务状态到文件"""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存任务文件失败: {e}")

    def get_or_create_task(self, source: str, prompt_name: str) -> Dict[str, Any]:
        """获取现有任务或创建新任务标识"""
        task_key = f"{source}_{prompt_name}"
        if task_key not in self.tasks:
            self.tasks[task_key] = {
                "source": source,
                "prompt_name": prompt_name,
                "status": AnalysisStatus.PENDING.value,
                "created_at": datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
                "output_path": "",
                "error_message": None,
                "metrics": {
                    "token_usage": 0,
                    "duration": 0
                }
            }
            self.save_tasks()
        return self.tasks[task_key]

    def update_task_status(self, source: str, prompt_name: str, status: AnalysisStatus, **kwargs):
        """更新任务状态及其它元数据"""
        task_key = f"{source}_{prompt_name}"
        if task_key in self.tasks:
            task = self.tasks[task_key]
            task["status"] = status.value
            
            if status == AnalysisStatus.PARSING:
                task["started_at"] = datetime.now().isoformat()
            elif status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]:
                task["completed_at"] = datetime.now().isoformat()
                if task["started_at"]:
                    start = datetime.fromisoformat(task["started_at"])
                    end = datetime.fromisoformat(task["completed_at"])
                    task["metrics"]["duration"] = (end - start).total_seconds()

            # 更新其他可选属性
            for key, value in kwargs.items():
                if key == "metrics":
                    task["metrics"].update(value)
                else:
                    task[key] = value
            
            self.save_tasks()

    def is_completed(self, source: str, prompt_name: str) -> bool:
        """检查任务是否已完成 (用于断点续跑)"""
        task_key = f"{source}_{prompt_name}"
        return self.tasks.get(task_key, {}).get("status") == AnalysisStatus.COMPLETED.value

    def get_batch_stats(self) -> Dict[str, Any]:
        """计算当前所有任务的统计信息"""
        stats = {
            "total": len(self.tasks),
            "completed": 0,
            "failed": 0,
            "pending": 0,
            "total_duration": 0.0,
            "total_tokens": 0,
            "status_distribution": {}
        }
        
        for task in self.tasks.values():
            status = task["status"]
            stats["status_distribution"][status] = stats["status_distribution"].get(status, 0) + 1
            
            if status == AnalysisStatus.COMPLETED.value:
                stats["completed"] += 1
                stats["total_duration"] += task["metrics"].get("duration", 0)
                stats["total_tokens"] += task["metrics"].get("token_usage", 0)
            elif status == AnalysisStatus.FAILED.value:
                stats["failed"] += 1
            else:
                stats["pending"] += 1
                
        return stats

    def reset_failed_tasks(self):
        """重置所有失败的任务为 PENDING，以便重新运行"""
        for task in self.tasks.values():
            if task["status"] == AnalysisStatus.FAILED.value:
                task["status"] = AnalysisStatus.PENDING.value
                task["error_message"] = None
        self.save_tasks()
