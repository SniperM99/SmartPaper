import os
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from loguru import logger

def load_config(config_dir: str = "config", env: Optional[str] = None) -> Dict[str, Any]:
    """加载多层配置文件并合并环境变量
    
    加载顺序:
    1. base.yaml (基础配置)
    2. {env}.yaml (环境特定配置, 如 dev, prod)
    3. .env (环境变量覆盖)
    
    Args:
        config_dir: 配置文件目录
        env: 环境名称 (如果为 None，则尝试从 ENV 环境变量读取)
    
    Returns:
        最终合并后的配置字典
    """
    # 1. 加载 .env
    load_dotenv()
    
    # 2. 确定环境
    if env is None:
        env = os.getenv("APP_ENV", "dev")
    
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    abs_config_dir = os.path.join(root_dir, config_dir)
    
    # 3. 加载 base.yaml
    config = {}
    base_path = os.path.join(abs_config_dir, "config.yaml") # 暂时保持原名作为 base
    if os.path.exists(base_path):
        with open(base_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    
    # 4. 加载环境特定配置 (可选)
    env_path = os.path.join(abs_config_dir, f"{env}.yaml")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            env_config = yaml.safe_load(f) or {}
            config = merge_dicts(config, env_config)
    
    # 5. 环境变量覆盖
    # 约定: SP_LLM__OPENAI__API_KEY -> config['llm']['openai']['api_key']
    config = override_from_env(config, "SP")
    
    return config

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """递归合并两个字典"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def override_from_env(config: Dict, prefix: str) -> Dict:
    """从环境变量中提取配置并覆盖"""
    for env_key, env_val in os.environ.items():
        if env_key.startswith(f"{prefix}_"):
            # SP_LLM__OPENAI__API_KEY -> ['LLM', 'OPENAI', 'API_KEY']
            keys = env_key[len(prefix)+1:].lower().split("__")
            
            # 深入字典进行修改
            curr = config
            for i, key in enumerate(keys):
                if i == len(keys) - 1:
                    curr[key] = env_val
                else:
                    if key not in curr or not isinstance(curr[key], dict):
                        curr[key] = {}
                    curr = curr[key]
    return config
