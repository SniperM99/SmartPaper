"""认证和授权依赖"""
from typing import Callable
from functools import wraps
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import (
    get_current_active_user,
    check_user_permission,
    check_user_role,
)
from app.database.models import User
from app.database.db import get_db


def require_permission(permission_name: str):
    """权限验证依赖"""
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        has_permission = await check_user_permission(current_user, permission_name, db)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {permission_name}",
            )
        return current_user

    return permission_checker


def require_role(role_name: str):
    """角色验证依赖"""
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        has_role = await check_user_role(current_user, role_name, db)
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少角色: {role_name}",
            )
        return current_user

    return role_checker


def require_permissions(*permission_names: str):
    """多权限验证装饰器（需要所有权限）"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取 current_user
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证",
                )

            db = kwargs.get("db")
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据库会话未提供",
                )

            # 检查所有权限
            for perm in permission_names:
                has_perm = await check_user_permission(current_user, perm, db)
                if not has_perm:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"缺少权限: {perm}",
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_role(*role_names: str):
    """任意角色验证装饰器（满足任一角色即可）"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取 current_user
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证",
                )

            db = kwargs.get("db")
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据库会话未提供",
                )

            # 检查是否有任一角色
            has_any_role = False
            for role in role_names:
                has_role = await check_user_role(current_user, role, db)
                if has_role:
                    has_any_role = True
                    break

            if not has_any_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少任一角色: {', '.join(role_names)}",
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
