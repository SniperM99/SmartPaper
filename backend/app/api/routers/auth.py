"""认证 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from datetime import datetime, timedelta

from app.auth.schemas import (
    UserCreate,
    UserLogin,
    Token,
    TokenRefresh,
    PasswordChange,
    UserResponse,
    BaseResponse,
)
from app.auth.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    validate_password_strength,
    get_current_active_user,
)
from app.database.models import User
from app.database.db import get_db
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        result = await db.execute(select(User).where(User.username == user_in.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在",
            )

        # 检查邮箱是否已存在
        result = await db.execute(select(User).where(User.email == user_in.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册",
            )

        # 验证密码强度
        is_valid, message = validate_password_strength(user_in.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        # 创建用户
        user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            full_name=user_in.full_name,
            bio=user_in.bio,
            is_active=True,
            is_verified=False,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"新用户注册: {user.username} ({user.email})")

        # 生成令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户注册失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试",
        )


@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """用户登录"""
    try:
        # 查找用户（用户名或邮箱）
        result = await db.execute(
            select(User).where(
                (User.username == user_in.username) | (User.email == user_in.username)
            )
        )
        user = result.scalar_one_or_none()

        # 验证用户是否存在
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )

        # 验证密码
        if not verify_password(user_in.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )

        # 检查用户是否被禁用
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用",
            )

        # 更新最后登录信息
        user.last_login = datetime.utcnow()
        client_host = request.client.host
        if client_host:
            user.last_login_ip = client_host

        await db.commit()

        logger.info(f"用户登录: {user.username} from {client_host}")

        # 生成令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试",
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_in: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    """刷新访问令牌"""
    from app.auth.security import decode_token

    try:
        # 验证刷新令牌
        payload = decode_token(token_in.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌类型",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
            )

        # 查找用户
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用",
            )

        # 生成新令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新令牌失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌刷新失败",
        )


@router.post("/logout", response_model=BaseResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """用户登出"""
    # 如果使用 Redis 存储 token 黑名单，可以在这里添加
    return BaseResponse(success=True, message="登出成功")


@router.post("/change-password", response_model=BaseResponse)
async def change_password(
    password_in: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """修改密码"""
    try:
        # 验证旧密码
        if not verify_password(password_in.old_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误",
            )

        # 验证新密码强度
        is_valid, message = validate_password_strength(password_in.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        # 更新密码
        current_user.hashed_password = hash_password(password_in.new_password)
        await db.commit()

        logger.info(f"用户修改密码: {current_user.username}")

        return BaseResponse(success=True, message="密码修改成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码修改失败",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user)
