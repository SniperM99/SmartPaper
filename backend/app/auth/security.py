"""认证和授权安全工具"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.models import User
from app.database.db import get_db

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 认证
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"无效的令牌: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """获取当前用户"""
    token = credentials.credentials

    try:
        payload = decode_token(token)

        # 验证令牌类型
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌类型",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌载荷",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌验证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """获取当前超级用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级用户权限",
        )
    return current_user


def validate_password_strength(password: str) -> tuple[bool, str]:
    """验证密码强度"""
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"密码长度至少需要 {settings.PASSWORD_MIN_LENGTH} 位"

    if settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "密码必须包含大写字母"

    if settings.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "密码必须包含小写字母"

    if settings.PASSWORD_REQUIRE_DIGITS and not any(c.isdigit() for c in password):
        return False, "密码必须包含数字"

    if settings.PASSWORD_REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "密码必须包含特殊字符"

    return True, ""


async def check_user_permission(user: User, permission_name: str, db: AsyncSession) -> bool:
    """检查用户是否具有指定权限"""
    # 超级用户拥有所有权限
    if user.is_superuser:
        return True

    # 检查用户的角色是否具有该权限
    from sqlalchemy import select
    from app.database.models import Permission, Role

    result = await db.execute(
        select(Permission)
        .join(Role, Permission.roles)
        .join(User, Role.users)
        .where(User.id == user.id)
        .where(Permission.name == permission_name)
    )

    return result.scalar_one_or_none() is not None


async def check_user_role(user: User, role_name: str, db: AsyncSession) -> bool:
    """检查用户是否具有指定角色"""
    # 超级用户拥有所有角色
    if user.is_superuser:
        return True

    from sqlalchemy import select
    from app.database.models import Role

    result = await db.execute(
        select(Role).join(User.roles).where(User.id == user.id).where(Role.name == role_name)
    )

    return result.scalar_one_or_none() is not None
