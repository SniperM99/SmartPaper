# SmartPaper Vue 3 项目 - 最终启动指南

## 🚀 一键启动（推荐）

### 启动所有服务

```bash
cd /Users/m99/Documents/SmartPaper
./start_all.sh
```

### 停止所有服务

```bash
cd /Users/m99/Documents/SmartPaper
./stop_all.sh
```

---

## 📋 前提条件

### 已修复的问题

1. ✅ 后端依赖已安装（python-jose、passlib、aiosqlite、email-validator、slowapi）
2. ✅ 前端依赖已安装（@vue/tsconfig、element-plus、@element-plus/icons-vue）
3. ✅ 环境配置已创建（.env 文件）
4. ✅ 类型导入错误已修复（file_service.py）
5. ✅ CORS 配置已修复（ALLOWED_ORIGINS）
6. ✅ Python 路径已设置（PYTHONPATH）

### 环境要求

- **Python**: >= 3.10
- **Node.js**: >= 18.0.0
- **npm**: >= 9.0.0

---

## 🎯 快速启动流程

### 方式 1：一键启动（推荐）

```bash
# 启动前后端
cd /Users/m99/Documents/SmartPaper
./start_all.sh

# 停止前后端
./stop_all.sh
```

### 方式 2：分别启动

#### 启动后端

```bash
cd /Users/m99/Documents/SmartPaper/backend
./start_backend.sh
```

#### 启动前端（新终端）

```bash
cd /Users/m99/Documents/SmartPaper/vue-frontend
npm run dev
```

---

## 📍 访问地址

启动成功后，可以访问：

- **前端**: http://localhost:3000
- **后端**: http://localhost:8000
- **API 文档**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **健康检查**: http://localhost:8000/health

---

## 📝 日志查看

### 后端日志

```bash
tail -f /tmp/smartpaper_backend.log
```

### 前端日志

```bash
tail -f /tmp/smartpaper_frontend.log
```

---

## 🔧 手动启动详解

### 后端手动启动

```bash
# 1. 进入后端目录
cd /Users/m99/Documents/SmartPaper/backend

# 2. 激活虚拟环境
source ../.venv/bin/activate

# 3. 设置 PYTHONPATH
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH

# 4. 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端手动启动

```bash
# 1. 进入前端目录
cd /Users/m99/Documents/SmartPaper/vue-frontend

# 2. 安装依赖（首次运行）
npm install

# 3. 启动前端
npm run dev
```

---

## 📦 依赖安装

### 后端依赖安装

```bash
cd /Users/m99/Documents/SmartPaper/backend
./install_deps.sh
```

或手动安装：

```bash
# FastAPI 基础
pip install fastapi uvicorn python-multipart

# 数据验证
pip install pydantic pydantic-settings

# 异步支持
pip install httpx aiofiles

# 数据库
pip install sqlalchemy aiosqlite alembic

# 认证授权
pip install 'python-jose[cryptography]' 'passlib[bcrypt]'

# 工具库
pip install python-dotenv loguru

# 速率限制
pip install slowapi

# 邮箱验证
pip install email-validator
```

### 前端依赖安装

```bash
cd /Users/m99/Documents/SmartPaper/vue-frontend
npm install
```

---

## 🐛 常见问题

### 1. vite: command not found

**原因**: 前端依赖未安装

**解决**:
```bash
cd /Users/m99/Documents/SmartPaper/vue-frontend
npm install
```

### 2. ModuleNotFoundError: No module named 'application'

**原因**: 未设置 PYTHONPATH

**解决**:
```bash
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH
```

### 3. ModuleNotFoundError: No module named 'jose'

**原因**: 未安装 python-jose

**解决**:
```bash
pip install 'python-jose[cryptography]'
```

### 4. ModuleNotFoundError: No module named 'aiosqlite'

**原因**: 未安装 aiosqlite

**解决**:
```bash
pip install aiosqlite
```

### 5. Cannot find base config file "@vue/tsconfig/tsconfig.dom.json"

**原因**: TypeScript 配置依赖缺失

**解决**:
```bash
npm install @vue/tsconfig --save-dev
```

### 6. 后端启动失败

**检查日志**:
```bash
tail -f /tmp/smartpaper_backend.log
```

**常见原因**:
- 虚拟环境未激活
- PYTHONPATH 未设置
- 数据库文件权限问题

### 7. 前端启动失败

**检查日志**:
```bash
tail -f /tmp/smartpaper_frontend.log
```

**常见原因**:
- node_modules 未安装
- 端口被占用（3000 或 5173）
- 依赖版本冲突

---

## 📊 项目结构

```
SmartPaper/
├── start_all.sh           # 一键启动脚本
├── stop_all.sh           # 停止所有服务
├── backend/              # 后端目录
│   ├── start_backend.sh  # 后端启动脚本
│   ├── install_deps.sh   # 后端依赖安装脚本
│   ├── .env             # 环境配置
│   └── app/             # FastAPI 应用
├── vue-frontend/         # 前端目录
│   ├── package.json     # 前端依赖配置
│   ├── vite.config.ts   # Vite 配置
│   └── src/             # Vue 源代码
├── docs/                # 文档目录
├── application/          # 应用编排层
├── domain/              # 领域模型
├── infrastructure/      # 基础设施
└── src/                 # 工具模块
```

---

## 🎯 功能特性

### 已实现的功能

- ✅ 用户注册登录（JWT 认证）
- ✅ 后台管理系统
- ✅ 用户管理
- ✅ 角色管理
- ✅ 权限管理（RBAC）
- ✅ 研究地图可视化
- ✅ Zotero 集成
- ✅ 文献导入
- ✅ 论文分析
- ✅ 多论文对比
- ✅ 科研画像

### 界面特点

- ✅ 无 emoji 图标（专业 SVG 图标）
- ✅ 学术蓝 #1e40af 主色调
- ✅ 响应式布局
- ✅ 现代简约设计
- ✅ 流畅的过渡动画

---

## 🔐 默认账户

首次使用需要注册账户：

1. 访问 http://localhost:3000
2. 点击"注册"
3. 填写用户信息
4. 登录后使用

**注意**: 第一个注册的用户将自动获得管理员权限。

---

## 📚 相关文档

- **架构设计**: `/Users/m99/Documents/SmartPaper/docs/VUE_ARCHITECTURE.md`
- **后端启动指南**: `/Users/m99/Documents/SmartPaper/backend/STARTUP_GUIDE_FINAL.md`
- **前端文档**: `/Users/m99/Documents/SmartPaper/vue-frontend/README.md`
- **研究地图文档**: `/Users/m99/Documents/SmartPaper/vue-frontend/docs/INTEGRATION_GUIDE.md`

---

## 💡 使用建议

### 开发环境

- 使用 `./start_all.sh` 一键启动
- 使用 `npm run dev` 启动前端（带热重载）
- 使用 `uvicorn ... --reload` 启动后端（带热重载）

### 生产环境

- 前端构建: `npm run build`
- 后端使用 Gunicorn + Uvicorn Workers
- 配置 HTTPS
- 使用 PostgreSQL 或 MySQL 数据库

---

## 🎉 开始使用

现在你可以启动 SmartPaper 了！

```bash
cd /Users/m99/Documents/SmartPaper
./start_all.sh
```

然后访问 http://localhost:3000 开始使用！

---

**祝使用愉快！** 🚀
