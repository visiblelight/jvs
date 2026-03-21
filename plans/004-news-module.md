# Plan 004 - 新闻板块

**日期**: 2026-03-19
**状态**: 待确认

---

## 零、多用户数据隔离原则

本项目为多用户系统，**所有业务资源必须关联 `user_id`，查询/操作时必须过滤当前用户**，确保用户间数据完全隔离。

本次涉及的所有新表（news_categories、news_sources、news_articles、access_keys）均包含 `user_id` 字段。开放 API 通过 Access Key 反查所属用户，提交的文章归属该用户。

> 已有模块 ToDo 已正确实现用户隔离，无需调整。

---

## 一、功能概述

新闻板块管理 Markdown 文章，文章来源有两种渠道：
1. 管理员在后台手动创建
2. Agent 通过开放 API 提交（使用 Access Key 鉴权，文章归属 Key 所属用户）

支持分类管理、来源管理、全文搜索。每个用户拥有独立的分类、来源和文章数据。

---

## 二、数据库设计

### 2.1 news_categories — 新闻分类表

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| name | String(100) | Not Null | — | 分类名称 |
| sort_order | Integer | — | 0 | 排序权重 |
| created_at | DateTime | — | now() | 创建时间 |

> user_id + name 联合唯一，同一用户不允许重名分类。

### 2.2 news_sources — 新闻来源表

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| name | String(100) | Not Null | — | 来源名称（如：微信公众号、纽约时报等） |
| created_at | DateTime | — | now() | 创建时间 |

> user_id + name 联合唯一。

### 2.3 news_articles — 新闻文章表

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| title | String(300) | Not Null, Index | — | 文章标题 |
| summary | String(200) | Nullable | null | 简介（100字以内） |
| content | Text | Not Null | — | 完整原文（Markdown） |
| source_url | String(500) | Nullable | null | 文章来源 URL |
| source_id | Integer | FK → news_sources.id, Nullable | null | 文章来源 |
| author | String(100) | Nullable | null | 作者 |
| published_at | DateTime | Nullable, Index | null | 文章发表时间 |
| category_id | Integer | FK → news_categories.id, Nullable | null | 所属分类 |
| created_at | DateTime | — | now() | 入库时间 |
| updated_at | DateTime | — | now() | 更新时间 |

### 2.4 access_keys — 开放 API 密钥表

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| name | String(100) | Not Null | — | 密钥名称（标识用途） |
| key | String(64) | Unique, Not Null, Index | — | 密钥值 |
| is_active | Boolean | — | True | 是否启用 |
| created_at | DateTime | — | now() | 创建时间 |

> Access Key 归属某个用户，通过该 Key 提交的数据自动关联该用户的 user_id。

### 2.5 全文搜索方案

**当前阶段（SQLite）**：使用 SQL `LIKE` 对 title、summary、content、author 进行模糊搜索，所有查询均带 `user_id` 过滤。

**未来迁移 PostgreSQL 后**：可切换为 `tsvector + GIN 索引` 实现高性能全文检索，搜索逻辑封装在 service 层，切换时只需修改 service 实现。

---

## 三、后端 API

### 3.1 管理后台接口 — `/api/admin/news`

所有接口均通过 JWT 鉴权获取 `current_user`，操作范围限定为该用户的数据。

#### 分类管理 — `/api/admin/news/categories`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取当前用户的全部分类 |
| POST | `/` | 创建分类（当前用户下） |
| PUT | `/{id}` | 修改分类（校验归属） |
| DELETE | `/{id}` | 删除分类（校验归属 + 检查关联文章） |

#### 来源管理 — `/api/admin/news/sources`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取当前用户的全部来源 |
| POST | `/` | 创建来源（当前用户下） |
| PUT | `/{id}` | 修改来源（校验归属） |
| DELETE | `/{id}` | 删除来源（校验归属 + 检查关联文章） |

#### 文章管理 — `/api/admin/news/articles`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 文章列表（当前用户，分页 + 按分类/来源/关键字筛选） |
| POST | `/` | 创建文章（当前用户下） |
| GET | `/{id}` | 获取文章详情（校验归属） |
| PUT | `/{id}` | 修改文章（校验归属） |
| DELETE | `/{id}` | 删除文章（校验归属） |

### 3.2 开放 API — `/api/open/news`

#### Access Key 鉴权流程

