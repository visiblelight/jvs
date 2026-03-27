# 015 - 通用图片上传服务 (Universal Image Upload)

## 背景 (Context)

系统多个功能板块都需要支持图片内嵌：

- **ToDo 描述**：Ctrl+V 粘贴剪贴板图片，嵌入到 Markdown 描述中
- **News 正文**：撰写新闻时直接粘贴或插入图片
- **未来板块**：任何需要富文本/Markdown 描述的地方

若每个板块各自实现上传逻辑，会导致代码重复、存储分散、难以统一维护。因此将图片上传抽象为一个**通用服务**，所有板块共享同一套上传接口和前端 composable。

---

## 一、后端实现

### 1.1 静态文件服务 — `main.py`

挂载 `/uploads` 路由，让 FastAPI 直接提供上传文件的 HTTP 访问：

```python
from fastapi.staticfiles import StaticFiles

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

上传根目录：`backend/uploads/`（已加入 `.gitignore`）

### 1.2 新建路由文件 — `backend/app/api/admin/uploads.py`

```
POST /admin/uploads/images?module=todo
POST /admin/uploads/images?module=news
POST /admin/uploads/images?module=general   ← 默认值
```

**请求：** `multipart/form-data`，字段名 `file`

**校验规则：**
| 规则 | 限制 |
|------|------|
| 文件类型 | 仅允许 `image/jpeg`、`image/png`、`image/gif`、`image/webp` |
| 文件大小 | ≤ 5 MB |

**存储路径：** `backend/uploads/{module}/{uuid4}{ext}`

**成功响应：**
```json
{ "url": "/uploads/todo/3f2a1b4c-....png" }
```

**失败响应：**
- `400` — 文件类型不合法
- `400` — 文件超过大小限制
- `401` — 未登录

**鉴权：** 复用现有 `get_current_user` 依赖，需要有效 JWT。

### 1.3 注册路由 — `backend/app/api/admin/__init__.py` 或主路由文件

```python
from .uploads import router as uploads_router
router.include_router(uploads_router, prefix="/uploads", tags=["uploads"])
```

---

## 二、前端实现

### 2.1 API 层 — `frontend/admin/src/api/uploads.js`（新建）

```js
export const uploadImage = (file, module = 'general') => {
  const form = new FormData()
  form.append('file', file)
  return request.post(`/admin/uploads/images?module=${module}`, form)
}
```

### 2.2 Composable — `frontend/admin/src/composables/useImagePaste.js`（新建）

封装剪贴板图片检测、上传、占位符替换的完整流程：

```js
// 用法示例（在任意表单组件中）
const { handlePaste } = useImagePaste({
  module: 'todo',
  getValue: () => form.description,
  setValue: (val) => form.description = val,
  getEl: () => textareaRef.value,
})
```

**内部流程：**

1. 监听 `paste` 事件，遍历 `clipboardData.items`
2. 发现 `image/*` 类型时，阻止默认行为
3. 在当前光标位置插入占位文本：`![上传中...]()`
4. 将图片 Blob POST 到 `/admin/uploads/images?module={module}`
5. 上传成功：将占位文本替换为 `![图片](url)`
6. 上传失败：移除占位文本，通过 `console.error` 或 toast 提示用户

### 2.3 接入 ToDo — `TodoFormDrawer.vue`

- 在描述 `<textarea>` 绑定 `@paste="handlePaste"`
- 调用 `useImagePaste({ module: 'todo', ... })`
- 添加粘贴提示文案（placeholder 末尾加 "，支持 Ctrl+V 粘贴图片"）

### 2.4 接入 News — `NewsFormDrawer.vue`

- 同上，`module: 'news'`

### 2.5 详情面板图片样式 — `TodoDetail.vue` / `NewsDetail.vue`

补充 markdown 渲染区域的图片样式：

```css
.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 8px 0;
  display: block;
}
```

---

## 三、影响评估

### 后端变更文件
| 文件 | 变更类型 |
|------|---------|
| `backend/main.py` | 修改 — 挂载 `/uploads` 静态目录 |
| `backend/app/api/admin/uploads.py` | **新增** — 上传路由 |
| `backend/app/api/admin/router.py`（或同等文件） | 修改 — 注册 uploads 路由 |
| `backend/.gitignore` | 修改 — 忽略 `uploads/` 目录内容 |

### 前端变更文件
| 文件 | 变更类型 |
|------|---------|
| `frontend/admin/src/api/uploads.js` | **新增** — uploadImage 函数 |
| `frontend/admin/src/composables/useImagePaste.js` | **新增** — 粘贴上传 composable |
| `frontend/admin/src/views/todo/TodoFormDrawer.vue` | 修改 — 接入 useImagePaste |
| `frontend/admin/src/views/news/NewsFormDrawer.vue` | 修改 — 接入 useImagePaste |
| `frontend/admin/src/views/todo/TodoDetail.vue` | 修改 — 图片 CSS |

### 不涉及的变更
- 数据库：描述字段已是 `Text`，无需迁移
- Schema / Service：不变
- 移动端：本次不涉及

---

## 四、实施顺序

1. **Phase 1 — 后端**：静态挂载 → 上传路由 → 注册路由
2. **Phase 2 — 前端基础**：`api/uploads.js` → `composables/useImagePaste.js`
3. **Phase 3 — 接入板块**：TodoFormDrawer → NewsFormDrawer → 详情面板图片样式
