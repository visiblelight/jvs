# Plan 020: 事项评论功能

## 背景

事项目前只有描述字段，无法记录过程进展。评论功能让用户对事项追加时序性记录，
形成轻量"动态流"。支持 Markdown + 粘贴图片，评论数在列表中显示。

## 已确认

- ✅ 评论支持 Markdown 渲染（DOMPurify 防 XSS）
- ✅ 支持粘贴图片（复用现有 `/api/admin/uploads/images?module=todo` 接口）
- ✅ 事项列表显示评论数
- ✅ 移动端 Phase 2，本次只做管理后台

---

## 数据模型

### 新表：todo_comments

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| todo_item_id | Integer FK → todo_items.id CASCADE | 所属事项 |
| user_id | Integer FK → users.id | 所属用户 |
| content | Text Not Null | 评论内容，Markdown 格式 |
| created_at | DateTime | 创建时间（UTC） |
| updated_at | DateTime | 更新时间（UTC），自动更新 |
| deleted_at | DateTime nullable | 软删除，不物理删除 |

### TodoItemOut 新增 comment_count 字段

在后端返回事项列表时附带评论数（通过 SQLAlchemy `column_property` 或子查询），
无需前端额外请求。

---

## API 设计

Base Path: `/api/admin/todo/items/{item_id}/comments`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /items/{id}/comments | 获取评论列表，按 created_at ASC，过滤 deleted_at |
| POST | /items/{id}/comments | 新建评论 |
| PUT | /items/{id}/comments/{cid} | 编辑评论内容（仅限本人） |
| DELETE | /items/{id}/comments/{cid} | 软删除（仅限本人） |

**GET 响应**：
```json
[
  {
    "id": 1,
    "content": "已与客户确认需求",
    "created_at": "2026-04-03T10:00:00Z",
    "updated_at": "2026-04-03T10:00:00Z"
  }
]
```

图片上传复用现有接口：`POST /api/admin/uploads/images?module=todo`，返回 `{"url": "..."}`

---

## 前端设计（管理后台）

### 1. TodoList.vue — 评论数气泡

每个事项 meta 行末尾，若 `comment_count > 0` 显示：
```
💬 3
```
灰色小字，不喧宾夺主。

### 2. TodoDetail.vue — 评论区

布局（紧接现有属性信息之后）：

```
─── 评论  3 ───────────────────────────
  [头像] 2小时前
         已与客户确认需求，计划下周跟进。
                              ✎ 编辑  × 删除

  [头像] 刚刚
         ![screenshot](...)
                              ✎ 编辑  × 删除

────────────────────────────────────────
  [ 添加评论…支持 Markdown，可粘贴图片  ]
                                  [发送]
```

**评论列表细节**：
- 相对时间（"2 小时前"），hover 显示完整时间
- 内容 Markdown 渲染（DOMPurify）
- hover 行显示编辑 / 删除按钮（本人才显示）
- 编辑：原地 inline 切换为 textarea，Esc 取消，Enter 或按钮保存
- 删除：弹窗二次确认后软删

**输入框细节**：
- `<textarea>` 自动增高（autosize）
- 监听 `paste` 事件：检测到图片文件 → 上传 → 插入 `![](url)` 到光标位置
- 上传中显示 loading 占位文字 `![上传中…]()`
- `Cmd/Ctrl + Enter` 提交，或点击发送按钮
- 提交后清空输入框，列表滚动到底部

---

## 实施步骤

- [x] Step 1：后端 — TodoComment 模型 + schema + service + router + migration
- [x] Step 2：后端 — TodoItemOut 增加 comment_count 字段
- [x] Step 3：前端 — api/todo.js 增加评论相关接口（图片上传复用 uploads.js）
- [x] Step 4：前端 — TodoDetail.vue 评论区（列表 + inline edit + 输入框 + 粘贴图片）
- [x] Step 5：前端 — TodoList.vue 评论数气泡
- [ ] Step 6：文档更新（API + schema）
