"""后台管理 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Optional, List
from loguru import logger

from app.auth.schemas import (
    UserUpdate,
    UserDetailResponse,
    UserListResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
    PermissionCreate,
    PermissionResponse,
    PermissionListResponse,
    StatsResponse,
    BaseResponse,
)
from app.auth.security import get_current_superuser, hash_password, validate_password_strength
from app.auth.dependencies import require_permission
from app.database.models import User, Role, Permission
from app.database.db import get_db

router = APIRouter()


# ==================== 用户管理 ====================

@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜索用户名或邮箱"),
    is_active: Optional[bool] = Query(None, description="筛选活跃用户"),
    current_user: User = Depends(require_permission("user:read")),
    db: AsyncSession = Depends(get_db),
):
    """获取用户列表"""
    try:
        # 构建查询
        query = select(User)

        # 搜索过滤
        if search:
            query = query.where(
                (User.username.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%"))
            )

        # 状态过滤
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(User.created_at.desc())

        # 执行查询
        result = await db.execute(query)
        users = result.scalars().all()

        # 加载角色
        for user in users:
            await db.refresh(user, ["roles"])

        return UserListResponse(
            total=total,
            page=page,
            page_size=page_size,
            users=[UserDetailResponse.model_validate(u) for u in users],
        )

    except Exception as e:
        logger.error(f"获取用户列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败",
        )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:read")),
    db: AsyncSession = Depends(get_db),
):
    """获取用户详情"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        await db.refresh(user, ["roles"])

        return UserDetailResponse.model_validate(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户详情失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户详情失败",
        )


@router.put("/users/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
):
    """更新用户信息"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        # 更新字段
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user, ["roles"])

        logger.info(f"更新用户信息: {user.username}")

        return UserDetailResponse.model_validate(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败",
        )


@router.delete("/users/{user_id}", response_model=BaseResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:delete")),
    db: AsyncSession = Depends(get_db),
):
    """删除用户"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        # 不能删除自己
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除当前用户",
            )

        await db.delete(user)
        await db.commit()

        logger.info(f"删除用户: {user.username}")

        return BaseResponse(success=True, message="用户已删除")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败",
        )


@router.post("/users/{user_id}/activate", response_model=BaseResponse)
async def activate_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
):
    """激活用户"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        user.is_active = True
        await db.commit()

        logger.info(f"激活用户: {user.username}")

        return BaseResponse(success=True, message="用户已激活")

    except Exception as e:
        logger.error(f"激活用户失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="激活用户失败",
        )


@router.post("/users/{user_id}/deactivate", response_model=BaseResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
):
    """停用用户"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        # 不能停用自己
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能停用当前用户",
            )

        user.is_active = False
        await db.commit()

        logger.info(f"停用用户: {user.username}")

        return BaseResponse(success=True, message="用户已停用")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"停用用户失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="停用用户失败",
        )


# ==================== 角色管理 ====================

@router.get("/roles", response_model=RoleListResponse)
async def list_roles(
    current_user: User = Depends(require_permission("user:read")),
    db: AsyncSession = Depends(get_db),
):
    """获取角色列表"""
    try:
        result = await db.execute(select(Role).order_by(Role.created_at))
        roles = result.scalars().all()

        return RoleListResponse(
            total=len(roles),
            roles=[RoleResponse.model_validate(r) for r in roles],
        )

    except Exception as e:
        logger.error(f"获取角色列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色列表失败",
        )


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    current_user: User = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
):
    """创建角色"""
    try:
        # 检查角色名是否已存在
        result = await db.execute(select(Role).where(Role.name == role_in.name))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名已存在",
            )

        # 创建角色
        role = Role(
            name=role_in.name,
            description=role_in.description,
            is_active=role_in.is_active,
        )

        db.add(role)
        await db.commit()
        await db.refresh(role)

        # 添加权限
        if role_in.permission_ids:
            for perm_id in role_in.permission_ids:
                result = await db.execute(select(Permission).where(Permission.id == perm_id))
                perm = result.scalar_one_or_none()
                if perm:
                    role.permissions.append(perm)

            await db.commit()
            await db.refresh(role)

        logger.info(f"创建角色: {role.name}")

        return RoleResponse.model_validate(role)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建角色失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建角色失败",
        )


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    current_user: User = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
):
    """更新角色"""
    try:
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在",
            )

        # 更新字段
        update_data = role_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)

        await db.commit()
        await db.refresh(role)

        logger.info(f"更新角色: {role.name}")

        return RoleResponse.model_validate(role)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新角色失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新角色失败",
        )


@router.delete("/roles/{role_id}", response_model=BaseResponse)
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_permission("user:delete")),
    db: AsyncSession = Depends(get_db),
):
    """删除角色"""
    try:
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在",
            )

        await db.delete(role)
        await db.commit()

        logger.info(f"删除角色: {role.name}")

        return BaseResponse(success=True, message="角色已删除")

    except Exception as e:
        logger.error(f"删除角色失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除角色失败",
        )


