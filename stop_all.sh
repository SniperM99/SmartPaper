#!/bin/bash
# SmartPaper 停止所有服务脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 停止 SmartPaper 服务...${NC}"
echo ""

# 查找并停止后端进程
BACKEND_PID=$(ps aux | grep "uvicorn app.main:app" | grep -v grep | awk '{print $2}')
if [ -n "$BACKEND_PID" ]; then
    echo -e "${GREEN}停止后端服务 (PID: $BACKEND_PID)${NC}"
    kill $BACKEND_PID
    sleep 1
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}强制停止后端...${NC}"
        kill -9 $BACKEND_PID
    fi
    echo -e "${GREEN}✅ 后端服务已停止${NC}"
else
    echo -e "${YELLOW}未找到运行中的后端服务${NC}"
fi

# 查找并停止前端进程
FRONTEND_PID=$(ps aux | grep "vite" | grep -v grep | awk '{print $2}')
if [ -n "$FRONTEND_PID" ]; then
    echo -e "${GREEN}停止前端服务 (PID: $FRONTEND_PID)${NC}"
    kill $FRONTEND_PID
    sleep 1
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}强制停止前端...${NC}"
        kill -9 $FRONTEND_PID
    fi
    echo -e "${GREEN}✅ 前端服务已停止${NC}"
else
    echo -e "${YELLOW}未找到运行中的前端服务${NC}"
fi

echo ""
echo -e "${GREEN}✅ 所有服务已停止${NC}"
