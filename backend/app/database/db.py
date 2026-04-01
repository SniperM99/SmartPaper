"""数据库配置和连接管理"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from loguru import logger

from app.core.config import settings

# 创建异步引擎（如果 DATABASE_URL 为 None，使用默认 SQLite）
db_url = settings.DATABASE_URL or "sqlite+aiosqlite:///./smartpaper.db"
engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    future=True,
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 创建基类
Base = declarative_base()


class Database:
    """数据库管理类"""

    def __init__(self):
        self.engine = engine
        self.session_maker = async_session_maker

    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        async with self.session_maker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"数据库会话错误: {e}", exc_info=True)
                raise
            finally:
                await session.close()

    async def create_tables(self):
        """创建所有表"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建完成")

    async def drop_tables(self):
        """删除所有表（仅用于开发/测试）"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("数据库表已删除")

    async def init_db(self):
        """初始化数据库，创建表和默认数据"""
        await self.create_tables()
        await self._create_default_roles()
        await self._create_default_permissions()
        await self._create_default_admin()
        logger.info("数据库初始化完成")

    async def _create_default_roles(self):
        """创建默认角色"""
        from app.database.models import Role
        from sqlalchemy import select

        async with self.session_maker() as session:
            # 检查是否已存在
            result = await session.execute(select(Role).where(Role.name == "admin"))
            if result.scalar_one_or_none():
                return

            # 创建默认角色
            roles = [
                Role(name="admin", description="系统管理员", is_active=True),
                Role(name="user", description="普通用户", is_active=True),
                Role(name="guest", description="访客", is_active=True),
            ]

            for role in roles:
                session.add(role)

            await session.commit()
            logger.info("默认角色创建完成")

    async def _create_default_permissions(self):
        """创建默认权限"""
        from app.database.models import Permission
        from sqlalchemy import select

        async with self.session_maker() as session:
            # 检查是否已存在
            result = await session.execute(
                select(Permission).where(Permission.name == "user:read")
            )
            if result.scalar_one_or_none():
                return

            # 创建默认权限
            permissions = [
                # 用户权限
                Permission(name="user:read", description="查看用户信息"),
                Permission(name="user:write", description="修改用户信息"),
                Permission(name="user:delete", description="删除用户"),
                # 论文权限
                Permission(name="paper:read", description="查看论文"),
                Permission(name="paper:write", description="上传/编辑论文"),
                Permission(name="paper:delete", description="删除论文"),
                Permission(name="paper:analyze", description="分析论文"),
                # 系统权限
                Permission(name="system:config", description="系统配置"),
                Permission(name="system:stats", description="查看统计"),
                # Zotero 权限
                Permission(name="zotero:read", description="查看 Zotero 数据"),
                Permission(name="zotero:import", description="从 Zotero 导入"),
            ]

            for perm in permissions:
                session.add(perm)

            await session.commit()
            logger.info("默认权限创建完成")

    async def _create_default_admin(self):
        """创建默认管理员账户"""
        from app.database.models import User, Role, UserRole
        from sqlalchemy import select
        from app.auth.security import hash_password

        async with self.session_maker() as session:
            # 检查是否已存在
            result = await session.execute(
                select(User).where(User.username == "admin")
            )
            if result.scalar_one_or_none():
                return

            # 创建默认管理员
            admin = User(
                username="admin",
                email="admin@smartpaper.com",
                hashed_password=hash_password("admin123"),
                is_active=True,
                is_superuser=True,
            )

            session.add(admin)
            await session.flush()

            # 分配 admin 角色
            admin_role = await session.execute(
                select(Role).where(Role.name == "admin")
            )
            admin_role = admin_role.scalar_one()

            user_role = UserRole(user_id=admin.id, role_id=admin_role.id)
            session.add(user_role)

            await session.commit()
            logger.warning("默认管理员账户创建完成: admin/admin123")


# 创建全局数据库实例
db = Database()


async def get_db() -> AsyncSession:
    """获取数据库会话的依赖注入函数"""
    async for session in db.get_session():
        yield session
