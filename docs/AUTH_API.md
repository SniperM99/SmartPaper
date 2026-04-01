# SmartPaper 认证和管理 API 文档

## 概述

SmartPaper 后端实现了完整的用户认证和授权系统，包括用户注册登录、JWT Token 认证、基于角色的访问控制（RBAC）和后台管理接口。

## 安全特性

- **JWT Token 认证**: 使用访问令牌和刷新令牌的双令牌机制
- **密码加密**: 使用 bcrypt 加密存储密码
- **密码强度验证**: 支持配置密码复杂度要求
- **RBAC 权限控制**: 基于角色和权限的细粒度访问控制
- **速率限制**: 防止暴力破解和 DDoS 攻击
- **安全头**: 添加 XSS、CSRF 等安全防护头
- **审计日志**: 记录重要操作日志

## 数据库模型

### User（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String(50) | 用户名（唯一） |
| email | String(100) | 邮箱（唯一） |
| hashed_password | String(255) | 加密密码 |
| full_name | String(100) | 全名 |
| avatar_url | String(255) | 头像URL |
| bio | Text | 个人简介 |
| is_active | Boolean | 是否活跃 |
| is_superuser | Boolean | 是否超级用户 |
| is_verified | Boolean | 是否已验证 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
| last_login | DateTime | 最后登录时间 |
| last_login_ip | String(50) | 最后登录IP |

### Role（角色表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(50) | 角色名（唯一） |
| description | String(255) | 角色描述 |
| is_active | Boolean | 是否活跃 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### Permission（权限表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 权限名（唯一） |
| description | String(255) | 权限描述 |
| resource | String(50) | 资源类型 |
| action | String(50) | 操作类型 |
| created_at | DateTime | 创建时间 |

### Paper（论文表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID（外键） |
| title | String(500) | 论文标题 |
| arxiv_id | String(50) | arXiv ID |
| file_path | String(500) | 文件路径 |
| file_size | Integer | 文件大小 |
| parsed_content | Text | 解析内容（JSON） |
| analysis_result | Text | 分析结果（JSON） |
| status | String(20) | 状态 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
| analyzed_at | DateTime | 分析时间 |

## 认证 API（/api/auth）

### 1. 用户注册

**端点**: `POST /api/auth/register`

**请求体**:
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "bio": "Researcher"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "full_name": "John Doe",
    "bio": "Researcher",
    "avatar_url": null,
    "is_active": true,
    "is_superuser": false,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": null
  }
}
```

### 2. 用户登录

**端点**: `POST /api/auth/login`

**请求体**:
```json
{
  "username": "newuser",
  "password": "SecurePass123!"
}
```

**响应**: 同注册接口

**说明**: 用户名和邮箱都可以用于登录

### 3. 刷新令牌

**端点**: `POST /api/auth/refresh`

**请求体**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应**: 同注册接口

### 4. 用户登出

**端点**: `POST /api/auth/logout`

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

### 5. 修改密码

**端点**: `POST /api/auth/change-password`

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!"
}
```

**响应**:
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

### 6. 获取当前用户信息

**端点**: `GET /api/auth/me`

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "full_name": "John Doe",
  "bio": "Researcher",
  "avatar_url": null,
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

## 后台管理 API（/api/admin）

### 用户管理

#### 获取用户列表

**端点**: `GET /api/admin/users`

**请求头**:
```
Authorization: Bearer {access_token}
```

**权限**: `user:read`

**查询参数**:
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20，最大 100）
- `search`: 搜索用户名或邮箱
- `is_active`: 筛选活跃用户

**响应**:
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "users": [
    {
      "id": 1,
      "username": "newuser",
      "email": "user@example.com",
      "full_name": "John Doe",
      "bio": "Researcher",
      "avatar_url": null,
      "is_active": true,
      "is_superuser": false,
      "is_verified": false,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-01T12:00:00Z",
      "roles": [
        {
          "id": 1,
          "name": "user",
          "description": "普通用户",
          "is_active": true,
          "created_at": "2024-01-01T00:00:00Z"
        }
      ]
    }
  ]
}
```

#### 获取用户详情

**端点**: `GET /api/admin/users/{user_id}`

**权限**: `user:read`

**响应**: 同用户列表中的 user 对象

#### 更新用户

**端点**: `PUT /api/admin/users/{user_id}`

**权限**: `user:write`

**请求体**:
```json
{
  "full_name": "John Smith",
  "email": "newemail@example.com",
  "bio": "Senior Researcher",
  "avatar_url": "https://example.com/avatar.jpg",
  "is_active": true
}
```

#### 删除用户

**端点**: `DELETE /api/admin/users/{user_id}`

**权限**: `user:delete`

#### 激活/停用用户

**端点**: `POST /api/admin/users/{user_id}/activate`
**端点**: `POST /api/admin/users/{user_id}/deactivate`

**权限**: `user:write`

### 角色管理

#### 获取角色列表

**端点**: `GET /api/admin/roles`

**权限**: `user:read`

#### 创建角色

**端点**: `POST /api/admin/roles`

**权限**: `user:write`

**请求体**:
```json
{
  "name": "editor",
  "description": "内容编辑",
  "is_active": true,
  "permission_ids": [1, 2, 3]
}
```

#### 更新角色

**端点**: `PUT /api/admin/roles/{role_id}`

**权限**: `user:write`

#### 删除角色

**端点**: `DELETE /api/admin/roles/{role_id}`

**权限**: `user:delete`

#### 分配权限给角色

**端点**: `POST /api/admin/roles/{role_id}/permissions/{permission_id}`

**权限**: `user:write`

#### 撤销角色权限

**端点**: `DELETE /api/admin/roles/{role_id}/permissions/{permission_id}`

**权限**: `user:write`

### 权限管理

#### 获取权限列表

**端点**: `GET /api/admin/permissions`

**权限**: `user:read`

#### 创建权限

**端点**: `POST /api/admin/permissions`

**权限**: `user:write`

**请求体**:
```json
{
  "name": "paper:publish",
  "description": "发布论文",
  "resource": "paper",
  "action": "publish"
}
```

### 用户角色管理

#### 分配角色给用户

**端点**: `POST /api/admin/users/{user_id}/roles/{role_id}`

**权限**: `user:write`

#### 撤销用户角色

**端点**: `DELETE /api/admin/users/{user_id}/roles/{role_id}`

**权限**: `user:write`

### 系统统计

**端点**: `GET /api/admin/stats`

**权限**: `system:stats`

**响应**:
```json
{
  "total_users": 100,
  "active_users": 95,
  "total_papers": 500,
  "total_roles": 5,
  "total_permissions": 20
}
```

## 使用认证

### 在请求头中添加 Token

所有需要认证的接口都需要在请求头中添加 JWT Token：

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer {access_token}"
```

