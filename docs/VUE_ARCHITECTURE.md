# SmartPaper Vue.js 技术架构设计方案

## 一、架构概述

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        Vue.js 前端应用                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Vue 3     │  │  Vue Router  │  │    Pinia     │           │
│  │ Composition  │  │  路由管理     │  │   状态管理    │           │
│  │     API      │  │              │  │              │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                  │                  │                   │
│  ┌──────▼──────────────────▼──────────────────▼───────┐         │
│  │              UI 组件层 (Element Plus)               │         │
│  │  Overview | Library | Analysis | ResearchMap | Zotero│         │
│  └────────────────────────┬───────────────────────────┘         │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                    HTTP/REST/WebSocket
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   FastAPI 后端服务                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   API Layer  │  │ Service Layer│  │  Domain Layer│           │
│  │  (FastAPI)   │  │ (业务编排)    │  │  (领域模型)   │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                  │                  │                   │
│  ┌──────▼──────────────────▼──────────────────▼───────┐         │
│  │              Infrastructure Layer                  │         │
│  │   LLM Client | PDF Converter | Zotero Client       │         │
│  └────────────────────────┬───────────────────────────┘         │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   外部服务与存储                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ OpenAI   │  │  智谱AI   │  │  Zotero  │  │ 文件系统 │         │
│  │  /其他   │  │          │  │  API     │  │  存储    │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 架构分层

| 层级 | 技术栈 | 职责 |
|------|--------|------|
| 前端表现层 | Vue 3 + Element Plus | 用户交互、数据展示 |
| 前端逻辑层 | Composition API + Pinia | 业务逻辑、状态管理 |
| 前端路由层 | Vue Router | 页面导航、路由守卫 |
| 网络通信层 | Axios + WebSocket | HTTP 请求、实时通信 |
| 后端 API 层 | FastAPI + Pydantic | RESTful API、请求验证 |
| 后端服务层 | Application Services | 业务编排、流程控制 |
| 领域层 | Domain Models | 核心业务对象 |
| 基础设施层 | LLM/PDF/Zotero Clients | 外部服务集成 |

---

## 二、前端技术栈选择

### 2.1 核心技术栈

| 技术 | 版本 | 选型理由 |
|------|------|----------|
| **Vue 3** | ^3.4.0 | 响应式系统优秀、Composition API 提高代码复用、生态成熟 |
| **TypeScript** | ^5.3.0 | 类型安全、提升开发体验、减少运行时错误 |
| **Vue Router** | ^4.2.0 | 官方路由、支持动态路由、导航守卫完善 |
| **Pinia** | ^2.1.0 | 官方推荐状态管理、API 简洁、TypeScript 支持好 |
| **Element Plus** | ^2.5.0 | 组件丰富、设计美观、中文文档完善、科研场景适配 |
| **Vite** | ^5.0.0 | 构建速度快、HMR 优秀、开发体验好 |
| **Axios** | ^1.6.0 | HTTP 客户端成熟、拦截器完善 |
| **VueUse** | ^10.7.0 | Composition API 工具库、提升开发效率 |

### 2.2 UI 框架对比

| 框架 | 优点 | 缺点 | 选择理由 |
|------|------|------|----------|
| **Element Plus** | 中文文档、组件丰富、适合后台管理 | 主题定制相对复杂 | ✅ **选择**：科研场景中文内容多、组件风格专业 |
| Ant Design Vue | 设计系统完善、企业级 | 体积较大、配置复杂 | 备选：如需国际化场景 |
| Naive UI | 主题定制灵活、TypeScript 支持好 | 中文社区较小 | 备选：如需高度定制 |

### 2.3 开发工具链

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.5.0",
    "axios": "^1.6.0",
    "@vueuse/core": "^10.7.0",
    "dayjs": "^1.11.0",
    "mitt": "^3.0.0",
    "monaco-editor": "^0.45.0",
    "jwt-decode": "^4.0.0",
    "dompurify": "^3.0.0",
    "crypto-js": "^4.2.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "vue-tsc": "^1.8.0",
    "@vitejs/plugin-vue": "^5.0.0",
    "sass": "^1.69.0",
    "unplugin-auto-import": "^0.17.0",
    "unplugin-vue-components": "^0.26.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0",
    "@types/dompurify": "^3.0.0"
  }
}
```

---

## 三、后端架构设计

### 3.1 框架选择：FastAPI

**选型理由**：

1. **性能优势**：基于 Starlette + Pydantic，异步支持，比 Flask 快 2-3 倍
2. **自动文档**：OpenAPI/Swagger 自动生成，无需额外配置
3. **类型安全**：Pydantic 数据验证、自动类型提示
4. **异步支持**：原生 async/await，适合 LLM 流式输出
5. **生态兼容**：与 LangChain、LangGraph 完美集成

### 3.2 核心依赖

```txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-multipart>=0.0.6
websockets>=12.0
httpx>=0.26.0
aiofiles>=23.2.0

# 认证与授权
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# 数据库
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0

# Redis 缓存
redis>=5.0.0
hiredis>=2.3.0

