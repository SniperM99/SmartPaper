# SmartPaper 快速启动指南

## 最简单的方式：一键启动 ⭐

```bash
cd /Users/m99/Documents/SmartPaper
./start_all.sh
```

服务启动后访问：
- 前端界面: http://localhost:3071
- 后端 API: http://localhost:8713
- API 文档: http://localhost:8713/api/docs

## 如果启动失败

### 问题：`vite: command not found`

**原因**: 前端依赖未安装

**解决方法**:

```bash
cd /Users/m99/Documents/SmartPaper
./install_frontend.sh
```

或者手动安装：

```bash
cd /Users/m99/Documents/SmartPaper/vue-frontend
npm install
```

### 问题：后端虚拟环境不存在

```bash
cd /Users/m99/Documents/SmartPaper
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 问题：端口被占用

```bash
# 查看占用进程
lsof -i :3000
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

## 服务说明

### 一键启动脚本 (`start_all.sh`)

**功能**:
- 自动检查并安装前端依赖
- 自动检查后端环境
- 并行启动前后端服务
- 输出日志到 `logs/` 目录
- Ctrl+C 优雅停止所有服务

**日志位置**:
- 后端日志: `./logs/backend.log`
- 前端日志: `./logs/frontend.log`

**查看实时日志**:
```bash
tail -f ./logs/backend.log
tail -f ./logs/frontend.log
```

### 前端依赖安装脚本 (`install_frontend.sh`)

用于单独安装或重装前端依赖：

```bash
cd /Users/m99/Documents/SmartPaper
./install_frontend.sh
```

## 项目结构

```
SmartPaper/
├── start_all.sh              # 一键启动脚本 ⭐
├── install_frontend.sh       # 前端依赖安装脚本
├── logs/                     # 运行日志目录
├── backend/
│   ├── .env                  # 后端环境配置（需配置 API Key）
│   └── requirements.txt      # Python 依赖
└── vue-frontend/
    ├── node_modules/         # npm 依赖（首次运行后生成）
    └── package.json          # npm 配置
```

## 首次运行前检查清单

- [ ] Python 3.10+ 已安装
- [ ] Node.js 18+ 已安装
- [ ] 后端虚拟环境存在: `.venv/`
- [ ] 后端配置文件存在: `backend/.env`
- [ ] 已配置 API Key（在 `backend/.env` 中）

## 相关文档

- [故障排除指南](TROUBLESHOOTING.md) - 详细的故障诊断和解决方案
- [项目 README](README.md) - 完整的项目文档
- [后端启动指南](backend/STARTUP_GUIDE_FINAL.md) - 后端详细配置说明

## 获取帮助

如果遇到问题：
1. 查看日志文件：`logs/backend.log` 和 `logs/frontend.log`
2. 参考 [故障排除指南](TROUBLESHOOTING.md)
3. 检查 API Key 配置是否正确
4. 确认网络连接正常
