# 数据结构文档

本文档记录系统中所有数据库表的结构定义。

---

## users — 用户表

管理后台及系统用户信息。

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK, Auto Increment | — | 主键 |
| username | String(50) | Unique, Not Null, Index | — | 登录账号 |
| hashed_password | String(255) | Not Null | — | bcrypt 哈希密码 |
| is_active | Boolean | — | True | 是否启用 |
| is_superuser | Boolean | — | False | 是否超级管理员 |
| created_at | DateTime | — | now() | 创建时间（UTC） |
| updated_at | DateTime | — | now() | 更新时间（UTC），自动更新 |

---

## todo_categories — ToDo 分类表

支持嵌套子分类，按用户隔离。

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK, Auto Increment | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| parent_id | Integer | FK → todo_categories.id, Nullable | null | 父分类 ID，null 为顶级 |
| name | String(100) | Not Null | — | 分类名称 |
| sort_order | Integer | — | 0 | 排序权重 |
| created_at | DateTime | — | now() | 创建时间（UTC） |

---

## todo_tags — ToDo 标签表

用户自定义标签。

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK, Auto Increment | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| name | String(50) | Not Null | — | 标签名称 |
| color | String(20) | — | #1890ff | 标签颜色 |
| created_at | DateTime | — | now() | 创建时间（UTC） |

---

## todo_items — ToDo 事项表

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK, Auto Increment | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| title | String(200) | Not Null | — | 标题 |
| description | Text | Nullable | null | 描述 |
| priority | Integer | — | 3 | 优先级（1-5，1 最低 5 最高） |
| importance | Integer | — | 3 | 重要程度（1-5，1 最低 5 最高） |
| status | String(20) | — | pending | 状态：pending / paused / completed / archived |
| category_id | Integer | FK → todo_categories.id, Nullable, ON DELETE SET NULL | null | 所属分类 |
| due_date | DateTime | Nullable | null | 截止时间 |
| scheduled_at | DateTime | Nullable | null | 指定执行时间；设置后 due_date = scheduled_at |
| completed_at | DateTime | Nullable | null | 完成时间；status 变为 completed 时自动填充 |
| archived_at | DateTime | Nullable | null | 归档时间；status 变为 archived 时自动填充 |
| is_deleted | Boolean | — | False | 软删除标记；True 表示已移入垃圾桶 |
| deleted_at | DateTime | Nullable | null | 软删除时间 |
| created_at | DateTime | — | now() | 创建时间（UTC） |
| updated_at | DateTime | — | now() | 更新时间（UTC），自动更新 |

---

## todo_item_tags — ToDo 事项-标签关联表

多对多关联。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| todo_item_id | Integer | PK, FK → todo_items.id, ON DELETE CASCADE | 事项 ID |
| tag_id | Integer | PK, FK → todo_tags.id, ON DELETE CASCADE | 标签 ID |

---

## news_categories — 新闻分类表

用户自定义新闻分类。user_id + name 联合唯一。

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK, Auto Increment | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| name | String(100) | Not Null | — | 分类名称 |
| sort_order | Integer | — | 0 | 排序权重 |
| created_at | DateTime | — | now() | 创建时间（UTC） |

---

## news_sources — 新闻来源表

用户自定义新闻来源（如：微信公众号、纽约时报等）。user_id + name 联合唯一。

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK, Auto Increment | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| name | String(100) | Not Null | — | 来源名称 |
| created_at | DateTime | — | now() | 创建时间（UTC） |

---

## news_articles — 新闻文章表

Markdown 格式文章，支持全文搜索。

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK, Auto Increment | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| title | String(300) | Not Null, Index | — | 文章标题 |
| summary | String(200) | Nullable | null | 简介 |
| content | Text | Not Null | — | 完整原文（Markdown） |
| source_url | String(500) | Nullable | null | 文章来源 URL |
| source_id | Integer | FK → news_sources.id, Nullable, ON DELETE SET NULL | null | 文章来源 |
| author | String(100) | Nullable | null | 作者 |
| published_at | DateTime | Nullable, Index | null | 文章发表时间 |
| category_id | Integer | FK → news_categories.id, Nullable, ON DELETE SET NULL | null | 所属分类 |
| created_at | DateTime | — | now() | 入库时间（UTC） |
| updated_at | DateTime | — | now() | 更新时间（UTC），自动更新 |

---

## access_keys — 开放 API 密钥表

用于 Agent 通过开放 API 提交数据的鉴权密钥，每个 Key 归属一个用户。

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK, Auto Increment | — | 主键 |
| user_id | Integer | FK → users.id, Not Null, Index | — | 所属用户 |
| name | String(100) | Not Null | — | 密钥名称（标识用途） |
| key | String(64) | Unique, Not Null, Index | secrets.token_hex(32) | 密钥值 |
| scopes | Text | Not Null | `"[]"` | JSON 格式的权限列表，如 `["news:create"]` |
| is_active | Boolean | — | True | 是否启用 |
| created_at | DateTime | — | now() | 创建时间（UTC） |
