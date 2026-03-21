# Plan 005 - 个人中心 & Access Key 管理

**日期**: 2026-03-20
**状态**: 待确认

---

## 一、功能概述

### 1.1 个人中心页面

点击侧栏左下角的用户头像区域，进入个人中心页面（`/profile`），包含：

1. **基本信息** — 显示用户名、账号创建时间等
2. **修改密码** — 输入旧密码 + 新密码进行密码修改
3. **Access Key 管理** — 管理开放 API 密钥及其权限

### 1.2 Access Key 管理

在个人中心页面内展示 Access Key 列表，支持：

- **创建** — 输入名称 + 勾选权限，生成新 Key（创建后完整显示一次，之后部分遮蔽）
- **删除** — 确认后删除
- **复制** — 一键复制 Key 到剪贴板
- **启用/禁用** — 切换 Key 的 is_active 状态
- **编辑权限** — 修改 Key 拥有的 API 权限

### 1.3 Access Key 权限体系

每个 Access Key 只拥有被明确授予的权限，不授予则无权调用。

**权限设计思路**：采用 **scope 字符串列表** 存储在 access_keys 表的 `scopes` 字段中（JSON 格式），每个 scope 对应一个开放 API 能力。这样做的好处是：
- 新增模块时只需注册新的 scope 定义，无需改表结构
- 简单直观，前端用 checkbox 列表即可配置
- 开放 API 端通过依赖注入校验当前 Key 是否持有所需 scope

**当前可用的 scope 定义**（随模块增长持续扩展）：

| Scope | 说明 | 对应接口 |
|-------|------|----------|
| `news:create` | 提交新闻文章 | `POST /api/open/news/articles` |

> 后续新增模块的开放 API 时，只需在权限定义注册表中追加新 scope 即可。

**鉴权流程改造**：

1. `verify_access_key` 依赖不变，仍返回 User 对象
2. 新增 `require_scope(scope: str)` 依赖工厂，返回一个依赖函数：
   - 接收 `X-Access-Key` header → 查 AccessKey → 校验 `is_active` → 校验 scope 是否在 `scopes` 列表中
   - 不满足则返回 `403 Forbidden`
3. 开放 API 路由使用 `require_scope("news:create")` 替代原来的 `verify_access_key`

---

## 二、数据库改动

### 2.1 access_keys 表新增 scopes 字段

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| scopes | Text | Not Null | `"[]"` | JSON 格式的权限列表，如 `["news:create"]` |

> SQLite 和 PostgreSQL 均支持 Text 存储 JSON。读写时通过 Python 的 `json.loads/dumps` 序列化。

### 2.2 权限定义注册表

在 `app/core/scopes.py` 中维护一份全局 scope 定义：

```python
AVAILABLE_SCOPES = {
    "news:create": "提交新闻文章",
}
```

后端创建/更新 Key 时校验 scope 合法性，前端从接口获取可选 scope 列表用于展示 checkbox。

---

## 三、后端改动

### 3.1 新增修改密码接口

`PUT /api/admin/auth/password`

```json
{ "old_password": "旧密码", "new_password": "新密码" }
```

- 校验旧密码正确性
- 新密码最少 6 位
- 更新 hashed_password

### 3.2 迁移 Access Key 路由

将 Access Key 的 CRUD 接口从 `api/admin/news.py` 迁移到 `api/admin/access_key.py`，路由前缀改为 `/api/admin/access-keys`。

### 3.3 新增获取可用 scope 列表接口

`GET /api/admin/access-keys/scopes`

返回系统中所有可用的 scope 定义，供前端渲染 checkbox 列表。

```json
[
  { "scope": "news:create", "label": "提交新闻文章" }
]
```

### 3.4 Access Key CRUD 调整

- **创建** 请求体新增 `scopes: list[str]`，后端校验每个 scope 是否在 `AVAILABLE_SCOPES` 中
- **更新** 请求体新增 `scopes: Optional[list[str]]`
- **响应** 新增 `scopes` 字段

### 3.5 改造开放 API 鉴权

- 新增 `app/core/scopes.py`：scope 定义 + `require_scope()` 依赖工厂
- 修改 `app/api/open/news.py`：使用 `require_scope("news:create")` 替代 `verify_access_key`

