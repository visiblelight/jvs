# 管理后台 — 打卡接口

Base Path: `/api/admin/tick`

需要登录 Token 且拥有 `tick` 板块权限。

---

## GET /tasks

列出当前用户的打卡任务。

**Query 参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| is_archived | bool | 过滤归档状态；不传则返回全部 |

**成功响应** (200):
```json
{
  "items": [
    {
      "id": 1,
      "title": "跳绳",
      "description": null,
      "frequency": "daily",
      "frequency_config": {"time": "20:00"},
      "start_date": "2026-04-01",
      "end_date": null,
      "enable_quality": false,
      "enable_points": true,
      "points_rule": [{"streak": 1, "points": 1}, {"streak": 3, "points": 3}],
      "is_archived": false,
      "created_at": "2026-04-01T00:00:00Z",
      "updated_at": "2026-04-01T00:00:00Z",
      "total_ticks": 5,
      "current_streak": 3,
      "total_points": 10,
      "ticked_this_period": true
    }
  ],
  "total": 1
}
```

---

## POST /tasks

创建打卡任务。

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 任务标题 |
| description | string | 否 | 描述（Markdown） |
| frequency | string | 是 | `daily` / `weekly` / `monthly` |
| frequency_config | object | 否 | 具体时间配置 |
| start_date | date | 是 | 开始日期 |
| end_date | date | 否 | 结束日期 |
| enable_quality | bool | 否 | 启用质量评价，默认 false |
| enable_points | bool | 否 | 启用积分，默认 false |
| points_rule | array | 否 | 阶梯积分规则 `[{"streak": N, "points": P}]` |

**frequency_config 格式**:
- daily: `{"time": "20:00"}`
- weekly: `{"day_of_week": 1, "time": "20:00"}` (1=周一…7=周日)
- monthly: `{"day_of_month": 8, "time": "20:00"}`

**成功响应** (201): `TickTaskOut`

---

## GET /tasks/{task_id}

获取任务详情（含统计字段）。返回 `TickTaskOut`。

---

## PUT /tasks/{task_id}

编辑任务（增量更新）。返回 `TickTaskOut`。

---

## DELETE /tasks/{task_id}

删除任务。级联删除所有打卡日志。返回 `204 No Content`。

---

## POST /tasks/{task_id}/tick

执行打卡。

**请求体** (JSON，可为空 `{}`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| quality | int (1-5) | 否 | 打卡质量评价 |
| note | string | 否 | 备注（Markdown） |

**成功响应** (200):
```json
{
  "log": {
    "id": 1,
    "task_id": 1,
    "ticked_at": "2026-04-06T12:00:00Z",
    "period_key": "2026-04-06",
    "quality": 4,
    "note": "今天完成得不错",
    "points_earned": 3,
    "created_at": "2026-04-06T12:00:00Z"
  },
  "current_streak": 3,
  "total_points": 15
}
```

**失败响应**:

| 状态码 | detail |
|--------|--------|
| 400 | 当前周期已打卡 |
| 400 | 任务已归档，无法打卡 |
| 400 | 任务尚未开始 |
| 400 | 任务已结束 |

---

## DELETE /tasks/{task_id}/tick

撤销当前周期的打卡。删除日志记录，退还积分。返回 `204 No Content`。

**失败响应**:

| 状态码 | detail |
|--------|--------|
| 400 | 当前周期未打卡 |

---

## GET /tasks/{task_id}/logs

获取打卡日志列表，按时间倒序。

**Query 参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页条数（1-100） |

**成功响应** (200):
```json
{
  "items": [
    {
      "id": 1,
      "task_id": 1,
      "ticked_at": "2026-04-06T12:00:00Z",
      "period_key": "2026-04-06",
      "quality": 4,
      "note": "备注",
      "points_earned": 3,
      "created_at": "2026-04-06T12:00:00Z"
    }
  ],
  "total": 1
}
```
