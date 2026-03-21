# 管理后台 — 认证接口

Base Path: `/api/admin/auth`

---

## POST /login

登录并获取 JWT Token。

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 登录账号 |
| password | string | 是 | 登录密码 |

**成功响应** (200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**失败响应**:

| 状态码 | detail | 说明 |
|--------|--------|------|
| 401 | 用户名或密码错误 | 账号不存在或密码不匹配 |
| 403 | 用户已被禁用 | 账号已被停用 |

---

## GET /me

获取当前登录用户信息。需在请求头中携带 Token。

**请求头**:

```
Authorization: Bearer <access_token>
```

**成功响应** (200):

```json
{
  "id": 1,
  "username": "admin",
  "is_active": true,
  "is_superuser": true
}
```

**失败响应**:

| 状态码 | detail | 说明 |
|--------|--------|------|
| 401 | 无效的认证凭据 | Token 缺失、过期或无效 |
| 403 | 用户已被禁用 | 用户账号已停用 |

---

## PUT /password

修改当前用户密码。

**请求头**: `Authorization: Bearer <access_token>`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 当前密码 |
| new_password | string | 是 | 新密码（最少 6 位） |

**成功响应**: `204 No Content`

**失败响应**:

| 状态码 | detail | 说明 |
|--------|--------|------|
| 400 | 旧密码不正确 | 当前密码验证失败 |
| 422 | 验证错误 | 新密码不满足长度要求 |
