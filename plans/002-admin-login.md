# Plan 002 - 管理后台登录功能

**日期**: 2026-03-19
**状态**: 已完成

---

## 一、功能概述

管理后台实现基于账号密码的登录功能，使用 JWT Token 进行会话管理。

---

## 二、后端实现

### 2.1 用户模型 — `backend/app/models/user.py`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer, PK | 自增主键 |
| username | String(50), Unique | 登录账号 |
| hashed_password | String(255) | bcrypt 哈希密码 |
| is_active | Boolean | 是否启用，默认 True |
| is_superuser | Boolean | 是否超级管理员，默认 False |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 2.2 请求/响应 Schema — `backend/app/schemas/auth.py`

- `LoginRequest`: `username` + `password`
- `TokenResponse`: `access_token` + `token_type`
- `UserInfo`: `id` + `username` + `is_active` + `is_superuser`（登录后获取当前用户信息）

### 2.3 业务逻辑 — `backend/app/services/auth.py`

- `authenticate(username, password)` — 查库校验密码，返回 User 或 None
- `get_current_user(token)` — 解析 JWT，返回当前用户（作为依赖注入使用）

### 2.4 API 路由 — `backend/app/api/admin/auth.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/auth/login` | 登录，返回 JWT Token |
| GET | `/api/admin/auth/me` | 获取当前登录用户信息（需携带 Token） |

### 2.5 初始数据

提供一个命令行脚本 `backend/scripts/init_admin.py`，用于创建初始管理员账号：
- 默认用户名: `admin`
- 默认密码: `admin123`（首次登录后应修改）

### 2.6 数据库迁移

生成 Alembic 迁移脚本，创建 `users` 表。

---

## 三、前端实现（admin）

### 3.1 登录页面 — `frontend/admin/src/views/LoginView.vue`

- 表单：用户名输入框 + 密码输入框 + 登录按钮
- 简洁居中布局，适合 PC 端
- 登录失败显示错误提示

### 3.2 API 请求封装 — `frontend/admin/src/api/auth.js`

- `login(username, password)` — 调用 POST `/api/admin/auth/login`
- `getMe()` — 调用 GET `/api/admin/auth/me`

### 3.3 状态管理 — `frontend/admin/src/stores/auth.js`

- state: `token`, `user`
- actions: `login()`, `fetchUser()`, `logout()`
- Token 存储在 `localStorage`，axios 请求拦截器自动附加 `Authorization: Bearer <token>`

### 3.4 路由守卫 — `frontend/admin/src/router/index.js`

- 添加 `beforeEach` 全局守卫
- 无 Token 时跳转到 `/login`
- 已登录时访问 `/login` 重定向到 `/dashboard`

### 3.5 Dashboard 占位页 — `frontend/admin/src/views/DashboardView.vue`

- 登录成功后的落地页，显示简单的欢迎信息
- 包含退出登录按钮

### 3.6 Axios 实例 — `frontend/admin/src/api/request.js`

- 统一 baseURL、请求拦截（附加 Token）、响应拦截（401 自动跳转登录）

---

## 四、涉及文件清单

```
backend/
├── app/
│   ├── models/user.py              # 新增：User 模型
│   ├── models/__init__.py          # 修改：导入 User
│   ├── schemas/auth.py             # 新增：登录相关 Schema
│   ├── services/auth.py            # 新增：认证业务逻辑
│   ├── api/admin/auth.py           # 新增：登录路由
│   ├── api/admin/__init__.py       # 修改：注册路由
│   └── core/deps.py               # 修改：添加 get_current_user 依赖
├── scripts/
│   └── init_admin.py               # 新增：初始化管理员脚本
└── main.py                         # 修改：挂载 admin 路由

frontend/admin/src/
├── api/
│   ├── request.js                  # 新增：Axios 实例
│   └── auth.js                     # 新增：认证 API
├── stores/auth.js                  # 新增：认证状态管理
├── views/
│   ├── LoginView.vue               # 新增：登录页
│   └── DashboardView.vue           # 新增：Dashboard 占位页
└── router/index.js                 # 修改：添加路由和守卫
```

---

## 五、文档更新

- `docs/api/admin-auth.md` — 登录相关接口文档
- `docs/database/schema.md` — 新增：全局数据结构文档（记录所有表结构），本次记录 `users` 表

---

## 六、执行顺序

1. 后端：创建 User 模型 → Alembic 迁移 → Schema → Service → API 路由 → 挂载路由
2. 后端：创建初始管理员脚本
3. 前端：Axios 实例 → API 封装 → Auth Store → 登录页 → Dashboard 页 → 路由守卫
4. 文档：更新 API 文档 + 数据结构文档
