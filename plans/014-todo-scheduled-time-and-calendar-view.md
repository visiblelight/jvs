# 014 - ToDo 执行时间 & 日历视图 (Scheduled Time & Calendar View)

## 背景 (Context)

当前 ToDo 事项只有一个 `due_date`（截止时间），适用于"在某个日期前完成"这类场景。但在实际使用中，许多事项是有**明确执行时间点**的，例如：

- "3月30日上午10点和朋友见面"
- "4月2日下午3点参加项目评审会"

对于这类事项，用户不仅需要知道**它即将发生**，更需要明确知道**它在什么时候发生**。因此需要：
1. 为事项新增一个"执行时间"字段（`scheduled_at`）
2. 提供日历视图，直观展示事项在时间轴上的分布

---

## 一、数据层改造 (Backend)

### 1.1 模型变更 — `TodoItem`

在 `backend/app/models/todo.py` 的 `TodoItem` 中新增字段：

```python
scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
```

**语义区分：**
| 字段 | 含义 | 举例 |
|------|------|------|
| `due_date` | 截止时间 — 在此之前完成即可 | "4月1日前提交报告" |
| `scheduled_at` | 执行时间 — 在这个时间点执行 | "3月30日10:00见朋友" |

一个事项可以同时拥有 `due_date` 和 `scheduled_at`，也可以只有其中一个或两者皆无。

### 1.2 Alembic 迁移

新建迁移脚本，为 `todo_items` 表添加 `scheduled_at` 列（`DateTime, nullable=True`）。

### 1.3 Schema 变更 — `schemas/todo.py`

- `TodoItemCreate`：新增 `scheduled_at: Optional[datetime] = None`
- `TodoItemUpdate`：新增 `scheduled_at: Optional[datetime] = None`
- `TodoItemOut`：新增 `scheduled_at: Optional[datetime]`

### 1.4 API 新增 — 日历查询接口

在 `backend/app/api/admin/todo.py` 新增专用日历接口：

```
GET /admin/todo/items/calendar?start=2026-03-01T00:00:00&end=2026-04-01T00:00:00
```

**参数：**
- `start` (datetime, required)：时间窗口起点
- `end` (datetime, required)：时间窗口终点

**查询逻辑：**
返回所有满足以下条件之一的**未删除**事项：
- `due_date` 落在 `[start, end)` 范围内
- `scheduled_at` 落在 `[start, end)` 范围内

**返回结构：**
```json
{
  "items": [
    {
      "id": 1,
      "title": "提交报告",
      "due_date": "2026-04-01T00:00:00",
      "scheduled_at": null,
      "status": "pending",
      "priority": 4,
      "tags": [...]
    },
    {
      "id": 2,
      "title": "和朋友见面",
      "due_date": null,
      "scheduled_at": "2026-03-30T10:00:00",
      "status": "pending",
      "priority": 3,
      "tags": [...]
    }
  ]
}
```

### 1.5 Service 变更 — `services/todo.py`

新增 `get_calendar_items(db, user_id, start, end)` 方法：

```python
from sqlalchemy import or_, and_

def get_calendar_items(db, user_id, start, end):
    return db.query(TodoItem).filter(
        TodoItem.user_id == user_id,
        TodoItem.is_deleted == False,
        or_(
            and_(TodoItem.due_date != None, TodoItem.due_date >= start, TodoItem.due_date < end),
            and_(TodoItem.scheduled_at != None, TodoItem.scheduled_at >= start, TodoItem.scheduled_at < end),
        )
    ).order_by(TodoItem.scheduled_at, TodoItem.due_date).all()
```

---

## 二、前端改造 (Frontend)

### 2.1 API 层 — `api/todo.js`

新增：
```javascript
export const getCalendarItems = (params) => request.get('/admin/todo/items/calendar', { params })
```

### 2.2 表单改造 — `TodoFormDrawer.vue`

在截止日期字段旁边，新增"执行时间"输入框：

```
┌─────────────────────┬─────────────────────┐
│ 📅 分栏分类         │ 📅 截止日期          │
├─────────────────────┼─────────────────────┤
│ 🕐 执行时间         │                     │
└─────────────────────┴─────────────────────┘
```

- 使用 `datetime-local` 输入类型
- Label 标注为"执行时间"，并附一行提示文案："事项将在此时间点执行"

### 2.3 详情面板改造 — `TodoDetail.vue`

在"截止时间"行下方新增"执行时间"展示行：
- 如果 `scheduled_at` 有值，展示时间并以🕐图标区分
- 展示格式与截止时间一致

### 2.4 列表改造 — `TodoList.vue`

在事项的 badges 区域：
- 如果事项有 `scheduled_at`，新增一个带🕐标记的时间 badge
- 与 `due_date` 的📅标记做视觉区分（使用不同颜色/图标）

### 2.5 日历视图 — `TodoCalendarView.vue`（新建）

