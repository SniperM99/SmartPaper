# SmartPaper 后端启动指南（修复版）

## 问题说明

后端代码依赖项目根目录的 `application`、`src` 等模块，因此需要设置 `PYTHONPATH` 环境变量。

---

## 正确的启动方式

### 方式 1：使用启动脚本（推荐）

```bash
cd /Users/m99/Documents/SmartPaper/backend
./start_backend.sh
```

### 方式 2：手动启动

```bash
# 进入后端目录
cd /Users/m99/Documents/SmartPaper/backend

# 激活虚拟环境
source ../.venv/bin/activate

# 设置 PYTHONPATH（重要！）
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 验证启动成功

看到以下输出表示启动成功：

```
INFO:     Will watch for changes in these directories: ['/Users/m99/Documents/SmartPaper/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

然后可以访问：
- 健康检查：http://localhost:8000/health
- API 文档：http://localhost:8000/api/docs

---

## 常见错误

### 错误：ModuleNotFoundError: No module named 'application'

**原因**：未设置 PYTHONPATH

**解决**：
```bash
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH
```

### 错误：ModuleNotFoundError: No module named 'src'

**原因**：未设置 PYTHONPATH

**解决**：
```bash
export PYTHONPATH=/Users/m99/Documents/SmartPaper:$PYTHONPATH
```

---

## 项目依赖关系

```
SmartPaper/
├── backend/app/           # FastAPI 后端
│   └── main.py           # 主应用入口
├── application/           # 应用编排层（被后端引用）
├── domain/               # 领域模型（被后端引用）
├── infrastructure/       # 基础设施（被后端引用）
└── src/                  # 工具模块（被后端引用）
```

后端启动时，Python 需要能够找到这些目录，因此必须设置 PYTHONPATH。
