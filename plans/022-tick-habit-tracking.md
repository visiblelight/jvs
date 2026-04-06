# Plan 022：打卡（Tick）板块

## 需求分析

### 核心概念
打卡板块用于追踪习惯养成。用户创建**打卡任务**（如"跳绳"），按照设定的周期（每天/每周/每月）进行打卡，每次打卡产生一条**打卡日志**。

### 打卡任务属性
| 属性 | 说明 |
|------|------|
| 标题 | 如"跳绳" |
| 描述 | 详细说明，Markdown |
| 周期频率 | daily / weekly / monthly |
| 具体执行时间 | daily: 可选时间 (HH:MM)；weekly: 星期几+可选时间；monthly: 几号+可选时间 |
| 开始/结束日期 | 任务的有效期 |
| 打卡质量 | 可选功能开关；启用后打卡时可评 1-5 星 |
| 积分 | 可选功能开关；支持阶梯式连续打卡加分 |

### 阶梯积分规则
配置示例：`[{"streak": 1, "points": 1}, {"streak": 2, "points": 2}, {"streak": 3, "points": 3}]`
- 连续第 1 天打卡得 1 分，第 2 天得 2 分，第 3 天及以后每次得 3 分
- 中断一天后重新从第 1 级开始计算

### 打卡日志属性
| 属性 | 说明 |
|------|------|
| 打卡时间 | 打卡的时间点 |
| 质量评价 | 1-5 星（任务启用时） |
| 备注 | 可选，Markdown |
| 获得积分 | 本次打卡得分 |

### 关键业务规则
1. **一个周期只能打一次卡**：每日任务打完今天的，要到明天 0:00 后才能再打；每周任务打完本周的要等下周一；每月同理
2. **允许撤销打卡**：删除本次日志、退还积分，然后可以重新打卡
3. **打卡判定**：打卡不校验具体执行时间（如"晚上 8 点"），具体时间仅作为展示提醒用途；校验的是周期边界（日/周/月）

---

## 数据模型设计

### tick_tasks（打卡任务表）

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK | auto | 主键 |
| user_id | Integer | FK→users.id, Index | — | 所属用户 |
| title | String(200) | Not Null | — | 任务标题 |
| description | Text | Nullable | null | 任务描述（Markdown） |
| frequency | String(10) | Not Null | — | 周期频率：daily / weekly / monthly |
| frequency_config | JSON | Not Null | `{}` | 具体执行时间配置（见下） |
| start_date | Date | Not Null | — | 有效期开始日期 |
| end_date | Date | Nullable | null | 有效期结束日期（null=永久） |
| enable_quality | Boolean | — | False | 是否启用打卡质量评价 |
| enable_points | Boolean | — | False | 是否启用积分 |
| points_rule | JSON | Not Null | `[]` | 阶梯积分规则 |
| is_archived | Boolean | — | False | 是否已归档（软停用） |
| created_at | DateTime | — | now() | 创建时间（UTC） |
| updated_at | DateTime | — | now() | 更新时间（UTC） |

**frequency_config 格式**：
- daily: `{"time": "20:00"}` （time 可选）
- weekly: `{"day_of_week": 1, "time": "20:00"}` （day_of_week: 1=周一…7=周日；time 可选）
- monthly: `{"day_of_month": 8, "time": "20:00"}` （day_of_month: 1-31；time 可选）

**points_rule 格式**：
```json
[
  {"streak": 1, "points": 1},
  {"streak": 2, "points": 2},
  {"streak": 3, "points": 3}
]
```
按 streak 升序排列，超过最大 streak 后沿用最后一档的分值。

### tick_logs（打卡日志表）

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK | auto | 主键 |
| user_id | Integer | FK→users.id, Index | — | 所属用户 |
| task_id | Integer | FK→tick_tasks.id, ON DELETE CASCADE | — | 关联任务 |
| ticked_at | DateTime | Not Null | — | 打卡时间 |
| period_key | String(10) | Not Null | — | 所属周期标识（见下） |
| quality | Integer | Nullable | null | 打卡质量 1-5 |
| note | Text | Nullable | null | 备注（Markdown） |
| points_earned | Integer | Not Null | 0 | 本次获得积分 |
| created_at | DateTime | — | now() | 创建时间（UTC） |

**period_key** 用于唯一标识一个打卡周期，防止重复打卡：
- daily: `"2026-04-06"` （日期字符串）
- weekly: `"2026-W15"` （ISO 年-周）
- monthly: `"2026-04"` （年-月）

联合唯一约束：`(task_id, period_key)` — 保证每个任务每个周期最多一条日志。

---

## API 设计

### 管理后台 `/api/admin/tick`

路由级别挂载 `require_module("tick")`。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /tasks | 列出当前用户的打卡任务（支持 `?is_archived=false` 过滤） |
| POST | /tasks | 创建打卡任务 |
| GET | /tasks/{task_id} | 获取任务详情（含统计：总打卡次数、当前连续天数、累计积分） |
| PUT | /tasks/{task_id} | 编辑任务 |
| DELETE | /tasks/{task_id} | 删除任务（硬删，级联删日志） |
| POST | /tasks/{task_id}/tick | 执行打卡（body: quality?, note?） |
| DELETE | /tasks/{task_id}/tick | 撤销当前周期的打卡 |
| GET | /tasks/{task_id}/logs | 获取打卡日志列表（分页，按时间倒序） |

### 关键接口说明

