"""应用配置管理"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path
import sys


class Settings(BaseSettings):
    """应用设置"""

    # 应用基础配置
    APP_NAME: str = "SmartPaper API"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"  # development, production
    DEBUG: bool = True

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS 配置
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:8080"

    @property
    def ALLOWED_ORIGINS_LIST(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # 文件存储配置
    UPLOAD_DIR: Path = Path(__file__).parent.parent.parent / "temp"
    OUTPUT_DIR: Path = Path(__file__).parent.parent.parent / "outputs"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB

    # LLM 配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"

    ZHIPUAI_API_KEY: Optional[str] = None
    ZHIPUAI_MODEL: str = "glm-4"

    # Zotero 配置
    ZOTERO_API_KEY: Optional[str] = None
    ZOTERO_USER_ID: Optional[str] = None
    ZOTERO_API_URL: str = "https://api.zotero.org"

    # JWT 配置
    SECRET_KEY: str = "smartpaper-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 数据库配置（预留）
    DATABASE_URL: Optional[str] = None

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path(__file__).parent.parent.parent / "logs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保目录存在
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)


# 创建全局设置实例
settings = Settings()
