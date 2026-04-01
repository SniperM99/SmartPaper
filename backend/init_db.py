#!/usr/bin/env python3
"""初始化数据库"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.db import db
from loguru import logger


async def init_database():
    """初始化数据库"""
    logger.info("开始初始化数据库...")

    try:
        # 初始化数据库（创建表和默认数据）
        await db.init_db()

        logger.info("✅ 数据库初始化完成！")
        logger.info("")
        logger.info("默认管理员账户:")
        logger.info("  用户名: admin")
        logger.info("  密码: admin123")
        logger.info("")
        logger.info("⚠️  生产环境请立即修改默认密码！")

    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}", exc_info=True)
        sys.exit(1)


async def reset_database():
    """重置数据库（开发/测试用）"""
    logger.warning("⚠️  正在重置数据库，所有数据将被删除！")

    confirm = input("确认继续？(yes/no): ")
    if confirm.lower() != "yes":
        logger.info("已取消操作")
        return

    try:
        # 删除所有表
        await db.drop_tables()

        # 重新初始化
        await db.init_db()

        logger.info("✅ 数据库重置完成！")

    except Exception as e:
        logger.error(f"❌ 数据库重置失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument("command", choices=["init", "reset"], help="操作命令")
    args = parser.parse_args()

    if args.command == "init":
        asyncio.run(init_database())
    elif args.command == "reset":
        asyncio.run(reset_database())
