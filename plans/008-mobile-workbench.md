# Plan 008 - 移动工作台

**日期**: 2026-03-22
**状态**: 已完成

---

## 一、功能概述

基于现有 `frontend/mobile` 脚手架，从零开发移动工作台前端。采用"桌面化"导航结构：底部 Tab Bar 仅保留**首页**和**我的**两个固定入口，首页作为可扩展的模块桌面，用户点击模块图标进入对应板块。后续新增板块只需在桌面配置列表追加一条记录，Tab Bar 无需改动。

---

## 二、导航结构

```
Tab Bar：首页 | 我的
           │
           ▼
      HomeView（桌面）
      ┌─────┬─────┬─────┬─────┐
      │ 待办 │ 新闻 │  …  │  …  │   ← 图标卡片，后续持续扩展
      └─────┴─────┴─────┴─────┘
           │
     点击进入模块（全屏，顶部 PageHeader + 返回键）
           │
      ┌────┴────┐
   TodoView  NewsView  …
```

**Tab Bar 显示规则**：路由 `meta: { tabBar: true }` 的页面（`/home`、`/profile`）显示底部导航；进入任意模块页面后自动隐藏，由 `PageHeader` 提供返回入口。

---

## 三、路由设计

| 路径 | 组件 | Tab Bar |
|------|------|---------|
| `/login` | LoginView | 无 |
| `/home` | HomeView | ✅ |
| `/profile` | ProfileView | ✅ |
| `/todo` | TodoView | ❌（顶部返回桌面） |
| `/news` | NewsView | ❌ |
| `/news/:id` | NewsDetailView | ❌ |

---

## 四、技术方案

### 4.1 技术栈

- Vue 3 + Vite + Pinia + Vue Router（与 admin 一致）
- 字体：系统字体栈（`-apple-system, BlinkMacSystemFont, PingFang SC`）—— 移动端渲染更佳，无需加载 Web 字体
- 标题用 Syne（仅少量场景）
- 主题变量与 admin 共用同色系（`#4F46E5` / `#7C6FEA`），针对移动端调整圆角（16px 卡片、24px Sheet）和阴影风格

### 4.2 移动端专项设计

| 特性 | 实现方式 |
|------|---------|
| 安全区适配 | `env(safe-area-inset-top/bottom)` CSS 变量，适配刘海屏/底部横条 |
| 滚动条隐藏 | 全局 `::-webkit-scrollbar { display: none }` |
| 点击高亮消除 | `-webkit-tap-highlight-color: transparent` |
| 触摸目标 | 最小 44px 可点击区域 |
| 页面过渡 | Tab 间用 `fade`，进入模块用 `slide-left`，返回用 `slide-right` |
| 上拉加载更多 | 新闻列表监听 `scroll` 事件，距底部 100px 自动加载下一页 |

### 4.3 底部 Sheet

封装通用 `BottomSheet.vue` 组件（`Teleport` 到 body），所有表单、筛选面板均通过 Sheet 弹出，符合移动端操作习惯：

- 顶部有拖拽指示条
- 点击遮罩关闭
- 进出动画：从底部 translateY(100%) 滑入

### 4.4 API 复用

完全复用后端同一套 API（`/api/admin/*`），与管理后台共享数据，无需新增后端接口。

---

## 五、各模块功能说明

### 5.1 HomeView（桌面）

- 顶部问候语（按时间段：早上好 / 下午好 / 晚上好）+ 用户头像（点击进入个人中心）
- 数据摘要条：待办总数 / 新闻总数
- 2 列模块图标网格，每个卡片包含渐变色图标、模块名、描述
- 新增模块只需在 `modules` 数组追加配置项

### 5.2 TodoView（待办）

- 顶部状态 Tab：全部 / 进行中 / 已完成
- 右上角筛选按钮（有筛选条件时显示红点），点击弹出筛选 Sheet（优先级 + 分类）
- 列表每项：圆圈完成按钮、标题、分类标签、优先级色标、截止日期（含逾期提示）、删除按钮
- 右下角 FAB 新建待办，点击弹出 `TodoFormSheet`
- `TodoFormSheet`：标题、备注、优先级、分类、截止日期，支持新建和编辑

### 5.3 NewsView（新闻）

- 右上角搜索按钮，点击展开搜索框（防抖 400ms）
- 横向滚动分类筛选条
- 卡片列表：分类徽章、日期、标题（最多 2 行）、摘要（最多 2 行）、来源
- 上拉到底自动加载下一页（无限滚动）

### 5.4 NewsDetailView（文章阅读）

- 全屏阅读器，顶部返回键
- Markdown 渲染（`marked`，`breaks: true`）
- 摘要用 `pre-wrap` 保留换行

### 5.5 ProfileView（个人中心）

- 顶部头像（只读展示，不支持移动端上传）+ 用户名 + 注册时间
- 设置列表卡片：修改密码（弹出 Sheet）、明暗主题切换、退出登录

---

## 六、涉及文件清单

### 新建
```
frontend/mobile/src/
├── assets/theme.css
├── api/
│   ├── request.js
│   ├── auth.js
│   ├── todo.js
│   └── news.js
├── stores/
│   ├── auth.js
│   ├── todo.js
│   ├── news.js
│   └── theme.js
├── components/
│   ├── UserAvatar.vue
│   ├── BottomNav.vue
│   ├── PageHeader.vue
│   └── BottomSheet.vue
├── layouts/
│   └── MobileLayout.vue
└── views/
    ├── LoginView.vue
    ├── HomeView.vue
    ├── todo/
    │   ├── TodoView.vue
    │   └── TodoFormSheet.vue
    ├── news/
    │   ├── NewsView.vue
    │   └── NewsDetailView.vue
    └── profile/
        └── ProfileView.vue
```

### 修改
```
frontend/mobile/src/main.js          引入 theme.css，初始化 Pinia/Router
frontend/mobile/src/App.vue          初始化 ThemeStore
frontend/mobile/src/router/index.js  完整路由配置 + 登录守卫（同 admin 逻辑）
frontend/mobile/vite.config.js       新增 /uploads 代理（头像图片访问）
frontend/mobile/package.json         新增 marked 依赖
```

---

## 七、功能范围边界

| 功能 | 移动工作台 | 说明 |
|------|-----------|------|
| 登录 / 退出 | ✅ | |
| 头像展示 | ✅ | 只读，上传功能保留在 PC 后台 |
| 修改密码 | ✅ | |
| 主题切换 | ✅ | |
| Todo 查看 / 新建 / 编辑 / 完成 / 删除 | ✅ | |
| Todo 分类 / 标签管理 | ❌ | 保留 PC 后台 |
| 新闻查看 / 搜索 / 阅读 | ✅ | |
| 新闻新建 / 编辑 | ❌ | 保留 PC 后台 |
| 分类 / 来源管理 | ❌ | 保留 PC 后台 |
| Access Key 管理 | ❌ | 保留 PC 后台 |
