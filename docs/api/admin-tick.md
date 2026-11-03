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

## 周期与补录规则（Plan 024）

业务时区固定配置为 `Asia/Shanghai`，日界为上海午夜，周使用 ISO 周（周一至周日）。`/api/admin/auth/me` 返回 `business_timezone`；前端显示该时区并在业务午夜、恢复可见时刷新。

`period_key` 必须是匹配任务频率的有效日、ISO 周或月。补打卡仅接受过去周期，且与任务有效日期区间有交集（包括起止日所在的不完整周／月）；已归档任务拒绝补录。已结束但未归档的任务可以补录有效历史周期。补录固定 0 分，不重算历史积分，后续连续次数接续；普通打卡的阶梯积分采用不超过当前连续次数的最高阶梯。

`GET /api/admin/tick/logs` 新增 `date_basis=submitted|calendar`，默认 submitted：按业务时区的实际提交日期过滤。calendar 按所属周期与日期区间的交集返回，包含近期补录的历史记录及计算周／月完成态所需的日志。`ticked_at` 始终是实际提交的 UTC 时间点，`period_key` 是目标周期，不能混用。end_date 包含当天。

任务的 description、end_date 显式传 null 可清空。非空字段拒绝 null；结束日期不得早于开始日期。积分规则必须包含正整数 streak 和非负整数 points，从 streak=1 开始且阶梯不重复；每项最大 1000000。已有打卡记录时修改 frequency 返回 400。非法周期、重复打卡（含并发）返回 400，结构不合法的任务输入返回 422。
