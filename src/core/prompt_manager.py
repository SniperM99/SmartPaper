import os
from typing import Dict, Union, Optional, List
import yaml
from loguru import logger

class PromptLibrary:
    def __init__(self, prompt_file: Optional[str] = None):
        """初始化提示词库"""
        if prompt_file is None:
            # 获取项目根目录的绝对路径
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.prompt_file = os.path.join(root_dir, "config", "prompts_llm.yaml")
        else:
            self.prompt_file = prompt_file

        self.config = self._load_config()
        self.roles = self.config.get("roles", {})
        self.tasks = self.config.get("tasks", {})
        self.domains = self.config.get("domains", {})
        self.personalization = self.config.get("personalization", {})
        self.prompts = self.config.get("prompts", {})
        self.version = self.config.get("version", "unknown")
        
        logger.info(f"成功加载提示词库 {self.version}: {len(self.roles)} 角色, {len(self.tasks)} 任务, {len(self.domains)} 领域, {len(self.personalization)} 个性化项, {len(self.prompts)} 预设")

    def _load_config(self) -> Dict:
        """加载提示词配置"""
        try:
            with open(self.prompt_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise Exception(f"加载提示词配置失败: {str(e)}")

    def get_role(self, name: str) -> str:
        """获取角色模板"""
        return self.roles.get(name, {}).get("template", "")

    def get_task(self, name: str) -> str:
        """获取任务模板"""
        return self.tasks.get(name, {}).get("template", "")

    def get_domain(self, name: str) -> str:
        """获取领域模板"""
        return self.domains.get(name, {}).get("template", "")

    def get_personalization(self, name: str = "user_context") -> str:
        """获取个性化模板"""
        return self.personalization.get(name, "")

    def get_prompt(self, prompt_name: str) -> str:
        """获取指定名称的预设提示词模板"""
        if prompt_name in self.prompts:
            return self.prompts[prompt_name]["template"]
        # 如果没找到预设，尝试作为任务处理
        if prompt_name in self.tasks:
            return self.tasks[prompt_name]["template"]
        raise ValueError(f"未找到名为 '{prompt_name}' 的提示词模板")

    def compose_prompt(self, role: str = "general_assistant", task: str = "summarization", domain: str = "general", text: str = "", user_context_str: str = "", user_focus_list: List[str] = None) -> str:
        """组合角色、任务和领域生成提示词"""
        role_p = self.get_role(role) or self.get_role("general_assistant")
        task_p = self.get_task(task) or self.get_task("summarization")
        domain_p = self.get_domain(domain) or ""
        
        # 处理个性化
        user_p = ""
        if user_context_str or user_focus_list:
            focus_str = "\n".join([f"- {f}" for f in user_focus_list]) if user_focus_list else "无特定侧重"
            user_p = self.get_personalization("user_context").format(
                user_context_str=user_context_str,
                user_focus_list=focus_str
            )
        
        # 使用 composite_analysis 作为基座
        try:
            base_template = self.get_prompt("composite_analysis")
        except ValueError:
            # 回退到简单拼接，如果预设模板丢失
            base_template = "{user_personalization}\n\n{role_prompt}\n\n{domain_prompt}\n\n{task_prompt}\n\n{text}"
        
        return base_template.format(
            user_personalization=user_p,
            role_prompt=role_p,
            domain_prompt=domain_p,
            task_prompt=task_p,
            text=text
        )

    def get_available_options(self) -> Dict[str, Dict[str, str]]:
        """列出所有可用的选项"""
        return {
            "roles": {name: info["description"] for name, info in self.roles.items()},
            "tasks": {name: info["description"] for name, info in self.tasks.items()},
            "domains": {name: info["description"] for name, info in self.domains.items()},
            "prompts": {name: info["description"] for name, info in self.prompts.items()}
        }

    def reload(self):
        """重新加载提示词配置"""
        self.config = self._load_config()
        self.roles = self.config.get("roles", {})
        self.tasks = self.config.get("tasks", {})
        self.domains = self.config.get("domains", {})
        self.personalization = self.config.get("personalization", {})
        self.prompts = self.config.get("prompts", {})


# 创建全局实例
_prompt_library = PromptLibrary()


# 导出便捷函数
def get_prompt(prompt_name: str) -> str:
    """获取指定名称的提示词模板"""
    return _prompt_library.get_prompt(prompt_name)

def compose_prompt(role: str = "general_assistant", task: str = "summarization", domain: str = "general", text: str = "", user_context_str: str = "", user_focus_list: list = None) -> str:
    """组合角色、任务和领域生成提示词"""
    return _prompt_library.compose_prompt(role, task, domain, text, user_context_str, user_focus_list)

def get_available_options() -> Dict[str, Dict[str, str]]:
    """列出所有可用的选项（角色、任务、领域、预设）"""
    return _prompt_library.get_available_options()

def get_available_prompts() -> Dict[str, str]:
    """保持兼容性：列出所有可用的预设提示词"""
    return {name: info["description"] for name, info in _prompt_library.prompts.items()}

def reload_prompts():
    """重新加载提示词配置"""
    _prompt_library.reload()