# 安全与工具
slowapi>=0.1.9
```

### 3.3 项目结构

```
backend/
├── main.py                    # FastAPI 应用入口
├── api/                       # API 路由层
│   ├── __init__.py
│   ├── deps.py                # 依赖注入
│   └── v1/                    # API v1 版本
│       ├── __init__.py
│       ├── auth.py            # 认证相关 API
│       ├── users.py           # 用户管理 API
│       ├── admin.py           # 后台管理 API
│       ├── papers.py          # 论文相关 API
│       ├── analysis.py        # 分析相关 API
│       ├── library.py         # 论文库管理 API
│       ├── research_map.py    # 研究地图 API
│       ├── zotero.py          # Zotero 集成 API
│       └── profile.py         # 用户画像 API
├── services/                  # 业务服务层
│   ├── __init__.py
│   ├── auth_service.py        # 认证服务
│   ├── user_service.py        # 用户管理服务
│   ├── admin_service.py       # 后台管理服务
│   ├── paper_service.py
│   ├── analysis_service.py
│   ├── library_service.py
│   ├── research_map_service.py
│   ├── zotero_service.py
│   └── profile_service.py
├── schemas/                   # Pydantic 数据模型
│   ├── __init__.py
│   ├── auth.py                # 认证相关模型
│   ├── user.py                # 用户相关模型
│   ├── admin.py               # 后台管理模型
│   ├── paper.py
│   ├── analysis.py
│   ├── library.py
│   ├── research_map.py
│   └── common.py
├── core/                      # 核心配置
│   ├── __init__.py
│   ├── config.py
│   ├── security.py            # JWT 与密码加密
│   ├── auth.py                # 认证相关工具
│   ├── rbac.py                # 权限管理 (RBAC)
│   └── llm.py
├── models/                    # SQLAlchemy 数据库模型
│   ├── __init__.py
│   ├── user.py                # 用户表
│   ├── role.py                # 角色表
│   ├── permission.py          # 权限表
│   └── base.py                # 基础模型
├── middleware/                # 中间件
│   ├── __init__.py
│   ├── cors.py
│   ├── auth.py                # 认证中间件
│   ├── rbac.py                # 权限验证中间件
│   └── logging.py
└── database/                  # 数据库相关
    ├── __init__.py
    ├── connection.py          # 数据库连接
    └── migrations/            # Alembic 迁移
        └── versions/
```

---

## 四、用户认证系统设计

### 4.1 认证架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    认证流程图                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   用户           前端              后端              数据库  │
│    │              │                 │                  │    │
│    ├─登录───────►│                 │                  │    │
│    │              ├─POST /auth/login────────────────────►│    │
│    │              │                 │  验证密码        │    │
│    │              │                 │  生成JWT Token   │    │
│    │              │◄─200 {token}─────┼───────────────────┤    │
│    │◄─保存Token──►│                 │                  │    │
│    │              │                 │                  │    │
│    ├─请求API────►│                 │                  │    │
│    │              ├─GET /api/v1/papers (Header: Bearer token)│
│    │              ├─────────────────►                  │    │
│    │              │                 │  解析JWT         │    │
│    │              │                 │  验证权限(RBAC)  │    │
│    │              │◄─200 data───────┼──────────────────┤    │
│    │◄─展示数据──►│                 │                  │    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 JWT Token 认证方案

#### 4.2.1 Token 结构

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_123",
    "username": "researcher",
    "roles": ["user", "researcher"],
    "permissions": ["paper:read", "analysis:create"],
    "iat": 1711948800,
    "exp": 1712035200
  },
  "signature": "..."
}
```

#### 4.2.2 Token 配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 算法 | RS256 | 非对称加密，更安全 |
| Access Token 有效期 | 2 小时 | 短期有效，降低泄露风险 |
| Refresh Token 有效期 | 7 天 | 用于刷新 Access Token |
| 密钥 | RSA 密钥对 | 私钥签名，公钥验证 |

#### 4.2.3 Python 后端实现

```python
# core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)

# JWT 配置
SECRET_KEY = "your-secret-key"  # 生产环境使用环境变量
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

def create_access_token(data: dict) -> str:
    """创建 Access Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    """解码 Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 4.3 RBAC 权限管理

#### 4.3.1 角色定义

| 角色代码 | 角色名称 | 权限描述 |
|----------|----------|----------|
| `admin` | 管理员 | 系统所有权限 |
| `researcher` | 研究员 | 论文分析、研究地图 |
| `reviewer` | 审核员 | 论文库管理、审核 |
| `guest` | 访客 | 只读权限 |

#### 4.3.2 权限定义

| 权限代码 | 权限名称 | 描述 |
|----------|----------|------|
| `paper:read` | 查看论文 | 查看论文列表和详情 |
| `paper:delete` | 删除论文 | 删除论文记录 |
| `analysis:create` | 创建分析 | 发起论文分析任务 |
| `analysis:read` | 查看分析 | 查看分析结果 |
| `library:manage` | 管理文库 | 论文库管理 |
| `admin:users` | 用户管理 | 查看和管理用户 |
| `admin:config` | 系统配置 | 系统配置管理 |

#### 4.3.3 权限验证中间件

```python
# middleware/rbac.py
from fastapi import Request, HTTPException, status
from functools import wraps

