# Plan 023 - Tick 补打卡功能

## 背景

用户有时会忘记当天打卡，希望事后可以补录。
采用**方案 A**：补打卡得 0 分，不影响历史积分，但修复视觉记录，且后续新打卡的 streak 将从补好的连续数自然接续。

## 核心规则

- 补打卡标记 `is_makeup = true`，`points_earned` 固定为 0
- 补打卡只能针对**过去**的周期，不能补当前或未来周期
- 补打卡的周期必须在任务的 `start_date` 之后
- 同一周期只能有一条记录（已有普通打卡的周期不能补打）
- streak 计算不区分 makeup，自然串联（补完后，后续新打卡可获得正确的连续积分）
- 补打卡日志在日历和记录列表中有视觉区分（半透明/灰色调）

## 涉及文件

### 后端
- `backend/app/models/tick.py` — `TickLog` 增加 `is_makeup: bool`
- `backend/alembic/versions/xxxx_add_is_makeup_to_tick_logs.py` — 迁移脚本
- `backend/app/schemas/tick.py` — `TickLogOut` 增加 `is_makeup` 字段；新增 `MakeupTickCreate` schema
- `backend/app/services/tick.py` — 新增 `makeup_tick()` 函数
- `backend/app/api/admin/tick.py` — 新增 `POST /tasks/{task_id}/makeup` 路由

### 前端
- `frontend/admin/src/views/tick/TickView.vue` — 补打卡入口 + 补打卡样式

---

## 详细改动

### 1. 数据库模型

`TickLog` 新增字段：

```python
is_makeup: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
```

### 2. 迁移脚本

```python
op.add_column('tick_logs', sa.Column('is_makeup', sa.Boolean(), nullable=False, server_default='false'))
```

### 3. Schema

新增：
```python
class MakeupTickCreate(BaseModel):
    period_key: str   # 例如 "2026-04-08"，由前端根据日历日期生成
    note: Optional[str] = None
```

`TickLogOut` 增加 `is_makeup: bool = False`

### 4. Service - `makeup_tick()`

```python
def makeup_tick(db, task, user_id, period_key, note=None):
    # 验证 period_key 格式与频率匹配
    # 验证 period_key < 当前周期（不能补当前或未来）
    # 验证 period_key 未有记录（UniqueConstraint 会兜底，但提前给友好提示）
    # 写入 TickLog(is_makeup=True, points_earned=0, ...)
```

### 5. API 路由

```
POST /admin/tick/tasks/{task_id}/makeup
Body: { period_key: "2026-04-08", note?: "..." }
```

验证：
- 任务属于当前用户
- 任务未归档
- `period_key` 是过去的周期
- 该周期无记录

### 6. 前端入口 — 日历格子点击

在日历视图中，点击"未打卡（missed）"的格子，弹出一个小操作浮层：

```
┌─────────────────────┐
│  2026-04-08  未打卡  │
│                     │
│  [补打卡]           │
│  (补打卡不计积分)    │
└─────────────────────┘
```

- 点击格子 → 小弹窗（不抢眼，小型 popover）
- 已打卡的格子不触发此弹窗（维持原 tooltip 逻辑）
- 确认后调用 API，成功则刷新日历数据

### 7. 前端样式区分

补打卡印章：
- `opacity: 0.45`
- 带一个小斜纹或虚线边框，区别于正常打卡的实色

日志记录列表中补打卡条目：
- 右侧加一个小标签 `补打` （灰色 badge）
- `points_earned` 不显示或显示 `+0`

---

## 不在本次范围内

- 不做补打卡限制次数（如每月只能补 X 次）
- 不重新计算历史积分
- 不做移动端适配（移动端暂无 tick 模块）
