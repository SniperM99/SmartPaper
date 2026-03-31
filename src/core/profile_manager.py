import yaml
import os
from typing import Dict, List, Any, Optional
from loguru import logger

class ProfileManager:
    """管理用户科研画像与个人化配置"""

    def __init__(self, config_path: str = "config/user_profile.yaml"):
        """初始化画像管理器
        
        Args:
            config_path: 配置文件路径
        """
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_path = os.path.join(root_dir, config_path)
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"加载用户画像失败: {e}")
                return {}
        return {}

    def get_context_string(self) -> str:
        """获取简化的科研背景描述字符串，用于注入 Prompt"""
        ctx = self.profile.get("user_context", {})
        interests = self.profile.get("interests", [])
        
        context_str = f"用户背景: {ctx.get('role', 'Researcher')}，研究方向为 {ctx.get('research_area', 'General Science')}。\n"
        context_str += f"当前课题: {ctx.get('current_project', 'N/A')}\n"
        context_str += f"关注关键词: {', '.join(interests)}\n"
        return context_str

    def get_analysis_focus(self) -> List[str]:
        """获取分析侧重点列表"""
        return self.profile.get("analysis_focus", [])

    def update_profile(self, new_profile: Dict):
        """更新并保存画像"""
        self.profile = new_profile
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.profile, f, allow_unicode=True, default_flow_style=False)
            logger.info("用户画像已更新")
        except Exception as e:
            logger.error(f"保存用户画像失败: {e}")

    def get_all(self) -> Dict:
        """获取完整画像"""
        return self.profile