@router.post("/roles/{role_id}/permissions/{permission_id}", response_model=BaseResponse)
async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    current_user: User = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
):
    """为角色分配权限"""
    try:
        # 查找角色
        role_result = await db.execute(select(Role).where(Role.id == role_id))
        role = role_result.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在",
            )

        # 查找权限
        perm_result = await db.execute(select(Permission).where(Permission.id == permission_id))
        perm = perm_result.scalar_one_or_none()

        if not perm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="权限不存在",
            )

        # 检查是否已分配
        if perm in role.permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该角色已拥有此权限",
            )

        # 分配权限
        role.permissions.append(perm)
        await db.commit()

        logger.info(f"为角色 {role.name} 分配权限 {perm.name}")

        return BaseResponse(success=True, message="权限分配成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分配权限失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分配权限失败",
        )


@router.delete("/roles/{role_id}/permissions/{permission_id}", response_model=BaseResponse)
async def revoke_permission_from_role(
    role_id: int,
    permission_id: int,
    current_user: User = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
):
    """撤销角色权限"""
    try:
        # 查找角色
        role_result = await db.execute(select(Role).where(Role.id == role_id))
        role = role_result.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在",
            )

        # 查找权限
        perm_result = await db.execute(select(Permission).where(Permission.id == permission_id))
        perm = perm_result.scalar_one_or_none()

        if not perm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="权限不存在",
            )

        # 检查是否拥有权限
        if perm not in role.permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该角色未拥有此权限",
            )

        # 撤销权限
        role.permissions.remove(perm)
        await db.commit()

        logger.info(f"撤销角色 {role.name} 的权限 {perm.name}")

        return BaseResponse(success=True, message="权限撤销成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"撤销权限失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="撤销权限失败",
        )


# ==================== 权限管理 ====================

@router.get("/permissions", response_model=PermissionListResponse)
async def list_permissions(
    current_user: User = Depends(require_permission("user:read")),
    db: AsyncSession = Depends(get_db),
):
    """获取权限列表"""
    try:
        result = await db.execute(
            select(Permission).order_by(Permission.resource, Permission.action)
        )
        permissions = result.scalars().all()

        return PermissionListResponse(
            total=len(permissions),
            permissions=[PermissionResponse.model_validate(p) for p in permissions],
        )

    except Exception as e:
        logger.error(f"获取权限列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取权限列表失败",
        )


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    perm_in: PermissionCreate,
    current_user: User = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
):
    """创建权限"""
    try:
        # 检查权限名是否已存在
        result = await db.execute(select(Permission).where(Permission.name == perm_in.name))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="权限名已存在",
            )

        # 创建权限
        permission = Permission(
            name=perm_in.name,
            description=perm_in.description,
            resource=perm_in.resource,
            action=perm_in.action,
        )

        db.add(permission)
        await db.commit()
        await db.refresh(permission)

        logger.info(f"创建权限: {permission.name}")

        return PermissionResponse.model_validate(permission)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建权限失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建权限失败",
        )


# ==================== 用户角色分配 ====================

@router.post("/users/{user_id}/roles/{role_id}", response_model=BaseResponse)
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
):
    """为用户分配角色"""
    try:
        # 查找用户
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        # 查找角色
        role_result = await db.execute(select(Role).where(Role.id == role_id))
        role = role_result.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在",
            )

        # 检查是否已分配
        if role in user.roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户已拥有此角色",
            )

        # 分配角色
        user.roles.append(role)
        await db.commit()

        logger.info(f"为用户 {user.username} 分配角色 {role.name}")

        return BaseResponse(success=True, message="角色分配成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分配角色失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分配角色失败",
        )


@router.delete("/users/{user_id}/roles/{role_id}", response_model=BaseResponse)
async def revoke_role_from_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
):
    """撤销用户角色"""
    try:
        # 查找用户
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        # 查找角色
        role_result = await db.execute(select(Role).where(Role.id == role_id))
        role = role_result.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在",
            )

        # 检查是否拥有角色
        if role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户未拥有此角色",
            )

        # 撤销角色
        user.roles.remove(role)
        await db.commit()

        logger.info(f"撤销用户 {user.username} 的角色 {role.name}")

        return BaseResponse(success=True, message="角色撤销成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"撤销角色失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="撤销角色失败",
        )


# ==================== 系统统计 ====================

@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(require_permission("system:stats")),
    db: AsyncSession = Depends(get_db),
):
    """获取系统统计数据"""
    try:
        # 统计用户总数
        users_count_result = await db.execute(select(func.count(User.id)))
        total_users = users_count_result.scalar()

        # 统计活跃用户数
        active_users_count_result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_users_count_result.scalar()

        # 统计角色数
        roles_count_result = await db.execute(select(func.count(Role.id)))
        total_roles = roles_count_result.scalar()

        # 统计权限数
        perms_count_result = await db.execute(select(func.count(Permission.id)))
        total_permissions = perms_count_result.scalar()

        # 论文统计（暂时返回0，后续实现）
        total_papers = 0

        return StatsResponse(
            total_users=total_users,
            active_users=active_users,
            total_papers=total_papers,
            total_roles=total_roles,
            total_permissions=total_permissions,
        )

    except Exception as e:
        logger.error(f"获取统计数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计数据失败",
        )
