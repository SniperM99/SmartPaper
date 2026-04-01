# SmartPaper 前后端启动故障排除指南

## 问题：`vite: command not found`

### 原因分析
前端项目的 `node_modules` 目录不存在，导致 `vite` 命令无法找到。

### 解决方案

#### 方法 1：使用一键启动脚本（推荐）
```bash
cd /Users/m99/Documents/SmartPaper
./start_all.sh
```
此脚本会自动检测并安装缺失的依赖，然后启动前后端服务。

#### 方法 2：单独安装前端依赖
```bash
cd /Users/m99/Documents/SmartPaper/vue-frontend
npm install
npm run dev
```

#### 方法 3：使用安装脚本
```bash
cd /Users/m99/Documents/SmartPaper
./install_frontend.sh
```

## 一键启动脚本使用说明

### 启动前后端
```bash
cd /Users/m99/Documents/SmartPaper
./start_all.sh
```

### 功能特性
- ✅ 自动检查后端虚拟环境（使用项目根目录的 `.venv`）
- ✅ 自动检查并安装前端依赖
- ✅ 自动复制 `.env.example` 到 `.env`（如果不存在）
- ✅ 并行启动前后端服务
- ✅ 输出日志到 `logs/` 目录
- ✅ Ctrl+C 优雅停止所有服务

### 服务地址
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/api/docs

### 日志位置
- 后端日志: `./logs/backend.log`
- 前端日志: `./logs/frontend.log`

### 常见问题

#### Q1: 后端虚拟环境未找到
```bash
cd /Users/m99/Documents/SmartPaper
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

#### Q2: 前端安装很慢或失败
```bash
# 使用淘宝镜像源
cd /Users/m99/Documents/SmartPaper/vue-frontend
npm install --registry=https://registry.npmmirror.com
```

#### Q3: 端口被占用
```bash
# 检查端口占用
lsof -i :3000
lsof -i :8000

# 杀死占用端口的进程
kill -9 <PID>
```

#### Q4: 后端启动失败
```bash
# 查看详细日志
cat /Users/m99/Documents/SmartPaper/logs/backend.log

# 单独测试后端
cd /Users/m99/Documents/SmartPaper/backend
source ../.venv/bin/activate
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 项目结构
```
SmartPaper/
├── start_all.sh           # 一键启动脚本 ⭐
├── install_frontend.sh    # 前端依赖安装脚本
├── logs/                  # 运行日志
├── backend/
│   ├── .venv/             # 后端虚拟环境（使用项目根目录的）
│   ├── .env               # 环境配置
│   ├── requirements.txt   # Python 依赖
│   └── start_backend.sh   # 后端启动脚本
└── vue-frontend/
    ├── node_modules/      # npm 依赖（首次运行后生成）
    ├── package.json       # npm 配置
    └── vite.config.ts     # Vite 配置
```

## 配置检查清单

启动前确保：
- [ ] 后端虚拟环境存在：`.venv/` 目录
- [ ] 后端配置文件存在：`backend/.env`
- [ ] Python 依赖已安装：在 `.venv` 中运行 `pip list`
- [ ] Node.js 已安装：运行 `node --version`
- [ ] npm 已安装：运行 `npm --version`
