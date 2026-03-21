# Plan 006 - 用户头像

**日期**: 2026-03-20
**状态**: 待确认

---

## 一、功能概述

用户可以在个人中心上传图片作为头像。未上传时，系统显示一个统一风格的默认矢量头像（SVG）。头像在以下位置展示：

- 侧栏底部的用户区域（目前是字母 Avatar）
- 个人中心页面的资料卡片顶部

---

## 二、技术方案

### 2.1 存储方式

上传的头像文件保存在服务端本地目录 `backend/uploads/avatars/`。

文件命名规则：`{user_id}.{ext}`（如 `1.jpg`），直接用 user_id 命名，同一用户上传新头像自动覆盖旧文件，无需额外清理逻辑。

支持格式：`jpg / jpeg / png / webp / gif`，大小限制 **2MB**。

后端通过 FastAPI 的 `StaticFiles` 挂载目录，提供静态文件访问：
```
GET /uploads/avatars/{filename}
```

前端取头像 URL 为 `/uploads/avatars/{user_id}.{ext}`，存在 `avatar` 字段（相对路径或文件名）记录在数据库中。

> **未来迁移 PostgreSQL + 对象存储时**：仅需修改 auth.py 的上传逻辑，将本地写文件改为上传至 S3/OSS，把返回的 URL 存入 `avatar` 字段，其他逻辑不变。

### 2.2 数据库改动

`users` 表新增 `avatar` 字段：

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| avatar | String(200) | Nullable | null | 头像文件名（如 `1.jpg`），null 表示使用默认头像 |

### 2.3 默认头像

无头像时，前端渲染一个内联 SVG —— 采用线条风格的通用人物轮廓，使用 `var(--color-accent)` 着色，与当前主题保持一致，不依赖任何外部图片资源。

---

## 三、后端改动

### 3.1 User 模型

新增 `avatar: Mapped[str | None]` 字段。

### 3.2 UserInfo Schema

新增 `avatar: str | None` 字段，前端通过 `GET /api/admin/auth/me` 获取头像信息。

### 3.3 上传接口

`POST /api/admin/auth/avatar`

- 接收 `multipart/form-data`，字段名 `file`
- 校验 MIME 类型（`image/jpeg / image/png / image/webp / image/gif`）
- 校验文件大小（≤ 2MB）
- 保存为 `uploads/avatars/{user_id}.{ext}`（覆盖旧文件）
- 更新 `user.avatar` 字段
- 返回 `{ "avatar": "1.jpg" }`（文件名）

### 3.4 删除头像接口

`DELETE /api/admin/auth/avatar`

- 删除磁盘上的文件（如果存在）
- 将 `user.avatar` 置为 null
- 返回 `204`

### 3.5 静态文件挂载

在 `main.py` 挂载 `StaticFiles`：

```python
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

启动前确保 `uploads/avatars/` 目录存在。

---

## 四、前端改动

### 4.1 Avatar 组件 — `UserAvatar.vue`

封装一个可复用的 `UserAvatar` 组件，接收 props：

| Prop | 类型 | 说明 |
|------|------|------|
| avatar | String \| null | 头像文件名，null 则显示默认 SVG |
| size | Number | 尺寸（px），默认 32 |

内部逻辑：
- 有 avatar → 显示 `<img src="/uploads/avatars/{avatar}">`，加载失败时 fallback 到默认 SVG
- 无 avatar → 显示默认矢量 SVG 头像

### 4.2 侧栏更新

`AdminLayout.vue` 中的 `nav-avatar` 区域，用 `<UserAvatar>` 替换现有的字母 Avatar，尺寸 32px。

### 4.3 个人中心页面更新

`ProfileView.vue` 中的基本信息卡片顶部新增头像展示区：

```
┌──────────────────────────────┐
│  [头像 64px]  用户名           │
│               创建时间         │
│  [上传新头像] [移除头像]        │
└──────────────────────────────┘
```

交互：
- 点击"上传新头像" → 触发 `<input type="file">` → 选择后立即调用上传接口 → 更新 store 中的 user 信息 → 头像实时刷新
- 有头像时才显示"移除头像"按钮，点击后调用删除接口

### 4.4 Auth Store 更新

上传/删除头像成功后，调用 `store.fetchUser()` 刷新用户信息，使侧栏头像实时更新。

---

## 五、涉及文件清单

```
backend/
├── app/
│   ├── models/user.py                 # 修改：新增 avatar 字段
│   ├── schemas/auth.py                # 修改：UserInfo 新增 avatar 字段
│   └── api/admin/auth.py              # 修改：新增上传/删除头像接口
├── main.py                            # 修改：挂载 StaticFiles
└── uploads/avatars/                   # 新增：头像存储目录（需创建）

frontend/admin/src/
├── components/
│   └── UserAvatar.vue                 # 新增：通用头像组件（含默认 SVG）
├── views/profile/ProfileView.vue      # 修改：基本信息卡片加入头像上传 UI
├── layouts/AdminLayout.vue            # 修改：侧栏用 UserAvatar 替换字母头像
└── api/auth.js                        # 修改：新增 uploadAvatar / deleteAvatar

docs/
├── api/admin-auth.md                  # 修改：新增头像上传/删除接口文档
└── database/schema.md                 # 修改：users 表新增 avatar 字段
```

---

## 六、执行顺序

1. 后端：User 模型 + UserInfo Schema 增加 avatar 字段 → 数据库迁移
2. 后端：创建 `uploads/avatars/` 目录 → main.py 挂载静态文件
3. 后端：auth.py 增加上传/删除头像接口
4. 前端：api/auth.js 增加 uploadAvatar / deleteAvatar
5. 前端：创建 `UserAvatar.vue` 通用组件
6. 前端：更新 AdminLayout 侧栏头像
7. 前端：更新 ProfileView 头像上传 UI
8. 文档更新
