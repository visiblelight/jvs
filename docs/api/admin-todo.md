# 管理后台 — ToDo 接口

Base Path: `/api/admin/todo`

所有接口需在请求头中携带 `Authorization: Bearer <token>`。

---

## 分类管理

### GET /categories

获取当前用户的分类树。

**成功响应** (200):

```json
[
  {
    "id": 1,
    "parent_id": null,
    "name": "工作",
    "sort_order": 0,
    "children": [
      { "id": 3, "parent_id": 1, "name": "项目A", "sort_order": 0, "children": [] }
    ]
  }
]
```

### POST /categories

创建分类。

**请求体**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 分类名称 |
| parent_id | int | 否 | 父分类 ID，不传为顶级 |
| sort_order | int | 否 | 排序权重，默认 0 |

### PUT /categories/{id}

修改分类。

**请求体**: 同 POST，所有字段可选。

### DELETE /categories/{id}

删除分类。

| 状态码 | 说明 |
|--------|------|
| 204 | 删除成功 |
| 400 | 存在子分类或关联事项，无法删除 |

---

## 标签管理

### GET /tags

获取当前用户的全部标签。

**成功响应** (200):

```json
[
  { "id": 1, "name": "紧急", "color": "#ff4d4f" }
]
```

### POST /tags

创建标签。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 标签名称 |
| color | string | 否 | 颜色，默认 #1890ff |

### PUT /tags/{id}

修改标签。字段同 POST，均可选。

### DELETE /tags/{id}

删除标签。返回 204。

---

## 事项管理

### GET /items

获取事项列表（分页 + 筛选）。

**Query 参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 按状态筛选：pending / paused / completed / archived（不传则默认排除 archived） |
| category_id | int | 按分类筛选 |
| tag_id | int | 按标签筛选 |
| priority | int | 按优先级筛选（1-5） |
| importance | int | 按重要程度筛选（1-5） |
| page | int | 页码，默认 1 |
| page_size | int | 每页数量，默认 50，最大 100 |

**成功响应** (200):

```json
{
  "items": [
    {
      "id": 1,
      "title": "完成报告",
      "description": "季度报告",
      "priority": 4,
      "importance": 5,
      "status": "pending",
      "category_id": 1,
      "due_date": "2026-03-20T00:00:00",
      "completed_at": null,
      "created_at": "2026-03-19T10:00:00",
      "updated_at": "2026-03-19T10:00:00",
      "tags": [{ "id": 1, "name": "紧急", "color": "#ff4d4f" }]
    }
  ],
  "total": 1
}
```

### POST /items

创建事项。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 标题 |
| description | string | 否 | 描述 |
| priority | int | 否 | 优先级 1-5，默认 3 |
| importance | int | 否 | 重要程度 1-5，默认 3 |
| category_id | int | 否 | 分类 ID |
| due_date | datetime | 否 | 截止时间 |
| tag_ids | int[] | 否 | 标签 ID 列表 |

### GET /items/{id}

获取事项详情。

### PUT /items/{id}

修改事项。字段同 POST，额外支持 `status` 和 `tag_ids`，均可选。

### DELETE /items/{id}

删除事项。返回 204。

### PATCH /items/{id}/status

快捷更新状态。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 是 | pending / paused / completed / archived（仅 completed 可设为 archived，archived 需先回到 completed） |
