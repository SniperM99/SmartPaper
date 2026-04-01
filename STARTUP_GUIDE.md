# SmartPaper Vue 3 项目启动指南

## 项目概述

SmartPaper 已成功升级为 Vue 3 + FastAPI 前后端分离架构，包含：
- **前端**：Vue 3 + Vite + Pinia + Vue Router + D3.js
- **后端**：FastAPI + SQLAlchemy + SQLite
- **用户认证**：JWT + RBAC 权限管理
- **界面**：学术专业风格，无 emoji 图标，学术蓝 #1e40af 主色调

---

## 一、项目结构

```
SmartPaper/
├── backend/              # FastAPI 后端
│   ├── app/              # 应用代码
│   ├── requirements.txt  # Python 依赖
│   └── README.md         # 后端文档
├── vue-frontend/         # Vue 3 前端
│   ├── src/              # 源代码
│   ├── package.json      # Node 依赖
│   └── README.md         # 前端文档
├── docs/                 # 架构设计文档
└── streamlit.app.py      # 原始 Streamlit 应用（保留）
```

---

## 二、环境要求

### 前端环境
- Node.js >= 18.0.0
- npm >= 9.0.0

### 后端环境
- Python >= 3.10
- pip >= 23.0

### 后端依赖

后端需要额外的 Python 包，请运行：

```bash
cd /Users/m99/Documents/SmartPaper/backend
./install_deps.sh
```

或手动安装：

```bash
pip install 'python-jose[cryptography]' 'passlib[bcrypt]'
pip install aiosqlite email-validator slowapi
```

---

## 三、后端启动步骤

### 1. 进入后端目录

```bash
cd /Users/m99/Documents/SmartPaper/backend
```

### 2. 创建并激活虚拟环境

```bash
# 创建虚拟环境（如果还没有）
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件：

```bash
# 应用配置
ENV=development
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./smartpaper.db

# JWT 密钥（生产环境请使用强密钥）
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS 配置
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# API 配置
API_KEY=your-api-key
```

### 5. 初始化数据库

```bash
python -m app.database.init_db
```

### 6. 启动后端服务

**重要**：由于后端依赖项目根目录的代码，需要设置 PYTHONPATH。

```bash
# 方式 1：使用启动脚本（推荐）
./start_backend.sh

# 方式 2：手动启动（需要设置 PYTHONPATH）
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 方式 3：使用 Python 启动
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH
python -m app.main
```

### 7. 验证后端运行

访问以下地址：
- API 文档：http://localhost:8000/api/docs
- ReDoc 文档：http://localhost:8000/api/redoc
- 健康检查：http://localhost:8000/health

---

## 四、前端启动步骤

### 1. 进入前端目录

```bash
cd /Users/m99/Documents/SmartPaper/vue-frontend
```

### 2. 安装依赖

```bash
npm install
```

### 3. 配置 API 地址

编辑 `src/config/api.ts`（如果没有则创建）：

```typescript
export const API_BASE_URL = 'http://localhost:8000/api'
export const WS_BASE_URL = 'ws://localhost:8000/ws'
```

### 4. 启动开发服务器

```bash
npm run dev
```

### 5. 访问前端

打开浏览器访问：http://localhost:5173

---

## 五、完整启动流程（推荐）

### 终端 1：启动后端

```bash
# 进入后端目录
cd /Users/m99/Documents/SmartPaper/backend

# 激活虚拟环境
source ../.venv/bin/activate

# 设置 PYTHONPATH（重要！）
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 或者使用启动脚本（推荐）
./start_backend.sh
```

### 终端 2：启动前端

```bash
# 进入前端目录
cd /Users/m99/Documents/SmartPaper/vue-frontend

# 启动前端服务
npm run dev
```

### 终端 3：访问应用

- 前端地址：http://localhost:5173
- 后端 API 文档：http://localhost:8000/api/docs

---

## 六、用户认证系统使用

### 注册用户

1. 访问前端：http://localhost:5173
2. 点击"注册"
3. 填写用户信息：
   - 用户名
   - 邮箱
   - 密码（需满足强度要求）
4. 提交注册

### 登录系统

1. 访问前端：http://localhost:5173
2. 点击"登录"
3. 输入用户名和密码
4. 系统会生成 JWT Token 并保存到本地存储

### 后台管理

登录后，使用管理员账号可以访问后台管理系统：
- 用户管理
- 角色管理
- 权限管理
- 系统配置

---

## 七、构建生产版本

### 前端构建

```bash
cd /Users/m99/Documents/SmartPaper/vue-frontend

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

构建产物将输出到 `vue-frontend/dist/` 目录。

### 后端部署

```bash
# 修改环境变量为生产模式
ENV=production

# 使用 gunicorn 启动（推荐）
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## 八、常见问题

### 1. 后端启动失败

**问题**：ModuleNotFoundError

**解决方案**：
```bash
pip install -r requirements.txt
```

### 2. 前端启动失败

**问题**：依赖安装失败

**解决方案**：
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### 3. CORS 错误

**问题**：前端无法访问后端 API

**解决方案**：
检查后端 `.env` 文件中的 `ALLOWED_ORIGINS` 配置：
```bash
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4. 数据库初始化失败

**问题**：无法创建数据库表

**解决方案**：
```bash
# 删除现有数据库
rm smartpaper.db

# 重新初始化
python -m app.database.init_db
```

---

## 九、技术栈详情

### 前端技术栈

- **Vue 3.4.0** - 渐进式 JavaScript 框架
- **Vue Router 4.2.5** - 路由管理
- **Pinia 2.1.7** - 状态管理
- **Vite 5.0.0** - 构建工具
- **TypeScript 5.3.0** - 类型系统
- **D3.js 7.9.0** - 数据可视化（研究地图）
- **Element Plus** - UI 组件库（如需添加）

### 后端技术栈

- **FastAPI 0.109.0** - 现代 Web 框架
- **Uvicorn 0.27.0** - ASGI 服务器
- **SQLAlchemy 2.0.25** - ORM
- **Alembic 1.13.1** - 数据库迁移
- **Pydantic 2.10.5** - 数据验证
- **python-jose** - JWT Token 处理
- **passlib[bcrypt]** - 密码加密

---

## 十、快速命令参考

### 后端命令

```bash
# 启动后端
uvicorn app.main:app --reload

# 启动后端（指定端口）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 健康检查
curl http://localhost:8000/health

# 查看 API 文档
open http://localhost:8000/api/docs
```

### 前端命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 类型检查
npm run type-check

# 代码检查
npm run lint
```

---

## 十一、文档资源

- **前端文档**：`/Users/m99/Documents/SmartPaper/vue-frontend/README.md`
- **后端文档**：`/Users/m99/Documents/SmartPaper/backend/README.md`
- **架构设计**：`/Users/m99/Documents/SmartPaper/docs/VUE_ARCHITECTURE.md`
- **集成指南**：`/Users/m99/Documents/SmartPaper/vue-frontend/docs/INTEGRATION_GUIDE.md`
- **组件文档**：`/Users/m99/Documents/SmartPaper/vue-frontend/docs/COMPONENT_DOCS.md`

---

## 十二、支持与反馈

如有问题，请检查：
1. 后端日志：终端输出
2. 前端日志：浏览器控制台
3. API 文档：http://localhost:8000/api/docs

---

祝使用愉快！🎉