def require_permission(permission: str):
    """权限验证装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = request.state.user  # 从认证中间件获取用户
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证"
                )
            if permission not in user.get("permissions", []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少权限: {permission}"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@router.get("/admin/users")
@require_permission("admin:users")
async def list_users(request: Request):
    return {"users": [...]}
```

### 4.4 Session 管理

#### 4.4.1 登录流程

```typescript
// 前端登录
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

async function login(username: string, password: string) {
  const res = await api.post('/api/v1/auth/login', {
    username,
    password
  })

  // 保存 Token
  authStore.setToken(res.data.access_token)
  authStore.setRefreshToken(res.data.refresh_token)

  // 保存用户信息
  authStore.setUser(res.data.user)

  return res.data
}
```

```python
# 后端登录接口
@router.post("/login")
async def login(
    credentials: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate(
        username=credentials.username,
        password=credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 生成 Token
    access_token = create_access_token({
        "sub": user.id,
        "username": user.username,
        "roles": [r.code for r in user.roles],
        "permissions": [p.code for p in user.permissions]
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }
```

#### 4.4.2 Token 刷新

```python
@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    user_id = decode_refresh_token(refresh_token)
    user = await auth_service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="无效的 Refresh Token")

    # 生成新的 Access Token
    access_token = create_access_token({
        "sub": user.id,
        "username": user.username,
        "roles": [r.code for r in user.roles],
        "permissions": [p.code for p in user.permissions]
    })

    return {"access_token": access_token}
```

### 4.5 前端认证 Store (Pinia)

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const user = ref<User | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.roles.includes('admin') ?? false)
  const permissions = computed(() => user.value?.permissions ?? [])

  // Actions
  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }

  function setRefreshToken(newToken: string) {
    refreshToken.value = newToken
    localStorage.setItem('refresh_token', newToken)
  }

  function setUser(newUser: User) {
    user.value = newUser
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  function clearAuth() {
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  async function login(username: string, password: string) {
    const res = await api.post('/api/v1/auth/login', { username, password })
    setToken(res.data.access_token)
    setUser(res.data.user)
    return res.data
  }

  async function logout() {
    await api.post('/api/v1/auth/logout')
    clearAuth()
  }

  // 初始化：从 localStorage 恢复
  function init() {
    const savedToken = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user')
    if (savedToken) token.value = savedToken
    if (savedUser) user.value = JSON.parse(savedUser)
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    permissions,
    login,
    logout,
    clearAuth,
    init
  }
})
```

---

## 五、后台管理系统设计

### 5.1 后台管理架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    后台管理系统架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Vue 前端 - 管理界面                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │ 用户管理 │  │ 角色管理 │  │ 日志查看 │  │ 数据统计 │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │           系统配置管理                              │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│                              │ JWT Token                         │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 FastAPI 后端 - 管理接口                     │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │              权限验证 (RBAC)                         │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │ 用户API  │  │ 角色API  │  │ 日志API  │  │ 统计API  │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 PostgreSQL 数据库                         │   │
│  │  users | roles | permissions | user_roles | audit_logs   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 数据库设计

#### 5.2.1 用户表 (users)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, banned
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

#### 5.2.2 角色表 (roles)

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预置角色
INSERT INTO roles (code, name, description) VALUES
    ('admin', '管理员', '系统管理员，拥有所有权限'),
    ('researcher', '研究员', '可以进行论文分析和管理个人文库'),
    ('reviewer', '审核员', '可以管理论文库和审核内容'),
    ('guest', '访客', '只读权限');
```

#### 5.2.3 权限表 (permissions)

```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    resource VARCHAR(50) NOT NULL, -- paper, analysis, admin, etc.
    action VARCHAR(50) NOT NULL,   -- read, create, update, delete
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预置权限
INSERT INTO permissions (code, name, resource, action) VALUES
    ('paper:read', '查看论文', 'paper', 'read'),
    ('paper:delete', '删除论文', 'paper', 'delete'),
    ('analysis:create', '创建分析', 'analysis', 'create'),
    ('analysis:read', '查看分析', 'analysis', 'read'),
    ('library:manage', '管理文库', 'library', 'manage'),
    ('admin:users', '用户管理', 'admin', 'users'),
    ('admin:config', '系统配置', 'admin', 'config');
```

#### 5.2.4 用户角色关联表 (user_roles)

```sql
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id)
);
```

#### 5.2.5 角色权限关联表 (role_permissions)

```sql
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);
```

#### 5.2.6 审计日志表 (audit_logs)

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    username VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),  -- user, paper, config, etc.
    resource_id UUID,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    request_data JSONB,
    response_data JSONB,
    status VARCHAR(20),  -- success, failure
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
```

### 5.3 后台管理功能模块

#### 5.3.1 用户管理

**功能列表**：
- 用户列表展示（分页、搜索、筛选）
- 用户详情查看
- 用户创建/编辑/删除
- 用户状态管理（激活/禁用）
- 用户角色分配
- 用户密码重置
- 登录历史查看

**API 接口**：

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /api/v1/admin/users | 获取用户列表 | admin:users |
| GET | /api/v1/admin/users/{id} | 获取用户详情 | admin:users |
| POST | /api/v1/admin/users | 创建用户 | admin:users |
| PUT | /api/v1/admin/users/{id} | 更新用户 | admin:users |
| DELETE | /api/v1/admin/users/{id} | 删除用户 | admin:users |
| POST | /api/v1/admin/users/{id}/roles | 分配角色 | admin:users |
| POST | /api/v1/admin/users/{id}/reset-password | 重置密码 | admin:users |

#### 5.3.2 角色管理

**功能列表**：
- 角色列表展示
- 角色创建/编辑/删除
- 权限分配
- 角色用户列表

**API 接口**：

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /api/v1/admin/roles | 获取角色列表 | admin:users |
| POST | /api/v1/admin/roles | 创建角色 | admin:users |
| PUT | /api/v1/admin/roles/{id} | 更新角色 | admin:users |
| DELETE | /api/v1/admin/roles/{id} | 删除角色 | admin:users |
| POST | /api/v1/admin/roles/{id}/permissions | 分配权限 | admin:users |

#### 5.3.3 日志查看

**功能列表**：
- 操作日志查询（分页、时间筛选、用户筛选）
- 日志详情查看
- 日志导出

**API 接口**：

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /api/v1/admin/logs | 获取日志列表 | admin:users |
| GET | /api/v1/admin/logs/{id} | 获取日志详情 | admin:users |
| POST | /api/v1/admin/logs/export | 导出日志 | admin:users |

#### 5.3.4 数据统计

**功能列表**：
- 用户统计（总数、活跃用户、新增用户）
- 论文统计（总数、分析完成数、今日新增）
- 分析统计（总分析次数、平均耗时、成功率）
- 系统资源统计（存储使用、API 调用次数）

**API 接口**：

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /api/v1/admin/stats | 获取统计概览 | admin:users |
| GET | /api/v1/admin/stats/users | 用户统计 | admin:users |
| GET | /api/v1/admin/stats/papers | 论文统计 | admin:users |

### 5.4 前端后台页面结构

```
frontend/src/views/admin/
├── Dashboard.vue        # 后台首页（统计概览）
├── users/
│   ├── UserList.vue     # 用户列表
│   ├── UserForm.vue     # 用户表单
│   └── UserDetail.vue   # 用户详情
├── roles/
│   ├── RoleList.vue     # 角色列表
│   └── RolePermission.vue  # 权限分配
├── logs/
│   ├── LogList.vue      # 日志列表
│   └── LogDetail.vue    # 日志详情
└── settings/
    ├── SystemConfig.vue # 系统配置
    └── LLMConfig.vue    # LLM 配置
```

### 5.5 路由配置

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // 公共路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue')
  },

  // 主应用路由（需要认证）
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/overview' },
      { path: 'overview', component: () => import('@/views/Overview.vue') },
      { path: 'import', component: () => import('@/views/Import.vue') },
      { path: 'library', component: () => import('@/views/Library.vue') },
      { path: 'analysis', component: () => import('@/views/Analysis.vue') },
      { path: 'research-map', component: () => import('@/views/ResearchMap.vue') },
      { path: 'zotero', component: () => import('@/views/Zotero.vue') }
    ]
  },

  // 后台管理路由（需要管理员权限）
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'users', component: () => import('@/views/admin/users/UserList.vue') },
      { path: 'roles', component: () => import('@/views/admin/roles/RoleList.vue') },
      { path: 'logs', component: () => import('@/views/admin/logs/LogList.vue') },
      { path: 'settings', component: () => import('@/views/admin/settings/SystemConfig.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }

  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/')
    return
  }

  next()
})

export default router
```

### 5.6 Axios 请求拦截器

```typescript
// utils/request.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000
})

// 请求拦截器：添加 Token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore()

    // 401 未认证
    if (error.response?.status === 401) {
      // 尝试刷新 Token
      if (authStore.refreshToken) {
        try {
          const res = await axios.post('/api/v1/auth/refresh', {
            refresh_token: authStore.refreshToken
          })
          authStore.setToken(res.data.access_token)
          // 重新发送原请求
          return api.request(error.config)
        } catch (refreshError) {
          authStore.logout()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        authStore.logout()
        window.location.href = '/login'
      }
    }

    // 403 无权限
    if (error.response?.status === 403) {
      ElMessage.error('没有权限访问此资源')
    }

    return Promise.reject(error)
  }
)

export default api
```

---

## 七、API 接口设计

### 7.1 认证相关 API

#### 7.1.1 用户注册

**POST** `/api/v1/auth/register`

**请求体**：
```json
{
  "username": "researcher",
  "email": "researcher@example.com",
  "password": "SecurePass123!",
  "full_name": "张研究员"
}
```

**响应**：
```json
{
  "user": {
    "id": "uuid",
    "username": "researcher",
    "email": "researcher@example.com",
    "full_name": "张研究员",
    "roles": ["researcher"]
  }
}
```

#### 7.1.2 用户登录

**POST** `/api/v1/auth/login`

**请求体**：
```json
{
  "username": "researcher",
  "password": "SecurePass123!"
}
```

**响应**：
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "researcher",
    "email": "researcher@example.com",
    "full_name": "张研究员",
    "roles": ["researcher"],
    "permissions": ["paper:read", "analysis:create"]
  }
}
```

#### 7.1.3 刷新 Token

**POST** `/api/v1/auth/refresh`

**请求体**：
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应**：
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 7.1.4 获取当前用户信息

**GET** `/api/v1/auth/me`

**请求头**：
```
Authorization: Bearer {access_token}
```

**响应**：
```json
{
  "id": "uuid",
  "username": "researcher",
  "email": "researcher@example.com",
  "full_name": "张研究员",
  "avatar_url": "https://example.com/avatar.jpg",
  "roles": [
    {
      "code": "researcher",
      "name": "研究员"
    }
  ],
  "permissions": ["paper:read", "analysis:create", "analysis:read"],
  "created_at": "2025-01-01T00:00:00Z",
  "last_login_at": "2025-03-31T12:00:00Z"
}
```

### 7.2 后台管理 API

#### 7.2.1 获取用户列表

**GET** `/api/v1/admin/users`

**查询参数**：
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20）
- `search`: 搜索关键词（用户名/邮箱）
- `status`: 状态筛选（active/inactive/banned）

**响应**：
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": "uuid",
      "username": "researcher",
      "email": "researcher@example.com",
      "full_name": "张研究员",
      "status": "active",
      "roles": ["researcher"],
      "created_at": "2025-01-01T00:00:00Z",
      "last_login_at": "2025-03-31T12:00:00Z"
    }
  ]
}
```

#### 7.2.2 创建用户

**POST** `/api/v1/admin/users`

**请求体**：
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "full_name": "新用户",
  "roles": ["researcher"]
}
```

**响应**：
```json
{
  "id": "uuid",
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "新用户",
  "status": "active",
  "roles": ["researcher"]
}
```

#### 7.2.3 分配用户角色

**POST** `/api/v1/admin/users/{id}/roles`

**请求体**：
```json
{
  "roles": ["admin", "researcher"]
}
```

**响应**：
```json
{
  "message": "角色分配成功"
}
```

#### 7.2.4 获取角色列表

**GET** `/api/v1/admin/roles`

**响应**：
```json
{
  "items": [
    {
      "id": "uuid",
      "code": "admin",
      "name": "管理员",
      "description": "系统管理员，拥有所有权限",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

#### 7.2.5 获取审计日志

**GET** `/api/v1/admin/logs`

**查询参数**：
- `page`: 页码
- `page_size`: 每页数量
- `user_id`: 用户 ID 筛选
- `action`: 操作类型筛选
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应**：
```json
{
  "total": 500,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "username": "researcher",
      "action": "paper:delete",
      "resource_type": "paper",
      "resource_id": "uuid",
      "ip_address": "192.168.1.1",
      "status": "success",
      "created_at": "2025-03-31T12:00:00Z"
    }
  ]
}
```

#### 7.2.6 获取系统统计

**GET** `/api/v1/admin/stats`

**响应**：
```json
{
  "users": {
    "total": 100,
    "active": 80,
    "new_today": 5
  },
  "papers": {
    "total": 500,
    "analyzed": 450,
    "new_today": 10
  },
  "analysis": {
    "total_tasks": 1000,
    "completed": 950,
    "avg_duration": 180,
    "success_rate": 0.95
  },
  "system": {
    "storage_used": "1.5GB",
    "api_calls_today": 5000,
    "uptime": "99.9%"
  }
}
```

### 7.3 RESTful API 规范（业务接口）

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/papers | 获取论文列表 |
| POST | /api/v1/papers | 创建论文记录 |
| GET | /api/v1/papers/{id} | 获取论文详情 |
| DELETE | /api/v1/papers/{id} | 删除论文 |
| POST | /api/v1/papers/{id}/analyze | 分析论文 |
| GET | /api/v1/papers/{id}/analysis/{task_id} | 获取分析结果 |
| GET | /api/v1/library/stats | 获取库统计信息 |
| POST | /api/v1/library/batch-import | 批量导入论文 |
| GET | /api/v1/research-map/nodes | 获取研究地图节点 |
| GET | /api/v1/research-map/connections | 获取研究地图连线 |
| POST | /api/v1/zotero/sync | 同步 Zotero 数据 |
| GET | /api/v1/profile | 获取用户画像 |
| PUT | /api/v1/profile | 更新用户画像 |

### 7.4 WebSocket 接口

```typescript
// 前端连接示例
const ws = new WebSocket('ws://localhost:8000/ws/analysis/{task_id}')

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  // { type: 'chunk' | 'progress' | 'complete', content: string, progress?: number }
}
```

### 4.3 核心 API 设计示例

#### 4.3.1 分析论文 API

**POST** `/api/v1/papers/analyze`

**请求体**：
```json
{
  "source": "https://arxiv.org/pdf/2301.07041.pdf",
  "source_type": "url",
  "role": "phd_student",
  "task": "phd_analysis",
  "domain": "machine_learning",
  "use_chain": false
}
```

**响应**：
```json
{
  "task_id": "task_abc123",
  "status": "pending",
  "message": "分析任务已创建"
}
```

#### 4.3.2 流式获取分析结果

**GET** `/api/v1/papers/analyze/stream/{task_id}`

**SSE 流式响应**：
```
data: {"type": "progress", "step": "解析PDF", "progress": 10}

data: {"type": "chunk", "content": "# 论文分析报告\n\n"}

data: {"type": "progress", "step": "调用LLM", "progress": 50}

data: {"type": "chunk", "content": "## 摘要\n本文提出..."}

data: {"type": "complete", "file_path": "/outputs/analysis_task_abc123.md"}
```

### 4.4 数据模型（Pydantic Schemas）

```python
# backend/schemas/paper.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PaperMetadata(BaseModel):
    title: str
    authors: List[str] = []
    abstract: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    keywords: List[str] = []

class PaperCreate(BaseModel):
    source: str = Field(..., description="URL或本地路径")
    source_type: str = Field(..., description="url|file|local")

class PaperResponse(BaseModel):
    id: str
    cache_key: str
    metadata: PaperMetadata
    status: str
    created_at: datetime
    file_path: Optional[str] = None

class AnalysisRequest(BaseModel):
    paper_id: str
    role: str
    task: str
    domain: str = "general"
    use_chain: bool = False

class AnalysisResponse(BaseModel):
    task_id: str
    status: str
    message: str
```

---

## 五、前端项目结构

### 5.1 目录结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/              # 静态资源
│   │   ├── images/
│   │   └── styles/
│   │       └── variables.scss
│   ├── components/          # 通用组件
│   │   ├── common/
│   │   │   ├── Loading.vue
│   │   │   └── Empty.vue
│   │   └── analysis/
│   │       ├── MarkdownViewer.vue
│   │       └── ProgressCard.vue
│   ├── composables/         # Composition API 复用逻辑
│   │   ├── useAnalysis.ts
│   │   ├── useLibrary.ts
│   │   ├── useZotero.ts
│   │   └── useWebSocket.ts
│   ├── layouts/             # 布局组件
│   │   └── MainLayout.vue
│   ├── router/              # 路由配置
│   │   └── index.ts
│   ├── stores/              # Pinia 状态管理
│   │   ├── user.ts
│   │   ├── paper.ts
│   │   ├── analysis.ts
│   │   ├── library.ts
│   │   ├── researchMap.ts
│   │   └── zotero.ts
│   ├── types/               # TypeScript 类型定义
│   │   ├── index.ts
│   │   ├── paper.ts
│   │   ├── analysis.ts
│   │   └── zotero.ts
│   ├── utils/               # 工具函数
│   │   ├── request.ts       # Axios 封装
│   │   ├── storage.ts       # 本地存储
│   │   └── format.ts        # 格式化工具
│   ├── views/               # 页面组件
│   │   ├── Overview.vue         # 工作台总览
│   │   ├── Import.vue           # 导入与解析
│   │   ├── Library.vue          # 论文库
│   │   ├── Analysis.vue         # 分析工作流
│   │   ├── ResearchMap.vue      # 研究地图
│   │   └── Zotero.vue           # Zotero 集成
│   ├── App.vue
│   └── main.ts
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env.development
```

### 5.2 核心页面映射

| Streamlit 页面 | Vue 页面 | 路由路径 |
|----------------|----------|----------|
| 🧭 工作台总览 | `views/Overview.vue` | `/overview` |
| 📥 导入与解析 | `views/Import.vue` | `/import` |
| 📚 论文库 | `views/Library.vue` | `/library` |
| 🧠 分析工作流 | `views/Analysis.vue` | `/analysis` |
| 🗂️ Zotero 集成 | `views/Zotero.vue` | `/zotero` |

---

## 六、状态管理策略（Pinia）

### 6.1 Store 设计

```typescript
// stores/paper.ts - 论文状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Paper, AnalysisResult } from '@/types'

export const usePaperStore = defineStore('paper', () => {
  // State
  const papers = ref<Paper[]>([])
  const activePaper = ref<Paper | null>(null)
  const loading = ref(false)

  // Getters
  const analyzedCount = computed(() => papers.value.filter(p => p.status === 'completed').length)
  const pendingCount = computed(() => papers.value.filter(p => p.status === 'pending').length)

  // Actions
  async function fetchPapers() {
    loading.value = true
    try {
      const res = await api.get('/api/v1/papers')
      papers.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function analyzePaper(params: AnalysisParams) {
    const res = await api.post('/api/v1/papers/analyze', params)
    return res.data.task_id
  }

  return { papers, activePaper, loading, analyzedCount, pendingCount, fetchPapers, analyzePaper }
})
```

### 6.2 跨 Store 状态共享

使用 Pinia 插件实现持久化：

```typescript
// plugins/pinia-persist.ts
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
```

---

## 七、数据流转设计

### 7.1 前后端交互流程

```
用户操作 → Vue 组件 → Pinia Store → Axios → FastAPI → Service Layer → Domain Layer
                                                                 ↓
                                                          LLM/PDF/Zotero
                                                                 ↓
Pydantic Response → Axios → Store → 组件更新
```

### 7.2 文件上传机制

```typescript
// 前端上传
async function uploadPDF(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await api.post('/api/v1/papers/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      // 更新进度条
    }
  })
  return res.data
}
```

```python
# 后端接收
@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    paper_service: PaperService = Depends(get_paper_service)
):
    paper = await paper_service.create_from_upload(file)
    return PaperResponse.model_validate(paper)
```

### 7.3 流式输出实现

**Server-Sent Events (SSE)** 方案：

```typescript
// 前端接收 SSE
async function streamAnalysis(taskId: string) {
  const eventSource = new EventSource(`/api/v1/analysis/stream/${taskId}`)

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'chunk') {
      // 追加内容到 Markdown 显示
    } else if (data.type === 'progress') {
      // 更新进度条
    } else if (data.type === 'complete') {
      eventSource.close()
      // 分析完成
    }
  }

  return () => eventSource.close() // 清理函数
}
```

```python
# 后端 SSE
from fastapi.responses import StreamingResponse
import json
import asyncio

@router.get("/stream/{task_id}")
async def stream_analysis(task_id: str):
    async def event_generator():
        while not is_complete(task_id):
            chunk = get_next_chunk(task_id)
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            await asyncio.sleep(0.1)

        yield f"data: {json.dumps({'type': 'complete'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

## 八、配置文件管理

### 8.1 环境变量配置

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws
VITE_UPLOAD_MAX_SIZE=50MB
```

```bash
# .env.production
VITE_API_BASE_URL=https://api.smartpaper.ai/api/v1
VITE_WS_BASE_URL=wss://api.smartpaper.ai/ws
VITE_UPLOAD_MAX_SIZE=100MB
```

### 8.2 Vite 配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
```

---

## 八、前端项目结构

### 8.1 目录结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/              # 静态资源
│   │   ├── images/
│   │   └── styles/
│   │       └── variables.scss
│   ├── components/          # 通用组件
│   │   ├── common/
│   │   │   ├── Loading.vue
│   │   │   └── Empty.vue
│   │   └── analysis/
│   │       ├── MarkdownViewer.vue
│   │       └── ProgressCard.vue
│   ├── composables/         # Composition API 复用逻辑
│   │   ├── useAnalysis.ts
│   │   ├── useLibrary.ts
│   │   ├── useZotero.ts
│   │   └── useWebSocket.ts
│   ├── layouts/             # 布局组件
│   │   ├── MainLayout.vue
│   │   └── AdminLayout.vue
│   ├── router/              # 路由配置
│   │   └── index.ts
│   ├── stores/              # Pinia 状态管理
│   │   ├── auth.ts          # 认证状态
│   │   ├── user.ts
│   │   ├── paper.ts
│   │   ├── analysis.ts
│   │   ├── library.ts
│   │   ├── researchMap.ts
│   │   └── zotero.ts
│   ├── types/               # TypeScript 类型定义
│   │   ├── index.ts
│   │   ├── paper.ts
│   │   ├── analysis.ts
│   │   ├── auth.ts
│   │   └── zotero.ts
│   ├── utils/               # 工具函数
│   │   ├── request.ts       # Axios 封装
│   │   ├── storage.ts       # 本地存储
│   │   └── format.ts        # 格式化工具
│   ├── views/               # 页面组件
│   │   ├── auth/            # 认证相关页面
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   ├── admin/           # 后台管理页面
│   │   │   ├── Dashboard.vue
│   │   │   ├── users/
│   │   │   ├── roles/
│   │   │   ├── logs/
│   │   │   └── settings/
│   │   ├── Overview.vue         # 工作台总览
│   │   ├── Import.vue           # 导入与解析
│   │   ├── Library.vue          # 论文库
│   │   ├── Analysis.vue         # 分析工作流
│   │   ├── ResearchMap.vue      # 研究地图
│   │   └── Zotero.vue           # Zotero 集成
│   ├── App.vue
│   └── main.ts
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env.development
```

### 8.2 核心页面映射

| Streamlit 页面 | Vue 页面 | 路由路径 | 是否需要认证 |
|----------------|----------|----------|--------------|
| 登录页面 | `views/auth/Login.vue` | `/login` | ❌ 否 |
| 🧭 工作台总览 | `views/Overview.vue` | `/overview` | ✅ 是 |
| 📥 导入与解析 | `views/Import.vue` | `/import` | ✅ 是 |
| 📚 论文库 | `views/Library.vue` | `/library` | ✅ 是 |
| 🧠 分析工作流 | `views/Analysis.vue` | `/analysis` | ✅ 是 |
| 🗂️ Zotero 集成 | `views/Zotero.vue` | `/zotero` | ✅ 是 |
| 后台管理首页 | `views/admin/Dashboard.vue` | `/admin/dashboard` | ✅ 是（管理员） |
| 用户管理 | `views/admin/users/UserList.vue` | `/admin/users` | ✅ 是（管理员） |
| 角色管理 | `views/admin/roles/RoleList.vue` | `/admin/roles` | ✅ 是（管理员） |
| 日志查看 | `views/admin/logs/LogList.vue` | `/admin/logs` | ✅ 是（管理员） |
| 系统配置 | `views/admin/settings/SystemConfig.vue` | `/admin/settings` | ✅ 是（管理员） |

---

## 九、数据流转设计

### 9.1 迁移策略

#### 阶段一：基础设施搭建（Week 1-2）
1. 创建 Vue 3 + Vite 前端项目
2. 创建 FastAPI 后端项目
3. 配置开发环境和构建工具
4. 搭建基础组件库（布局、导航、通用组件）

#### 阶段二：后端 API 开发（Week 3-4）
1. 迁移 `PaperAnalysisService` 到 FastAPI Service
2. 设计并实现 RESTful API
3. 实现流式输出接口（SSE）
4. API 文档自动生成

#### 阶段三：前端页面开发（Week 5-7）
1. 实现 Overview 页面
2. 实现 Import/Library 页面
3. 实现 Analysis 页面（核心）
4. 实现 ResearchMap 和 Zotero 页面

#### 阶段四：联调测试（Week 8）
1. 前后端联调
2. 性能优化
3. 错误处理完善
4. 用户体验优化

#### 阶段五：部署上线（Week 9-10）
1. 生产环境配置
2. Docker 容器化
3. CI/CD 流水线
4. 监控与日志

### 9.2 兼容性方案

在迁移期间，保持 Streamlit 版本可用：

```
/current/          # 现有 Streamlit 版本
/vue/              # 新 Vue.js 版本（并行运行）
/api/              # 共享的 FastAPI 后端
```

### 9.3 数据迁移

1. **论文数据**：保留现有 JSON 存储，新增数据库支持（PostgreSQL）
2. **分析结果**：保留 Markdown 文件，添加数据库索引
3. **用户配置**：迁移到用户数据库

---

## 十、性能优化策略

### 10.1 前端优化

| 优化项 | 方案 | 预期效果 |
|--------|------|----------|
| 路由懒加载 | `defineAsyncComponent` | 减少首屏加载体积 40% |
| 组件虚拟化 | `vue-virtual-scroller` | 大列表渲染性能提升 10 倍 |
| 请求缓存 | Axios 拦截器 + 内存缓存 | 减少重复请求 60% |
| 图片懒加载 | `vue-lazyload` | 减少首屏加载时间 |
| CDN 加速 | 使用阿里云/腾讯云 CDN | 静态资源加载速度提升 |

### 10.2 后端优化

| 优化项 | 方案 | 预期效果 |
|--------|------|----------|
| 异步处理 | FastAPI async/await | 并发能力提升 3 倍 |
| 数据库连接池 | SQLAlchemy async | 减少数据库连接开销 |
| 响应压缩 | Gzip/Brotli | 响应体积减少 70% |
| Redis 缓存 | 热点数据缓存 | 接口响应速度提升 10 倍 |

---

## 十一、安全设计

### 11.1 前端安全

1. **XSS 防护**：使用 `DOMPurify` 清理用户输入
2. **CSRF 防护**：CSRF Token 验证
3. **敏感信息加密**：LocalStorage 不存储敏感信息

### 11.2 后端安全

1. **认证授权**：JWT Token + RBAC
2. **输入验证**：Pydantic 模型验证
3. **速率限制**：`slowapi` 实现请求限流
4. **文件上传安全**：类型检查、大小限制、病毒扫描

---

## 十二、技术债务与风险

### 12.1 已知风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Streamlit 到 Vue 重构工作量大 | 进度延迟 | 分阶段迁移，保持双版本运行 |
| LLM 流式输出延迟 | 用户体验差 | 优化 SSE 实现，前端缓冲 |
| 大文件上传超时 | 导入失败 | 分片上传、断点续传 |
| 研究地图渲染性能差 | 页面卡顿 | 使用 Canvas/WebGL 替代 SVG |

### 12.2 技术债务

1. **现有代码重构**：application 层需要适配 FastAPI
2. **测试覆盖**：前端 E2E 测试、后端单元测试
3. **文档完善**：API 文档、组件文档

---

## 十三、总结

### 13.1 架构优势

✅ **前后端分离**：解耦前端与后端，独立开发部署
✅ **类型安全**：TypeScript + Pydantic 双重保障
✅ **认证授权**：JWT + RBAC 完整权限体系
✅ **后台管理**：用户、角色、权限、日志全方位管理
✅ **用户体验**：流式输出、实时更新、响应式设计
✅ **可扩展性**：模块化设计，易于添加新功能
✅ **性能优化**：异步处理、缓存策略、懒加载
✅ **安全可靠**：密码加密、Token 刷新、审计日志

### 13.2 关键决策

1. **前端框架**：Vue 3 + Composition API（优于 React 的学习曲线）
2. **UI 框架**：Element Plus（中文文档完善、科研场景适配）
3. **后端框架**：FastAPI（异步支持、自动文档、类型安全）
4. **状态管理**：Pinia（Vuex 的现代化替代品）
5. **认证方案**：JWT Token + RBAC 权限控制
6. **数据库**：PostgreSQL + Redis（关系型数据 + 缓存）
7. **通信协议**：RESTful + SSE（HTTP 标准协议，兼容性好）

### 13.3 后续工作

- [ ] 搭建 Vue 3 + Vite 前端脚手架
- [ ] 搭建 FastAPI 后端脚手架
- [ ] 配置 PostgreSQL 数据库和 Redis 缓存
- [ ] 实现用户认证系统（注册、登录、Token 管理）
- [ ] 实现后台管理功能（用户、角色、权限、日志）
- [ ] 设计并实现核心 API 接口
- [ ] 开发前端基础组件和布局
- [ ] 实现论文分析功能的迁移
- [ ] 编写单元测试和 E2E 测试
- [ ] 部署到生产环境

---

## 更新日志

### v1.1 (2025-03-31)

**新增内容**：
- ✅ 第四章：用户认证系统设计
  - JWT Token 认证方案（Access Token + Refresh Token）
  - RBAC 权限管理（4 种角色、7 种权限）
  - 权限验证中间件
  - Session 管理（登录、刷新、登出）
  - 前端认证 Store (Pinia)
- ✅ 第五章：后台管理系统设计
  - 后台管理架构图
  - 数据库设计（6 张核心表：users, roles, permissions, user_roles, role_permissions, audit_logs）
  - 4 个后台管理功能模块（用户管理、角色管理、日志查看、数据统计）
  - 12 个后台管理 API 接口
  - 前端后台页面结构和路由配置
  - Axios 请求/响应拦截器（自动 Token 刷新）
- ✅ 第七章：API 接口设计扩展
  - 认证相关 API（5 个接口：注册、登录、刷新 Token、登出、获取用户信息）
  - 后台管理 API（6 个接口：用户列表、创建用户、分配角色、角色列表、审计日志、系统统计）
- ✅ 技术栈更新
  - 前端：新增 jwt-decode, dompurify, crypto-js
  - 后端：新增 python-jose, passlib, SQLAlchemy, Redis, slowapi

**修改内容**：
- 🔧 修正章节编号（原第四章→第七章）
- 🔧 更新项目结构（新增认证、后台管理相关模块）
- 🔧 更新 API 规范（分为认证 API、后台管理 API、业务 API）

### v1.0 (2025-03-31)

**初始版本**：
- ✅ 整体架构设计（前后端分离）
- ✅ 前端技术栈选型（Vue 3 + Element Plus + Pinia）
- ✅ 后端技术栈选型（FastAPI + Pydantic）
- ✅ 项目结构规划
- ✅ API 接口设计（业务接口）
- ✅ 数据流转设计
- ✅ 状态管理策略
- ✅ 配置文件管理
- ✅ 迁移路径与实施计划
- ✅ 性能优化策略
- ✅ 安全设计
- ✅ 技术债务与风险评估

---

**文档版本**: v1.1
**创建日期**: 2025-03-31
**更新日期**: 2025-03-31
**负责人**: 架构设计师
**审核状态**: 待审核
**更新内容**：新增用户认证系统设计（JWT + RBAC）、后台管理系统设计（用户/角色/权限/日志）、数据库表设计
