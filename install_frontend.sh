#!/bin/bash
# SmartPaper 前端依赖安装脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FRONTEND_DIR="$(dirname "${BASH_SOURCE[0]}")/vue-frontend"

echo -e "${GREEN}安装 SmartPaper 前端依赖...${NC}"
echo ""

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${YELLOW}⚠️  前端目录不存在: $FRONTEND_DIR${NC}"
    exit 1
fi

cd "$FRONTEND_DIR"

if [ -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules 已存在，正在删除重新安装...${NC}"
    rm -rf node_modules
fi

echo -e "${YELLOW}执行 npm install...${NC}"
npm install

echo ""
echo -e "${GREEN}✅ 前端依赖安装完成！${NC}"
