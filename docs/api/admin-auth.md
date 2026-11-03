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
  "is_superuser": true,
  "avatar": null,
  "created_at": "2026-01-01T00:00:00Z",
  "modules": ["todo", "news", "access_key"]
}
```

> 超级管理员的 `modules` 始终为空数组（隐式拥有全部板块权限）；普通用户则按授权列出。

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

## 图片上传约束（Plan 024）

头像最大 2 MB，通用图片最大 5 MB。服务端解码并验证 JPEG、PNG、GIF、WebP，声明 MIME 必须与真实内容一致；扩展名由服务端确定。单帧最多 2000 万像素，所有帧合计最多 4000 万像素、最多 200 帧，超限或损坏返回 400。头像替换失败保留旧文件。上传目录仅提供有效图片，历史 HTML 或伪装图片 URL 返回 404，并设置 `nosniff`。

## 时间格式（Plan 024）

所有时间点返回带 `Z`（UTC）的 ISO 8601，例如 `2026-11-03T05:00:00Z`，上海客户端显示 13:00。写入截止时间、执行时间、新闻发布时间或提交日历查询边界时必须带 `Z` 或 `+08:00` 等偏移量；无时区时间点返回 422。纯日期 `YYYY-MM-DD` 不做时间点转换。未传字段保持不变，可选字段传 null 可清空。
