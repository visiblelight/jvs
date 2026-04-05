# Plan 021：后台用户管理 + 板块权限控制

## 背景

目前系统是多用户 SaaS 平台，但缺少：
1. 超级管理员对普通后台用户的 CRUD 管理
2. 细粒度的板块（Module）权限分配

需求要点：
- 只有**超级管理员**（`is_superuser=True`）能进入用户管理
- 超管能创建 / 编辑 / 删除用户，并为每个用户配置可见的板块
- 板块权限不仅要在 UI 上隐藏菜单，更要在 **API 层拦截**，防止绕过
- 权限对 **管理后台 + 移动工作台** 同时生效
- 新增**完整的测试**覆盖

## 现状调研

- `User` 模型已有 `is_superuser` 布尔字段；`admin` 账号已是超管
- 后台和移动端都调用 `/api/admin/*` 接口
- 目前已有的板块：`todo`、`news`、`access_key`（开放接口管理）
- 无板块权限控制，任何登录用户都能访问所有接口
- `tests/conftest.py` 已有测试基础设施（in-memory SQLite + fixtures）

---

## 设计

### 1. 板块注册表（后端单一事实源）

新建 `app/core/modules.py`：
```python
MODULES = [
    {"key": "todo",       "label": "事项管理",   "sort_order": 10},
    {"key": "news",       "label": "新闻资讯",   "sort_order": 20},
    {"key": "access_key", "label": "开放接口",   "sort_order": 30},
    # 后续板块按 sort_order 排列
]
```
（用列表保持顺序，也便于按 sort_order 扩展）

用户管理本身不是"业务板块"，只对超管开放，不占用 MODULES 槽位。

### 2. 数据模型

**新表 `user_modules`**（多对多关联，简单明了）：

| 字段 | 类型 | 说明 |
|---|---|---|
| user_id | Integer FK → users.id CASCADE | 用户 |
| module_key | String(32) | 板块 key（如 "todo"）|
| granted_at | DateTime | 授予时间 |

主键：`(user_id, module_key)` 复合主键。

**不在 User 模型上加 modules 字段**，通过 relationship 访问。

### 3. 后端依赖注入

**`app/core/deps.py` 新增：**

```python
def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(403, detail="仅超级管理员可访问")
    return current_user

def require_module(module_key: str):
    def _dep(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if current_user.is_superuser:
            return current_user  # 超管直通
        has = db.query(UserModule).filter(
            UserModule.user_id == current_user.id,
            UserModule.module_key == module_key,
        ).first()
        if not has:
            raise HTTPException(403, detail=f"没有 '{module_key}' 板块权限")
        return current_user
    return _dep
```

**应用方式**：在各板块 router 上挂路由级依赖（FastAPI 会缓存，不影响现有 `get_current_user` 注入）：

```python
# app/api/admin/todo.py
router = APIRouter(
    prefix="/todo",
    tags=["admin-todo"],
    dependencies=[Depends(require_module("todo"))],
)
```

对 `news.py`、`access_key.py` 同样处理。`auth.py`、`uploads.py` 不加（所有登录用户都能访问个人资料和上传）。

### 4. API 设计

**`/api/admin/users`**（超管专属）：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /users | 列出所有用户（含禁用） |
| POST | /users | 创建用户 |
| GET | /users/{id} | 用户详情（含模块） |
| PUT | /users/{id} | 更新（username / is_active / password 可选） |
| PUT | /users/{id}/modules | 设置用户的板块权限（覆盖式） |

（**不提供 DELETE**：UI 上"禁用"即 `is_active=False`，不硬删。）

**`/api/admin/modules`**（登录即可）：
- GET：返回全部 MODULES（用于构建权限选择 UI）

**`/api/admin/auth/me`**（扩展现有接口）：
- 响应中追加 `is_superuser: bool`、`modules: list[str]`

### 5. 业务规则 / 保护措施

- **禁止自我禁用**：超管不能把自己 `is_active` 改为 False
- **禁止禁用最后一个活跃超管**：确保系统至少有一个可用超管
- **禁止修改自己的 is_superuser**：避免自废超管权
- **禁止对其他超管调整 modules**：超管本就全权限（接口返回 400，前端隐藏模块选择区）
- **username 唯一**：创建/更新时校验

### 6. 数据迁移（Alembic）

1. 新建 `user_modules` 表
2. 数据迁移：为**现有所有非超管用户**授予全部当前存在的模块（向后兼容，避免升级后失去访问权限）

---

## 前端设计（管理后台）

### 1. auth store 扩展

`fetchUser()` 拿到 `is_superuser` 和 `modules` 后存入 store。

新增 getters：
```js
const canAccess = (moduleKey) => user.value?.is_superuser || user.value?.modules?.includes(moduleKey)
const isSuperuser = computed(() => !!user.value?.is_superuser)
```

### 2. AdminLayout 菜单过滤

菜单项增加 `module` 字段：
```js
{ path: '/todo', label: 'ToDo', module: 'todo', svg: '...' }
{ path: '/news', label: '新闻', module: 'news', svg: '...' }
```

