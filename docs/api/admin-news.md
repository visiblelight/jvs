# 新闻管理接口文档

基础路径：`/api/admin/news`

所有接口需 JWT 鉴权（`Authorization: Bearer <token>`），操作范围限定为当前用户数据。

---

## 分类管理

### GET /categories
获取当前用户的全部新闻分类。

**响应** `200`
```json
[
  { "id": 1, "name": "科技", "sort_order": 0, "created_at": "..." }
]
```

### POST /categories
创建新闻分类。

**请求体**
```json
{ "name": "科技", "sort_order": 0 }
```

**响应** `201` — 返回分类对象

### PUT /categories/{id}
修改分类（校验归属）。

**请求体**
```json
{ "name": "新名称", "sort_order": 1 }
```

**响应** `200` — 返回更新后的分类对象

### DELETE /categories/{id}
删除分类（校验归属 + 检查关联文章，有关联文章时返回 400）。

**响应** `204`

---

## 来源管理

### GET /sources
获取当前用户的全部新闻来源。

**响应** `200`
```json
[
  { "id": 1, "name": "微信公众号", "created_at": "..." }
]
```

### POST /sources
创建新闻来源。

**请求体**
```json
{ "name": "微信公众号" }
```

**响应** `201`

### PUT /sources/{id}
修改来源。

**响应** `200`

### DELETE /sources/{id}
删除来源（有关联文章时返回 400）。

**响应** `204`

---

## 文章管理

### GET /articles
文章列表（分页 + 筛选）。

**查询参数**
| 参数 | 类型 | 说明 |
|------|------|------|
| category_id | int | 按分类筛选 |
| source_id | int | 按来源筛选 |
| keyword | string | 全文搜索（标题、简介、正文、作者） |
| page | int | 页码，默认 1 |
| page_size | int | 每页条数，默认 20，最大 100 |

**响应** `200`
```json
{
  "items": [
    {
      "id": 1,
      "title": "...",
      "summary": "...",
      "content": "...",
      "source_url": "...",
      "source_id": 1,
      "author": "...",
      "published_at": "...",
      "category_id": 1,
      "created_at": "...",
      "updated_at": "...",
      "category": { "id": 1, "name": "科技", "sort_order": 0, "created_at": "..." },
      "source": { "id": 1, "name": "微信公众号", "created_at": "..." }
    }
  ],
  "total": 100
}
```

### POST /articles
创建文章。

**请求体**
```json
{
  "title": "标题",
  "summary": "简介",
  "content": "Markdown 正文",
  "source_url": "https://...",
  "source_id": 1,
  "author": "张三",
  "published_at": "2026-03-20T10:00:00Z",
  "category_id": 1
}
```

**响应** `201`

### GET /articles/{id}
获取文章详情。

**响应** `200`

### PUT /articles/{id}
修改文章。

**响应** `200`

### DELETE /articles/{id}
删除文章。

**响应** `204`

> Access Key 管理接口已迁移至独立路由，参见 [admin-access-key.md](admin-access-key.md)