1. 请求头传递 `X-Access-Key: <key>`
2. 在 `core/deps.py` 中新增 `verify_access_key` 依赖：查 `access_keys` 表，校验 key 是否存在且 `is_active=True`
3. 返回该 Key 关联的 `User` 对象，后续操作的 `user_id` 来自此处

#### 开放接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/open/news/articles` | 提交文章（Agent 使用） |

请求体中 `source_name` 和 `category_name` 通过名称匹配该用户的来源/分类，不存在则自动创建（归属该 Key 的 user_id）。

---

## 四、前端实现

### 4.1 菜单新增

AdminLayout 侧栏新增第三个菜单项：**新闻**（`/news`）

### 4.2 新闻主页面 — `NewsView.vue`

采用**列表 + 详情**两栏布局：

```
┌────────────────────────────┬──────────────────────┐
│  左侧列表                   │  右侧文章详情         │
│  顶部：搜索框 + 筛选 + 新建  │  Markdown 渲染        │
│  文章卡片列表               │  元信息展示           │
│  分页                      │  编辑/删除操作         │
└────────────────────────────┴──────────────────────┘
```

### 4.3 页面组件拆分

| 组件 | 说明 |
|------|------|
| `NewsView.vue` | 新闻主页面，组织两栏布局 |
| `NewsList.vue` | 左侧文章列表（搜索 + 筛选 + 分页） |
| `NewsDetail.vue` | 右侧文章详情（Markdown 渲染 + 元信息） |
| `NewsFormModal.vue` | 新建/编辑文章弹窗（含 Markdown 编辑区域） |
| `NewsCategoryManager.vue` | 分类管理弹窗 |
| `NewsSourceManager.vue` | 来源管理弹窗 |

### 4.4 Markdown 渲染

使用 `marked` 库将 Markdown 内容渲染为 HTML，添加基本的排版样式。

---

## 五、涉及文件清单

```
backend/
├── app/
│   ├── models/
│   │   ├── news.py                  # 新增：新闻相关模型（3张表）
│   │   ├── access_key.py            # 新增：Access Key 模型
│   │   └── __init__.py              # 修改：导入新模型
│   ├── schemas/
│   │   ├── news.py                  # 新增：新闻相关 Schema
│   │   └── access_key.py            # 新增：Access Key Schema
│   ├── services/
│   │   └── news.py                  # 新增：新闻业务逻辑（含搜索）
│   ├── api/
│   │   ├── admin/
│   │   │   ├── news.py              # 新增：新闻管理路由
│   │   │   └── __init__.py          # 修改：注册 news 路由
│   │   └── open/
│   │       ├── news.py              # 新增：开放 API 路由
│   │       └── __init__.py          # 修改：注册路由
│   └── core/
│       └── deps.py                  # 修改：新增 verify_access_key 依赖
├── scripts/
│   └── init_access_key.py           # 新增：为 admin 用户生成初始 Access Key
└── main.py                          # 修改：挂载 open 路由

frontend/admin/
├── src/
│   ├── layouts/AdminLayout.vue      # 修改：新增菜单项
│   ├── api/news.js                  # 新增：新闻 API 封装
│   ├── stores/news.js               # 新增：新闻状态管理
│   ├── views/news/
│   │   ├── NewsView.vue             # 新增：新闻主页面
│   │   ├── NewsList.vue             # 新增：文章列表
│   │   ├── NewsDetail.vue           # 新增：文章详情（Markdown渲染）
│   │   ├── NewsFormModal.vue        # 新增：新建/编辑弹窗
│   │   ├── NewsCategoryManager.vue  # 新增：分类管理弹窗
│   │   └── NewsSourceManager.vue    # 新增：来源管理弹窗
│   └── router/index.js             # 修改：新增 news 路由
├── package.json                     # 修改：新增 marked 依赖

docs/
├── api/
│   ├── admin-news.md                # 新增：新闻管理接口文档
│   └── open-news.md                 # 新增：开放 API 接口文档
└── database/schema.md               # 修改：追加 4 张新表
```

---

## 六、执行顺序

1. 后端：Access Key 模型 + 鉴权依赖（verify_access_key → 返回 User）
2. 后端：新闻相关模型（3 张表，均含 user_id）→ 建表 → Schema → Service（含搜索，所有查询过滤 user_id）→ 管理 API → 开放 API
3. 后端：挂载路由 + 初始 Access Key 脚本（为 admin 用户生成）
4. 前端：安装 marked → API 封装 → Store → 新闻组件（6 个）→ 路由 + 菜单
5. 文档：更新数据结构文档 + 新增接口文档