**POST /tasks/{task_id}/tick（执行打卡）**：
1. 验证任务属于当前用户、有效期内、未归档
2. 计算当前 period_key，检查是否已有日志（有则 400 "当前周期已打卡"）
3. 计算连续打卡天数（streak），根据 points_rule 计算得分
4. 创建 tick_log 记录
5. 返回日志详情 + 当前 streak + 累计积分

**DELETE /tasks/{task_id}/tick（撤销打卡）**：
1. 找到当前周期的日志记录（没有则 400 "当前周期未打卡"）
2. 删除该日志
3. 返回 204

---

## 连续打卡（streak）计算逻辑

计算某任务从当前周期向前的连续完成周期数：

```
streak = 0
从当前周期 P 开始：
  if P 存在日志 → streak += 1，P = 上一个周期，继续
  else → 停止
return streak
```

周期回溯规则：
- daily: 前一天
- weekly: 前一周
- monthly: 前一月

注意：当前周期未打卡时，从上一个周期开始检查（用于计算"若现在打卡，streak 是多少"）。

---

## 实施步骤

### Step 1：后端 — 数据模型与迁移
- 新建 `backend/app/models/tick.py`（TickTask, TickLog）
- Alembic 迁移创建 `tick_tasks` 和 `tick_logs` 表
- 在 `app/core/modules.py` 注册 `tick` 板块（sort_order: 15，排在 todo 之后）
- 在 `tests/conftest.py` 中 `import app.models.tick`

### Step 2：后端 — Pydantic Schemas
- 新建 `backend/app/schemas/tick.py`
- TickTaskCreate / TickTaskUpdate / TickTaskOut（含统计字段：total_ticks, current_streak, total_points, ticked_today/this_period）
- TickLogCreate（quality?, note?）/ TickLogOut
- TickTaskListOut（带 items + total）

### Step 3：后端 — Service 层
- 新建 `backend/app/services/tick.py`
- CRUD：get_tasks / create_task / update_task / delete_task
- 核心逻辑：do_tick / undo_tick / get_logs
- 辅助函数：compute_period_key / compute_streak / compute_points

### Step 4：后端 — Admin API 路由
- 新建 `backend/app/api/admin/tick.py`
- 注册到 `backend/app/api/admin/__init__.py`
- 路由级依赖 `require_module("tick")`

### Step 5：后端 — 测试
- 新建 `backend/tests/test_tick.py`
- 覆盖：任务 CRUD、打卡、撤销打卡、重复打卡拒绝、连续打卡积分计算、周期判定、权限拦截

### Step 6：前端 Admin — API + Store
- 新建 `frontend/admin/src/api/tick.js`
- 新建 `frontend/admin/src/stores/tick.js`

### Step 7：前端 Admin — 页面与路由
- 新建 `frontend/admin/src/views/tick/TickView.vue`
  - 左侧：任务列表（活跃/已归档切换）
  - 右侧：选中任务的详情面板
    - 任务信息（频率、有效期、积分规则）
    - 今日/本期打卡状态 + 打卡/撤销按钮
    - 连续打卡天数、累计积分统计
    - 历史日志列表
  - 新建/编辑任务：Drawer 表单
- 路由 `{ path: 'tick', meta: { module: 'tick' } }`
- AdminLayout 菜单加入 tick 条目

### Step 8：前端 Mobile — API + Store
- 新建 `frontend/mobile/src/api/tick.js`
- 新建 `frontend/mobile/src/stores/tick.js`

### Step 9：前端 Mobile — 页面与路由
- 新建 `frontend/mobile/src/views/tick/TickView.vue`
  - 今日打卡清单卡片式布局
  - 每个任务卡显示：标题、频率标签、streak 和积分、打卡/已完成状态
  - 点击可展开查看详情/评价质量/写备注
  - 支持撤销打卡
- 路由 `{ path: 'tick', meta: { module: 'tick' } }`
- HomeView 增加打卡板块入口图标
- HomeView 统计条增加"今日打卡"计数

### Step 10：文档更新
- 新建 `docs/api/admin-tick.md`
- 更新 `docs/database/schema.md`：增加 tick_tasks、tick_logs 表说明

### Step 11：Alembic 数据迁移
- 迁移中将 `tick` module 授权给所有已有非超管用户（与 021 同策略）

---

## 设计决策说明

1. **period_key + 联合唯一约束** 而非"查询最近一条日志的时间差"：
   - 更可靠地防止重复打卡
   - 查询简单（直接 filter by period_key）
   - 格式标准化便于 streak 计算

2. **积分存储在日志记录上**（而非实时计算累加到任务表）：
   - 撤销打卡时无需反向修改任务表
   - 累计积分 = `SUM(points_earned)` 即可
   - 每条日志自身完整，可追溯

3. **打卡任务使用硬删除**（非软删除）：
   - 打卡任务不同于 ToDo，没有"回收站/恢复"的需求
   - 归档（is_archived）已满足"暂停但保留历史"的场景
   - 硬删级联清除日志，数据干净

4. **具体执行时间仅作展示用途**：
   - 需求文档中的打卡限制以周期边界（0:00/周一/月初）为准
   - time 字段仅在前端显示为提醒信息，不作为打卡时间门槛

5. **frequency_config 和 points_rule 使用 JSON 字段**：
   - 灵活存储不同频率类型的配置
   - 避免为不同频率类型创建多张配置表
   - SQLAlchemy + SQLite 支持 JSON 类型

6. **tick 板块 sort_order = 15**：
   - 排在 todo(10) 之后、news(20) 之前
   - 打卡与待办都是日常效率工具，关联性强
