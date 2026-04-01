"""科研画像服务"""
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger

from application.workbench_service import WorkbenchService
from src.core.config_loader import load_config


class ProfileService:
    """科研画像服务"""

    def __init__(self):
        """初始化服务"""
        self.config = load_config()
        self.workbench_service = WorkbenchService(self.config)

    def get_profile(self) -> Dict[str, Any]:
        """获取科研画像

        Returns:
            科研画像数据
        """
        try:
            profile = self.workbench_service.get_profile()

            return {
                "user_context": profile.get("user_context", {}),
                "interests": profile.get("interests", []),
                "analysis_focus": profile.get("analysis_focus", []),
                "updated_at": profile.get("updated_at", datetime.now().isoformat()),
            }

        except Exception as e:
            logger.error(f"获取科研画像失败: {e}", exc_info=True)
            return {
                "user_context": {},
                "interests": [],
                "analysis_focus": [],
                "error": str(e),
            }

    def update_profile(
        self,
        role: str = None,
        research_area: str = None,
        current_project: str = None,
        interests: List[str] = None,
        analysis_focus: List[str] = None,
    ) -> Dict[str, Any]:
        """更新科研画像

        Args:
            role: 身份/角色
            research_area: 研究领域
            current_project: 当前课题
            interests: 关注关键词
            analysis_focus: 分析侧重

        Returns:
            更新结果
        """
        try:
            # 获取当前画像
            profile = self.workbench_service.get_profile()

            # 更新用户上下文
            user_context = profile.get("user_context", {})
            if role:
                user_context["role"] = role
            if research_area:
                user_context["research_area"] = research_area
            if current_project:
                user_context["current_project"] = current_project

            profile["user_context"] = user_context

            # 更新其他字段
            if interests is not None:
                profile["interests"] = interests
            if analysis_focus is not None:
                profile["analysis_focus"] = analysis_focus

            profile["updated_at"] = datetime.now().isoformat()

            # 保存画像
            self.workbench_service.update_profile(profile)

            logger.info("科研画像已更新")

            return {
                "success": True,
                "message": "科研画像已更新",
                "profile": profile,
            }

        except Exception as e:
            logger.error(f"更新科研画像失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"更新失败: {str(e)}",
                "profile": None,
            }

    def get_analysis_options(self) -> Dict[str, Any]:
        """获取分析选项

        Returns:
            分析选项配置
        """
        try:
            from src.core.prompt_manager import get_available_options

            options = get_available_options()

            return {
                "roles": options.get("roles", {}),
                "domains": options.get("domains", {}),
                "tasks": options.get("tasks", {}),
                "prompts": options.get("prompts", {}),
            }

        except Exception as e:
            logger.error(f"获取分析选项失败: {e}", exc_info=True)
            return {
                "roles": {},
                "domains": {},
                "tasks": {},
                "prompts": {},
                "error": str(e),
            }
