#!/bin/bash
# FastAPI 后端启动脚本

echo "🚀 启动 SmartPaper FastAPI 后端..."

# 检查虚拟环境（优先使用项目根目录的 .venv）
if [ -d "../.venv" ]; then
    echo "✅ 使用项目根目录的虚拟环境"
    source ../.venv/bin/activate
elif [ -d "venv" ]; then
    echo "✅ 使用本地虚拟环境"
    source venv/bin/activate
else
    echo "⚠️  未检测到虚拟环境，正在创建..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 复制环境配置文件
if [ ! -f ".env" ]; then
    echo "📝 创建环境配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置你的 API Key"
fi

# 启动服务
echo "🎯 启动服务..."
# 添加项目根目录到 Python 路径，以便导入 application 模块
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8713 --reload
