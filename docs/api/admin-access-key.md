# Access Key 管理接口文档

基础路径：`/api/admin/access-keys`

所有接口需 JWT 鉴权（`Authorization: Bearer <token>`），操作范围限定为当前用户数据。

---

## GET /scopes

获取系统中所有可用的权限定义。

**响应** `200`
```json
[
  { "scope": "news:create", "label": "提交新闻文章" }
]
```

---

## GET /

获取当前用户的全部 Access Key。

**响应** `200`
```json
[
  {
    "id": 1,
    "name": "default",
    "key": "abc123...",
    "scopes": ["news:create"],
    "is_active": true,
    "created_at": "..."
  }
]
```

---

## POST /

创建 Access Key。

**请求体**
```json
{
  "name": "my-agent",
  "scopes": ["news:create"]
}
```

- `scopes` 中的每个值必须是系统已定义的合法 scope，否则返回 400

**响应** `201` — 返回完整 Key 对象（含 key 明文，仅此次返回完整值）

---

## PUT /{id}

修改 Access Key（名称、启用状态或权限）。

**请求体**
```json
{
  "name": "新名称",
  "is_active": false,
  "scopes": ["news:create"]
}
```

所有字段均为可选，仅传需要修改的字段。

**响应** `200`

---

## DELETE /{id}

删除 Access Key。

**响应** `204`
