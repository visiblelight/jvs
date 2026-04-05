# 管理后台 — 用户与板块权限接口

Base Path: `/api/admin`

除 `GET /modules` 仅需登录外，本文档的所有接口都**只允许超级管理员**调用。普通用户调用会返回 `403 仅超级管理员可访问`。

所有请求头需携带 Token：
```
Authorization: Bearer <access_token>
```

---

## 板块权限拦截规则

后台各板块 API（`/api/admin/todo/*`, `/api/admin/news/*`, `/api/admin/access-keys/*`）在路由级别挂载了 `require_module(<key>)` 依赖：

- 超级管理员直接放行（不校验 `user_modules`）
- 普通用户需在 `user_modules` 中有对应 `module_key`，否则返回 `403 没有 '<key>' 板块权限`

**无板块权限时：** 用户登录、查看个人信息、修改密码、上传头像等账号相关接口仍然可用；但无法进入任何业务板块 API。

---

## GET /modules

获取系统内置的板块列表（按 `sort_order` 升序）。登录用户皆可访问，用于前端构建 UI 菜单与权限勾选面板。

**成功响应** (200):
```json
[
  { "key": "todo",       "label": "事项管理", "sort_order": 10 },
  { "key": "news",       "label": "新闻资讯", "sort_order": 20 },
  { "key": "access_key", "label": "开放接口", "sort_order": 30 }
]
```

---

## GET /users

列出所有用户。

**成功响应** (200):
```json
[
  {
    "id": 1,
    "username": "admin",
    "is_active": true,
    "is_superuser": true,
    "avatar": null,
    "created_at": "2026-01-01T00:00:00Z",
    "module_count": 0
  }
]
```

---

## POST /users

新建用户。

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 登录账号，需唯一 |
| password | string | 是 | 登录密码（最少 6 位） |
| is_active | bool | 否 | 默认 true |
| is_superuser | bool | 否 | 默认 false |
| modules | string[] | 否 | 授权板块 key 列表；`is_superuser=true` 时忽略 |

**成功响应** (201): `UserDetail`
```json
{
  "id": 2,
  "username": "alice",
  "is_active": true,
  "is_superuser": false,
  "avatar": null,
  "created_at": "2026-04-05T10:00:00Z",
  "modules": ["todo", "news"]
}
```

**失败响应**:

| 状态码 | detail |
|--------|--------|
| 400 | 用户名已存在 |
| 400 | 无效的模块 key: xxx |

---

## GET /users/{user_id}

获取用户详情。返回 `UserDetail`（结构同上）。`404` 表示用户不存在。

---

## PUT /users/{user_id}

修改用户。字段为增量更新（可部分提交）。

**请求体** (JSON，全部可选):

| 字段 | 类型 | 说明 |
|------|------|------|
| username | string | 新用户名（需唯一） |
| password | string | 重置后的新密码（最少 6 位） |
| is_active | bool | 启用/禁用；禁用=软删除 |
| is_superuser | bool | 升降级超级管理员 |

**保护规则**:

| 状态码 | detail | 触发条件 |
|--------|--------|------|
| 400 | 用户名已存在 | 新用户名与他人冲突 |
| 400 | 不能修改自己的超管权限 | 当前用户即目标用户，且改动 `is_superuser` |
| 400 | 不能禁用自己 | 当前用户即目标用户，且 `is_active=false` |
| 400 | 至少需保留一个活跃的超级管理员 | 禁用/降级操作会导致系统无活跃超管 |
| 404 | 用户不存在 | |

> 当用户被升级为超管时，其 `user_modules` 记录会被清空（超管隐式拥有全部板块）。

**成功响应** (200): `UserDetail`

---

## PUT /users/{user_id}/modules

覆盖式设置用户的板块权限。

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| modules | string[] | 是 | 完整的板块 key 列表（先删后插） |

**失败响应**:

| 状态码 | detail |
|--------|--------|
| 400 | 超级管理员无需配置板块权限 |
| 400 | 无效的模块 key: xxx |
| 404 | 用户不存在 |

**成功响应** (200): `UserDetail`
