#!/bin/bash
# SmartPaper 后端依赖安装脚本

echo "安装 SmartPaper 后端依赖..."

# 激活虚拟环境
if [ -f "../.venv/bin/activate" ]; then
    source "../.venv/bin/activate"
else
    echo "错误：虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 安装基础依赖
echo "安装 FastAPI 基础依赖..."
pip install -q fastapi uvicorn python-multipart

# 安装数据验证
echo "安装数据验证依赖..."
pip install -q pydantic pydantic-settings

# 安装异步支持
echo "安装异步依赖..."
pip install -q httpx aiofiles

# 安装 CORS
echo "安装 CORS 依赖..."
pip install -q python-cors

# 安装数据库
echo "安装数据库依赖..."
pip install -q sqlalchemy aiosqlite alembic

# 安装认证和授权
echo "安装认证依赖..."
pip install -q 'python-jose[cryptography]' 'passlib[bcrypt]'

# 安装工具库
echo "安装工具库..."
pip install -q python-dotenv loguru

# 安装速率限制
echo "安装速率限制..."
pip install -q slowapi

# 安装邮箱验证
echo "安装邮箱验证..."
pip install -q email-validator

echo "✅ 后端依赖安装完成！"