---

## 四、前端改动

### 4.1 侧栏头像区域

将侧栏底部的 `user-badge` 区域改为可点击，点击后导航到 `/profile`。当前在 `/profile` 页面时高亮显示。

### 4.2 个人中心页面

布局为单栏卡片式：

```
┌──────────────────────────────────┐
│  基本信息卡片                      │
│  用户名 · 创建时间                  │
├──────────────────────────────────┤
│  修改密码卡片                      │
│  旧密码 / 新密码 / 确认密码 / 提交  │
├──────────────────────────────────┤
│  Access Key 管理卡片               │
│  [创建新 Key]                     │
│  Key 列表：名称 | 权限 | Key值 | 状态 | 操作 │
└──────────────────────────────────┘
```

### 4.3 组件拆分

| 组件 | 说明 |
|------|------|
| `ProfileView.vue` | 个人中心主页面，组织各卡片 |
| `AccessKeyManager.vue` | Access Key 列表 + 创建/删除/复制/启停/权限编辑 |

### 4.4 Access Key 交互细节

- **创建**：点击"创建" → 弹窗输入名称 + checkbox 勾选权限 → 确认后生成 → 弹出完整 Key 值提示用户复制保存（仅此一次完整显示）
- **列表显示**：Key 值默认显示前 8 位 + `****` 遮蔽，点击眼睛图标可切换显示完整值
- **权限标签**：每个 Key 的权限以小标签形式展示，点击"编辑权限"可弹窗修改
- **复制**：点击复制按钮，使用 `navigator.clipboard.writeText()` 复制，显示"已复制"反馈
- **删除**：确认对话框后删除
- **启用/禁用**：开关切换 `is_active` 状态

---

## 五、涉及文件清单

```
backend/
├── app/
│   ├── models/
│   │   └── access_key.py              # 修改：新增 scopes 字段
│   ├── schemas/
│   │   ├── access_key.py              # 修改：CRUD schema 增加 scopes
│   │   └── auth.py                    # 新增：PasswordChange schema
│   ├── core/
│   │   ├── scopes.py                  # 新增：scope 定义 + require_scope 依赖
│   │   └── deps.py                    # 修改：调整 verify_access_key 以携带 AccessKey 信息
│   ├── api/
│   │   ├── admin/
│   │   │   ├── auth.py                # 修改：新增 PUT /password
│   │   │   ├── access_key.py          # 新增：Access Key 独立路由 + GET /scopes
│   │   │   ├── news.py                # 修改：移除 Access Key 相关接口
│   │   │   └── __init__.py            # 修改：注册 access_key 路由
│   │   └── open/
│   │       └── news.py                # 修改：使用 require_scope("news:create")
│   └── services/                      # 无变动
├── scripts/
│   └── init_access_key.py             # 修改：初始 Key 带 scopes

frontend/admin/src/
├── api/
│   ├── news.js                        # 修改：移除 Access Key 相关调用
│   └── access-key.js                  # 新增：Access Key + scopes API 封装
├── views/
│   └── profile/
│       ├── ProfileView.vue            # 新增：个人中心主页面
│       └── AccessKeyManager.vue       # 新增：Access Key 管理组件
├── layouts/AdminLayout.vue            # 修改：头像区域改为可点击导航
└── router/index.js                    # 修改：新增 /profile 路由

docs/
├── api/admin-auth.md                  # 修改：新增修改密码接口文档
├── api/admin-news.md                  # 修改：移除 Access Key 部分
└── database/schema.md                 # 修改：更新 access_keys 表结构
```

---

## 六、执行顺序

1. 后端：access_key 模型增加 scopes 字段 → 重建表 → 更新 schema
2. 后端：新增 `core/scopes.py`（scope 定义 + require_scope 依赖工厂）
3. 后端：新增修改密码接口 + PasswordChange schema
4. 后端：将 Access Key 路由从 news.py 迁移到独立的 access_key.py（含 GET /scopes），更新 __init__.py
5. 后端：改造 open/news.py 使用 require_scope
6. 前端：创建 access-key.js API 封装，更新 news.js
7. 前端：创建 ProfileView.vue + AccessKeyManager.vue
8. 前端：更新路由 + 侧栏头像区域
9. 文档更新