这是本次最核心的新增组件。

#### 整体布局

```
┌──────────────────────────────────────────────┐
│  日历视图                                      │
│  ◀ 2026年3月 ▶         [今日] [周] [月] [年]   │
├──────────────────────────────────────────────┤
│  日   一   二   三   四   五   六              │
│  ...                                          │
│  26  27  28  29  30  31                       │
│  ┌──────┐                                     │
│  │🕐 见面│                                     │
│  │📅 报告│                                     │
│  └──────┘                                     │
│  ...                                          │
└──────────────────────────────────────────────┘
```

#### 视图切换模式

| 模式 | 内容 | 导航 |
|------|------|------|
| **今日** | 按时间线展示今天的事项，类似议程视图 | 左右切换到前一天/后一天 |
| **本周** | 7列显示，每列一天，每天内列出事项 | 左右切换到上一周/下一周 |
| **本月** | 标准月历网格，每个日期格内展示事项缩略条 | 左右切换到上一月/下一月 |
| **本年** | 12个月的缩略网格，每个月显示事项数量热度 | 左右切换到上一年/下一年 |

#### 事项类型视觉区分

在日历上，两种类型的事项需要有明确的视觉区分：

- **执行时间事项**（`scheduled_at`）：使用 **蓝色/靛蓝色** 条带 + 🕐 图标前缀，配以精确时间"10:00 见朋友"
- **截止时间事项**（`due_date`）：使用 **橙色/琥珀色** 条带 + 📅 图标前缀，配以"截止: 提交报告"

如果一个事项**同时具有**两个时间，它会在日历上出现两次（分别在各自的时间点），但样式有所区分。

#### 交互

- 点击日历中的事项条可以在右侧 `TodoDetail` 面板中展示详情
- 未来可扩展：点击空白日期格可快速新建事项并自动预填该日期

### 2.6 路由/视图切换集成 — `TodoView.vue`

在 `TodoView.vue` 中增加「列表/日历」视图切换按钮：

```
┌─────────────┬────────────┬─────────────────┐
│  Sidebar    │ [列表][日历]│   Detail        │
│             │  内容区域   │                 │
│             │            │                 │
└─────────────┴────────────┴─────────────────┘
```

- 顶部添加两个视图切换 Tab（列表视图 / 日历视图）
- 默认展示列表视图（现有的 `TodoList`）
- 切换到日历视图时，中间区域替换为 `TodoCalendarView`
- 侧边栏和详情面板保持不变，日历中点击事项同样联动详情面板

### 2.7 Store 变更 — `stores/todo.js`

新增：
- `calendarItems` ref：存储日历视图的事项数据
- `calendarRange` ref：存储当前日历的起止时间范围
- `fetchCalendarItems(start, end)` 方法：调用日历接口

---

## 三、影响评估

### 后端变更文件
| 文件 | 变更类型 |
|------|---------|
| `backend/app/models/todo.py` | 修改 — 新增 `scheduled_at` 字段 |
| `backend/app/schemas/todo.py` | 修改 — Create/Update/Out 新增字段 |
| `backend/app/services/todo.py` | 修改 — 新增 `get_calendar_items` 方法 |
| `backend/app/api/admin/todo.py` | 修改 — 新增 `/items/calendar` 接口 |
| `backend/alembic/versions/xxx.py` | 新增 — 迁移脚本 |

### 前端变更文件
| 文件 | 变更类型 |
|------|---------|
| `frontend/admin/src/api/todo.js` | 修改 — 新增 `getCalendarItems` |
| `frontend/admin/src/stores/todo.js` | 修改 — 新增日历相关 state 和 action |
| `frontend/admin/src/views/todo/TodoFormDrawer.vue` | 修改 — 表单新增执行时间字段 |
| `frontend/admin/src/views/todo/TodoDetail.vue` | 修改 — 详情面板展示执行时间 |
| `frontend/admin/src/views/todo/TodoList.vue` | 修改 — 列表新增执行时间 badge |
| `frontend/admin/src/views/todo/TodoView.vue` | 修改 — 增加列表/日历切换 |
| `frontend/admin/src/views/todo/TodoCalendarView.vue` | **新增** — 日历视图组件 |

### 不涉及的变更
- 移动端（`frontend/mobile`）：本次不涉及
- 其他模块（News、Auth 等）：不受影响
- 全局样式 `theme.css`：不需修改

---

## 四、实施顺序

1. **Phase 1 — 数据层**：模型 → 迁移 → Schema → Service → API（后端完整闭环）
2. **Phase 2 — 基础 UI**：表单新增字段 → 详情面板展示 → 列表 badge
3. **Phase 3 — 日历视图**：`TodoCalendarView` 组件开发 → 视图切换集成
4. **Phase 4 — 联调打磨**：日历点击联动详情、边界日期处理、响应式适配
