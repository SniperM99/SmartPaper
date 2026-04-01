#!/bin/bash
# SmartPaper 后端启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 激活虚拟环境
source "$PROJECT_ROOT/.venv/bin/activate"

# 添加项目根目录到 Python 路径
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 启动后端服务（使用虚拟环境中的 python -m uvicorn）
cd "$SCRIPT_DIR"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8713 --reload
