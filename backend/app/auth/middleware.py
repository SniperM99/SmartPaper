"""认证中间件"""
from fastapi import Request, HTTPException, status
from fastapi.middleware import Middleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from loguru import logger
from typing import Callable


# 创建限流器实例
limiter = Limiter(key_func=get_remote_address)


def rate_limit(limit: str):
    """速率限制装饰器"""
    return limiter.limit(limit)


def add_rate_limiting(app):
    """添加速率限制中间件"""
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)


def log_requests(app):
    """添加请求日志中间件"""
    @app.middleware("http")
    async def log_request_middleware(request: Request, call_next):
        # 记录请求
        logger.info(f"请求: {request.method} {request.url.path} from {request.client.host}")

        # 处理请求
        response = await call_next(request)

        # 记录响应状态
        logger.info(f"响应: {response.status_code}")

        return response


def security_headers(app):
    """添加安全头中间件"""
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)

        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
