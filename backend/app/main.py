"""SmartPaper FastAPI 主应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.database.db import db
from app.auth.middleware import add_rate_limiting, log_requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("🚀 SmartPaper FastAPI 服务启动中...")
    logger.info(f"📝 环境配置: {settings.ENV}")
    logger.info(f"🌐 监听地址: {settings.HOST}:{settings.PORT}")

    # 初始化数据库
    if settings.ENV == "development":
        logger.info("初始化数据库...")
        await db.init_db()

    yield

    # 关闭
    logger.info("👋 SmartPaper FastAPI 服务关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="SmartPaper API",
    description="智能论文分析平台后端服务",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求日志
log_requests(app)

# 添加速率限制
add_rate_limiting(app)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"全局异常捕获: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.ENV == "development" else None,
        },
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "success": True,
        "service": "SmartPaper API",
        "status": "healthy",
        "version": "1.0.0",
    }


# 注册路由
app.include_router(api_router, prefix="/api")


# 启动事件
@app.on_event("startup")
async def startup_event():
    setup_logging()
    logger.info("✅ 服务启动完成")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENV == "development",
        log_level="info",
    )