### 在前端使用

```typescript
// 设置认证头
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
};

// 请求受保护的接口
const response = await fetch('http://localhost:8000/api/admin/users', {
  headers: headers
});
```

### Token 过期处理

当 Token 过期时，使用刷新令牌获取新的访问令牌：

```typescript
// 1. 调用刷新接口
const refreshResponse = await fetch('http://localhost:8000/api/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh_token: refreshToken })
});

// 2. 获取新的 token
const { access_token, refresh_token } = await refreshResponse.json();

// 3. 更新本地存储
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
```

## 权限验证

### 在代码中使用依赖注入

```python
from fastapi import Depends, APIRouter
from app.auth.dependencies import require_permission

router = APIRouter()

@router.get("/papers")
async def get_papers(
    current_user = Depends(require_permission("paper:read"))
):
    # 只有拥有 paper:read 权限的用户才能访问
    pass
```

### 角色验证

```python
from app.auth.dependencies import require_role

@router.get("/admin/dashboard")
async def admin_dashboard(
    current_user = Depends(require_role("admin"))
):
    # 只有拥有 admin 角色的用户才能访问
    pass
```

### 超级用户验证

```python
from app.auth.security import get_current_superuser

@router.get("/system/config")
async def system_config(
    current_user = Depends(get_current_superuser)
):
    # 只有超级用户才能访问
    pass
```

## 默认账户

系统初始化后会创建默认管理员账户：

- **用户名**: `admin`
- **密码**: `admin123`
- **角色**: admin（拥有所有权限）

**⚠️ 生产环境请立即修改默认密码！**

## 默认角色

| 角色名 | 描述 | 默认权限 |
|--------|------|----------|
| admin | 系统管理员 | 所有权限 |
| user | 普通用户 | 基础权限 |
| guest | 访客 | 只读权限 |

## 默认权限

| 权限名 | 描述 | 资源 | 操作 |
|--------|------|------|------|
| user:read | 查看用户信息 | user | read |
| user:write | 修改用户信息 | user | write |
| user:delete | 删除用户 | user | delete |
| paper:read | 查看论文 | paper | read |
| paper:write | 上传/编辑论文 | paper | write |
| paper:delete | 删除论文 | paper | delete |
| paper:analyze | 分析论文 | paper | analyze |
| system:config | 系统配置 | system | config |
| system:stats | 查看统计 | system | stats |
| zotero:read | 查看 Zotero 数据 | zotero | read |
| zotero:import | 从 Zotero 导入 | zotero | import |

## 速率限制

为了防止暴力破解和滥用，认证相关接口有速率限制：

- `/api/auth/register`: 5 次/分钟/IP
- `/api/auth/login`: 10 次/分钟/IP
- `/api/auth/refresh`: 20 次/分钟/IP

超出限制将返回 `429 Too Many Requests`。

## 密码策略

密码强度要求（可在 `.env` 中配置）：

- 最小长度: 8 位（默认）
- 必须包含大写字母
- 必须包含小写字母
- 必须包含数字
- 必须包含特殊字符 (!@#$%^&*()_+-=[]{}|;:,.<>?)

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

## 安全建议

1. **修改默认密码**: 生产环境立即修改 admin 账户密码
2. **使用 HTTPS**: 生产环境必须使用 HTTPS
3. **定期更新 Token**: Token 过期时间不宜过长
4. **限制登录尝试**: 已实现速率限制
5. **日志监控**: 定期检查审计日志
6. **最小权限原则**: 按需分配权限
7. **定期备份**: 定期备份数据库

## 相关文档

- [FastAPI 后端文档](./FASTAPI_MIGRATION.md)
- [后端架构文档](./BACKEND_ARCHITECTURE.md)
- [API 快速开始](./API_QUICKSTART.md)
