"""数据库模型"""
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Table,
    func,
)
from sqlalchemy.orm import relationship
from app.database.db import Base

# 用户-角色关联表（多对多）
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# 角色-权限关联表（多对多）
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # 用户信息
    full_name = Column(String(100))
    avatar_url = Column(String(255))
    bio = Column(Text)

    # 用户状态
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    last_login_ip = Column(String(50))

    # 关系
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    papers = relationship("Paper", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Role(Base):
    """角色模型"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class Permission(Base):
    """权限模型"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255))
    resource = Column(String(50))  # 资源类型：user, paper, system 等
    action = Column(String(50))    # 操作类型：read, write, delete 等

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}')>"


class Paper(Base):
    """论文模型"""
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 论文信息
    title = Column(String(500))
    arxiv_id = Column(String(50))
    file_path = Column(String(500))
    file_size = Column(Integer)

    # 解析结果
    parsed_content = Column(Text)  # JSON 字符串
    analysis_result = Column(Text)  # JSON 字符串

    # 状态
    status = Column(String(20), default="pending")  # pending, processing, completed, failed

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    analyzed_at = Column(DateTime(timezone=True))

    # 关系
    owner = relationship("User", back_populates="papers")

    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class UserRole(Base):
    """用户角色关联模型（可选，用于记录分配时间）"""
    __tablename__ = "user_roles_extra"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(Integer, ForeignKey("users.id"))


class RolePermission(Base):
    """角色权限关联模型（可选）"""
    __tablename__ = "role_permissions_extra"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"))
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"))
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    granted_by = Column(Integer, ForeignKey("users.id"))


class AuditLog(Base):
    """审计日志模型"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(Text)  # JSON 字符串
    ip_address = Column(String(50))
    user_agent = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
