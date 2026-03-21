# Plan 003 - 左侧菜单 + ToDo 功能模块

**日期**: 2026-03-19
**状态**: 已完成

---

## 一、功能概述

1. 管理后台引入**左侧导航菜单 + 顶栏 + 内容区**的经典后台布局
2. 菜单包含两项：**首页**（Dashboard）和 **ToDo**
3. 实现完整的 ToDo 功能模块（多用户隔离），包括分类管理、标签管理、Todo CRUD

---

## 二、数据库设计

### 2.1 todo_categories — ToDo 分类表（支持嵌套）

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| parent_id | Integer | FK → todo_categories.id, Nullable | null | 父分类 ID，null 表示顶级 |
| name | String(100) | Not Null | — | 分类名称 |
| sort_order | Integer | — | 0 | 排序权重 |
| created_at | DateTime | — | now() | 创建时间 |

### 2.2 todo_tags — ToDo 标签表

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| name | String(50) | Not Null | — | 标签名称 |
| color | String(20) | — | #1890ff | 标签颜色 |
| created_at | DateTime | — | now() | 创建时间 |

### 2.3 todo_items — ToDo 事项表

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| title | String(200) | Not Null | — | 标题 |
| description | Text | Nullable | null | 描述 |
| priority | Integer | — | 3 | 优先级（1-5，1 最低 5 最高） |
| importance | Integer | — | 3 | 重要程度（1-5，1 最低 5 最高） |
| status | String(20) | — | pending | 状态：pending / paused / completed |
| category_id | Integer | FK → todo_categories.id, Nullable | null | 所属分类 |
| due_date | DateTime | Nullable | null | 截止时间 |
| completed_at | DateTime | Nullable | null | 完成时间 |
| created_at | DateTime | — | now() | 创建时间 |
| updated_at | DateTime | — | now() | 更新时间 |

### 2.4 todo_item_tags — ToDo 事项-标签关联表（多对多）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| todo_item_id | Integer | PK, FK → todo_items.id | 事项 ID |
| tag_id | Integer | PK, FK → todo_tags.id | 标签 ID |

---

## 三、后端 API

### 3.1 分类管理 — `/api/admin/todo/categories`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取当前用户的分类树 |
| POST | `/` | 创建分类（可指定 parent_id） |
| PUT | `/{id}` | 修改分类 |
| DELETE | `/{id}` | 删除分类（需检查是否有子分类或关联事项） |

### 3.2 标签管理 — `/api/admin/todo/tags`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取当前用户的全部标签 |
| POST | `/` | 创建标签 |
| PUT | `/{id}` | 修改标签 |
| DELETE | `/{id}` | 删除标签 |

### 3.3 ToDo 事项 — `/api/admin/todo/items`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取事项列表（支持按状态/分类/标签/优先级筛选，分页） |
| POST | `/` | 创建事项 |
| GET | `/{id}` | 获取事项详情 |
| PUT | `/{id}` | 修改事项 |
| DELETE | `/{id}` | 删除事项 |
| PATCH | `/{id}/status` | 快捷更新状态 |

---

## 四、前端实现

### 4.1 后台布局重构 — `AdminLayout.vue`

将当前的页面结构改为经典后台布局：

```
┌──────────────────────────────────────────┐
│  顶栏（标题 + 用户信息 + 退出）           │
├──────────┬───────────────────────────────┤
│          │                               │
│  左侧菜单 │       内容区                  │
│  ┌──────┐│    <router-view />            │
│  │ 首页  ││                               │
│  │ ToDo  ││                               │
│  └──────┘│                               │
│          │                               │
└──────────┴───────────────────────────────┘
```

- 左侧菜单固定宽度 200px，背景深色
- 当前激活菜单高亮
- 路由使用嵌套子路由，AdminLayout 为父路由

### 4.2 ToDo 主页面 — `TodoView.vue`

采用**三栏式布局**：

```
┌────────────┬──────────────────────┬──────────────┐
│ 左侧筛选栏  │   中间列表            │  右侧详情     │
│ 分类树      │   ToDo 条目列表       │  选中条目详情  │
│ 标签筛选    │   支持排序/筛选       │  编辑表单     │
│ 状态筛选    │                      │              │
└────────────┴──────────────────────┴──────────────┘
```

### 4.3 页面组件拆分

| 组件 | 说明 |
|------|------|
| `TodoView.vue` | ToDo 模块主页面，组织三栏布局 |
| `TodoSidebar.vue` | 左侧筛选面板（分类树 + 标签 + 状态） |
| `TodoList.vue` | 中间事项列表 |
| `TodoDetail.vue` | 右侧详情/编辑面板 |
| `TodoFormModal.vue` | 新建/编辑事项弹窗 |
| `CategoryManager.vue` | 分类管理弹窗（增删改 + 拖拽排序） |
| `TagManager.vue` | 标签管理弹窗 |

---

## 五、涉及文件清单

```
backend/
├── app/
│   ├── models/
│   │   ├── todo.py                 # 新增：ToDo 相关模型（4张表）
│   │   └── __init__.py             # 修改：导入新模型
│   ├── schemas/
│   │   └── todo.py                 # 新增：ToDo 相关 Schema
│   ├── services/
│   │   └── todo.py                 # 新增：ToDo 业务逻辑
│   ├── api/admin/
│   │   ├── todo.py                 # 新增：ToDo 路由（分类/标签/事项）
│   │   └── __init__.py             # 修改：注册 todo 路由

frontend/admin/src/
├── layouts/
│   └── AdminLayout.vue             # 新增：后台主布局（顶栏+侧栏+内容区）
├── views/
│   ├── DashboardView.vue           # 修改：移除自带顶栏，适配 Layout
│   └── todo/
│       ├── TodoView.vue            # 新增：ToDo 主页面
│       ├── TodoSidebar.vue         # 新增：左侧筛选面板
│       ├── TodoList.vue            # 新增：事项列表
│       ├── TodoDetail.vue          # 新增：详情/编辑面板
│       ├── TodoFormModal.vue       # 新增：新建/编辑弹窗
│       ├── CategoryManager.vue     # 新增：分类管理弹窗
│       └── TagManager.vue          # 新增：标签管理弹窗
├── api/
│   └── todo.js                     # 新增：ToDo 相关 API 封装
├── stores/
│   └── todo.js                     # 新增：ToDo 状态管理
└── router/index.js                 # 修改：嵌套路由（Layout 为父路由）

docs/
├── api/admin-todo.md               # 新增：ToDo 接口文档
└── database/schema.md              # 修改：追加 4 张新表
```

---

## 六、执行顺序

1. 后端：创建 4 张表的 Model → Alembic 迁移 → Schema → Service → API 路由
2. 前端：AdminLayout 布局组件 + 路由重构（嵌套路由）
3. 前端：DashboardView 适配新布局
4. 前端：ToDo API 封装 + Store
5. 前端：ToDo 页面组件（TodoView → Sidebar → List → Detail → FormModal → CategoryManager → TagManager）
6. 文档：更新数据结构文档 + 新增 ToDo 接口文档