使用 computed 过滤：
```js
const visibleMenuItems = computed(() => menuItems.filter(item =>
  !item.module || authStore.canAccess(item.module)
))
```

超管额外显示"用户管理"入口（带 superuser 标记）。

### 3. 路由守卫

在 `router.beforeEach` 中校验目标路由对应的 module：
```js
{
  path: 'todo',
  meta: { module: 'todo' },
  ...
}
```

如果 `to.meta.module` 存在且 `authStore.canAccess(to.meta.module)` 为 false，重定向到 `/dashboard`（并弹提示）。

`/users` 路由加 `meta: { superuser: true }`，非超管访问直接重定向。

### 4. 用户管理页面 `/users`

- 用户列表（表格：用户名、状态、超管标记、模块数、创建时间、操作）
- 新建 / 编辑用户弹窗（用户名、密码、is_active、modules 多选复选）
- 删除用户二次确认
- 使用已有的 confirm modal 风格

---

## 前端设计（移动工作台）

同样的思路：
- auth store 扩展 `canAccess`
- `HomeView.vue` 中的 feature tile 过滤
- 路由守卫按 module 拦截

移动端**无用户管理**页面（保持精简，用户管理只在后台）。

---

## 测试设计（tests/）

### test_users.py（新增）

**超管权限测试：**
- `test_list_users_as_superuser` — 超管可以 GET /users
- `test_list_users_as_normal_user_forbidden` — 普通用户 403
- `test_create_user_as_superuser` — 超管创建用户成功
- `test_create_user_duplicate_username` — 用户名重复 400
- `test_update_user` — 更新 username / is_active / password
- `test_disable_self_forbidden` — 超管不能把自己 is_active 改为 False
- `test_disable_last_superuser_forbidden` — 不能禁用最后一个活跃超管
- `test_cannot_modify_own_superuser_flag` — 不能改自己的 is_superuser
- `test_set_user_modules` — 设置用户模块权限
- `test_set_modules_on_superuser_forbidden` — 不能对其他超管配置 modules

### test_module_permissions.py（新增）

**板块权限拦截测试：**
- `test_user_without_todo_module_cannot_access_todo` — 无 todo 权限访问 `/admin/todo/items` 返回 403
- `test_user_with_todo_module_can_access_todo` — 有 todo 权限访问成功
- `test_superuser_bypasses_module_check` — 超管无需 modules 配置即可访问所有
- `test_module_permission_applies_to_all_todo_endpoints` — 抽样验证 POST/PUT/DELETE 均被拦截
- `test_news_and_todo_permissions_are_independent` — 有 todo 无 news 时 news 接口被拦截

### test_auth.py（扩展）

- `test_me_returns_modules_and_superuser_flag` — /auth/me 包含新字段

### conftest.py 新增 fixtures

- `superuser` / `superuser_auth_headers`
- `user_with_todo_module` / 相应 headers

---

## 实施步骤

- [ ] Step 1：后端 — 新建 `MODULES` 注册表
- [ ] Step 2：后端 — `UserModule` 模型 + Alembic 迁移（含数据迁移：为现有用户授予全模块）
- [ ] Step 3：后端 — `require_superuser` + `require_module` 依赖
- [ ] Step 4：后端 — 在 todo/news/access_key router 上挂 module 依赖
- [ ] Step 5：后端 — `/api/admin/users/*` 接口（CRUD + modules 配置）
- [ ] Step 6：后端 — `/api/admin/modules` 接口
- [ ] Step 7：后端 — 扩展 `/auth/me` 返回 is_superuser / modules
- [ ] Step 8：后端 — 新增测试（test_users.py, test_module_permissions.py），扩展 test_auth.py
- [ ] Step 9：前端后台 — auth store 扩展 canAccess / isSuperuser
- [ ] Step 10：前端后台 — AdminLayout 菜单过滤 + 用户管理入口
- [ ] Step 11：前端后台 — 路由守卫按 module / superuser 拦截
- [ ] Step 12：前端后台 — `/users` 用户管理页面（列表 + 弹窗 + 模块配置）
- [ ] Step 13：前端移动端 — auth store + HomeView 过滤 + 路由守卫
- [ ] Step 14：脚本 — 更新 init_admin 说明（不变），确认 init_demo 适配新权限模型
- [ ] Step 15：文档 — 更新 API 文档 + 数据结构文档

---

## 风险与兼容性

- **现有用户不会被锁出**：数据迁移时为所有非超管用户授予全部现有模块
- **新增模块时**：需要手动给需要的用户授权（符合最小权限原则）
- **接口缓存**：FastAPI 的依赖缓存确保 `require_module` 和 `get_current_user` 不会重复查询

## 已确认

1. ✅ **用户删除 = 软禁用**（方案 C）：UI 上"删除"实际只是切 `is_active=False`，保留所有数据；对应地，用户列表默认展示全部（含禁用），操作中增加"禁用/启用"按钮，无硬删除入口
2. ✅ **移动端无板块权限 = 不显示首页入口图标**（不渲染，不做空状态提示）
3. ✅ **MODULES 增加 `sort_order` 字段**，后端/前端按此排序展示
