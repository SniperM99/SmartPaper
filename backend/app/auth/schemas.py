"""认证和授权数据模型"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool
    message: str


class UserCreate(BaseModel):
    """用户创建模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, max_length=100, description="密码")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    bio: Optional[str] = Field(None, description="个人简介")

    @validator("username")
    def validate_username(cls, v):
        if not v.isalnum() and "_" not in v:
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户更新模型"""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class RoleUpdate(BaseModel):
    """角色更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleCreate(BaseModel):
    """角色创建模型"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    is_active: bool = True
    permission_ids: Optional[List[int]] = Field([], description="权限ID列表")


class PermissionCreate(BaseModel):
    """权限创建模型"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    resource: Optional[str] = Field(None, max_length=50)
    action: Optional[str] = Field(None, max_length=50)


class RoleResponse(BaseModel):
    """角色响应模型"""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    """权限响应模型"""
    id: int
    name: str
    description: Optional[str]
    resource: Optional[str]
    action: Optional[str]

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """用户详情响应模型"""
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenPayload(BaseModel):
    """令牌载荷模型"""
    sub: Optional[int] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class TokenRefresh(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str


class PasswordChange(BaseModel):
    """修改密码模型"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordReset(BaseModel):
    """重置密码模型"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    total: int
    page: int
    page_size: int
    users: List[UserDetailResponse]


class RoleListResponse(BaseModel):
    """角色列表响应模型"""
    total: int
    roles: List[RoleResponse]


class PermissionListResponse(BaseModel):
    """权限列表响应模型"""
    total: int
    permissions: List[PermissionResponse]


class StatsResponse(BaseModel):
    """统计响应模型"""
    total_users: int
    active_users: int
    total_papers: int
    total_roles: int
    total_permissions: int
