#!/bin/bash
# SmartPaper 一键启动前后端脚本（带端口占用处理）

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/vue-frontend"

# 端口配置
BACKEND_PORT=8713
FRONTEND_PORT=3071

# 函数：检查端口是否被占用
is_port_in_use() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 函数：停止指定端口的进程
stop_port() {
    local port=$1
    echo -e "${YELLOW}⚠️  检测到端口 $port 被占用，正在停止...${NC}"
    
    # 查找占用端口的进程
    local pids=$(lsof -ti :$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}正在停止进程: $pids${NC}"
        kill -9 $pids 2>/dev/null || true
        sleep 2
        
        # 再次检查
        if is_port_in_use $port; then
            echo -e "${RED}❌ 无法释放端口 $port${NC}"
            return 1
        else
            echo -e "${GREEN}✅ 端口 $port 已释放${NC}"
            return 0
        fi
    fi
    return 0
}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   SmartPaper 前后端一键启动工具${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# ========== 后端启动检查 ==========
echo -e "${YELLOW}[1/4] 检查后端环境...${NC}"
# 优先使用项目根目录的 .venv
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}❌ 后端虚拟环境不存在${NC}"
    echo "请先在项目根目录创建虚拟环境："
    echo "  cd /Users/m99/Documents/SmartPaper"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r backend/requirements.txt"
    exit 1
fi
echo -e "${GREEN}✅ 后端虚拟环境存在 (使用项目根目录 .venv)${NC}"

# 检查 .env 文件
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  后端 .env 文件不存在，正在从 .env.example 复制...${NC}"
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    echo -e "${YELLOW}⚠️  请编辑 $BACKEND_DIR/.env 配置你的 API Key${NC}"
fi

# ========== 前端依赖检查与安装 ==========
echo ""
echo -e "${YELLOW}[2/4] 检查前端依赖...${NC}"
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}⚠️  前端依赖未安装，正在安装（这可能需要几分钟）...${NC}"
    cd "$FRONTEND_DIR"
    npm install
    echo -e "${GREEN}✅ 前端依赖安装完成${NC}"
    cd "$PROJECT_ROOT"
else
    echo -e "${GREEN}✅ 前端依赖已安装${NC}"
fi

# ========== 创建日志目录 ==========
echo ""
echo -e "${YELLOW}[3/4] 准备启动环境...${NC}"
mkdir -p "$PROJECT_ROOT/logs"

# ========== 启动后端和前端 ==========
echo ""
echo -e "${YELLOW}[4/4] 启动前后端服务（并行运行）...${NC}"
echo ""

# 检查并释放后端端口
if is_port_in_use $BACKEND_PORT; then
    stop_port $BACKEND_PORT
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 无法启动后端，端口 $BACKEND_PORT 被占用且无法释放${NC}"
        exit 1
    fi
fi

# 检查并释放前端端口
if is_port_in_use $FRONTEND_PORT; then
    stop_port $FRONTEND_PORT
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 无法启动前端，端口 $FRONTEND_PORT 被占用且无法释放${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 启动中...${NC}"
echo -e "${GREEN}   后端: http://localhost:8713${NC}"
echo -e "${GREEN}   前端: http://localhost:3071${NC}"
echo -e "${GREEN}   API文档: http://localhost:8713/api/docs${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⚠️  按 Ctrl+C 停止所有服务${NC}"
echo ""

# 函数：清理进程
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止服务...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}✅ 所有服务已停止${NC}"
    exit 0
}

# 捕获 Ctrl+C 信号
trap cleanup SIGINT SIGTERM

# 启动后端（使用项目根目录的 .venv）
echo -e "${YELLOW}→ 启动后端服务...${NC}"
cd "$BACKEND_DIR"
source "$PROJECT_ROOT/.venv/bin/activate" 2>/dev/null || source ".venv/bin/activate"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8713 --reload \
    > "$PROJECT_ROOT/logs/backend.log" 2>&1 &
BACKEND_PID=$!
cd "$PROJECT_ROOT"

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ 后端启动失败，请查看日志: $PROJECT_ROOT/logs/backend.log${NC}"
    cat "$PROJECT_ROOT/logs/backend.log"
    exit 1
fi
echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"

# 启动前端
echo -e "${YELLOW}→ 启动前端服务...${NC}"
cd "$FRONTEND_DIR"
nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

# 等待前端启动
sleep 3

# 检查前端是否启动成功
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ 前端启动失败，请查看日志: $PROJECT_ROOT/logs/frontend.log${NC}"
    cat "$PROJECT_ROOT/logs/frontend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi
echo -e "${GREEN}✅ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"

# 显示实时日志
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 所有服务启动成功！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo -e "   后端日志: tail -f $PROJECT_ROOT/logs/backend.log"
echo -e "   前端日志: tail -f $PROJECT_ROOT/logs/frontend.log"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo ""

# 保持脚本运行，等待用户中断
wait $BACKEND_PID $FRONTEND_PID
