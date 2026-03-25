# Plan 010 - 管理后台 UI 风格改造（参考 Lovart.ai）

**日期**: 2026-03-24
**状态**: 待确认

---

## 一、设计方向

参考 Lovart.ai 的设计语言，将管理后台从当前的「indigo-violet 柔和风格」改造为「深色优先 + 明亮绿色点缀」的现代扁平风格。

**核心关键词**：深色沉浸、鲜明对比、扁平干净、pill 形按钮、微透明

---

## 二、设计 Token 变更（theme.css）

### 2.1 色彩体系

| 属性 | 当前值 | 新值 | 说明 |
|------|--------|------|------|
| **Accent** | `#4F46E5` (indigo) | `#57C74A` (green) | Lovart 主色 |
| **Accent hover** | `#4338CA` | `#45B438` | |
| **Accent subtle** | `rgba(79,70,229,0.08)` | `rgba(87,199,74,0.10)` | |
| **Accent text** | `#4F46E5` | `#57C74A` | |

**Dark 模式（作为默认）**

| 属性 | 当前值 | 新值 |
|------|--------|------|
| bg | `#08080E` | `#0B0B10` |
| surface | `#101019` | `#131318` |
| surface-raised | `#16162A` | `#1A1A22` |
| surface-hover | `#1A1A2E` | `#1E1E28` |
| surface-sidebar | `#0C0C18` | `#0E0E14` |
| border | `#1E1E38` | `#252530` |
| border-light | `#171728` | `#1C1C28` |
| text | `#EEEDF8` | `#F0F0F5` |
| text-secondary | `#9896B8` | `#9898A8` |
| text-tertiary | `#5C5A78` | `#606070` |
| accent (dark) | `#7C6FEA` | `#65D958` |
| accent-hover (dark) | `#6D5FD8` | `#55C84A` |
| accent-subtle (dark) | `rgba(124,111,234,0.12)` | `rgba(87,199,74,0.12)` |
| accent-text (dark) | `#A59FF4` | `#72E065` |

**Light 模式**

| 属性 | 当前值 | 新值 |
|------|--------|------|
| bg | `#F4F3F0` | `#F5F5F7` |
| surface | `#FFFFFF` | `#FFFFFF` |
| surface-hover | `#F0EFF6` | `#F0F0F4` |
| surface-sidebar | `#FAFAF8` | `#FAFAFC` |
| border | `#E4E3EF` | `#E2E2EA` |
| border-light | `#EEEDF8` | `#ECECF2` |

### 2.2 圆角

| Token | 当前 | 新值 | 说明 |
|-------|------|------|------|
| radius-sm | 6px | 8px | 所有小元素更圆润 |
| radius-md | 10px | 12px | |
| radius-lg | 14px | 16px | |
| radius-xl | 20px | 22px | |
| **新增 radius-pill** | — | 999px | 胶囊按钮专用 |

### 2.3 阴影

保持当前结构但适配新色调：暗色模式阴影更重更深。

---

## 三、组件风格变更

### 3.1 按钮（全局统一）

- **主按钮（btn-primary / btn-create / login-btn）**：`border-radius: var(--radius-pill)`，胶囊形状，更大内边距
- **次按钮（btn-secondary）**：保持边框样式，也改为 pill 形
- **小操作按钮（act-btn）**：圆角加大到 radius-md
- 所有按钮 hover 加入微微 scale(1.02) 或亮度变化

### 3.2 输入框（全局统一）

- `border-radius` 从 `radius-sm` 改为 `radius-md`（12px），更加圆润
- 聚焦时 box-shadow 改为绿色光晕 `0 0 0 3px rgba(87,199,74,0.15)`
- 边框颜色聚焦态改为新 accent

### 3.3 侧边栏（AdminLayout）

- 背景用更深的色值，与主区域形成层次
- 活跃项指示条改为绿色
- Logo-mark 背景渐变更新为绿色系
- 活跃项背景改为 accent-subtle（绿色微透）

### 3.4 模态框（所有 Modal）

- 圆角加大到 `radius-xl`
- overlay 加重模糊 `blur(8px)`
- 模态框边框透明度降低，更融入深色背景
- 头部与内容之间分隔线改为更淡

### 3.5 卡片（Dashboard / 列表项）

- 边框使用更淡的 border-light
- hover 时边框改为 accent 色
- 深色模式下增加微微的 `rgba(255,255,255,0.02)` 背景提升层次感

### 3.6 徽章/标签（Badge / Chip）

- 所有 pill 形 chip 保持 `border-radius: 20px`
- 活跃态使用绿色方案

### 3.7 登录页

- brand-col 背景改为新 accent 绿色
- mesh orb 的渐变色更新（绿、青、蓝替代 indigo、紫、cyan）
- login-btn 改为 pill 形

### 3.8 Favicon / Logo

- 渐变色从 `#4F46E5→#7C3AED` 改为 `#57C74A→#2AAF25`

---

## 四、涉及文件清单

| # | 文件 | 变更类型 |
|---|------|----------|
| 1 | `src/assets/theme.css` | 全量重写 design tokens |
| 2 | `src/layouts/AdminLayout.vue` | 更新 sidebar 样式 + logo 渐变 |
| 3 | `src/views/LoginView.vue` | 更新 brand-col 色彩 + 按钮 pill 化 |
| 4 | `src/views/DashboardView.vue` | 更新卡片和按钮样式 |
| 5 | `src/views/todo/TodoList.vue` | 更新按钮样式 |
| 6 | `src/views/todo/TodoSidebar.vue` | 更新 chip / tree-item 样式 |
| 7 | `src/views/todo/TodoDetail.vue` | 更新按钮和 dot 颜色 |
| 8 | `src/views/todo/TodoFormModal.vue` | 更新 modal、input、button 样式 |
| 9 | `src/views/todo/CategoryManager.vue` | 更新 modal、button 样式 |
| 10 | `src/views/todo/TagManager.vue` | 同上 |
| 11 | `src/views/news/NewsList.vue` | 更新按钮样式 |
| 12 | `src/views/news/NewsFormModal.vue` | 更新 modal 样式 |
| 13 | `src/views/news/NewsCategoryManager.vue` | 更新 modal 样式 |
| 14 | `src/views/news/NewsSourceManager.vue` | 同上 |
| 15 | `src/views/news/NewsDetail.vue` | 更新按钮样式 |
| 16 | `src/views/profile/ProfileView.vue` | 更新按钮和输入框样式 |
| 17 | `src/views/profile/AccessKeyManager.vue` | 更新 modal、toggle、按钮样式 |
| 18 | `public/favicon.svg` (admin + mobile) | 更新渐变色 |

---

## 五、执行策略

1. **先改 theme.css** — 70% 的视觉效果由 design token 驱动，一改全变
2. **再改 favicon/logo** — 品牌色同步
3. **逐个组件微调** — 只改 border-radius、按钮形状等 token 无法覆盖的样式
4. **不改任何业务逻辑和 HTML 结构** — 纯 CSS 层面改动

---

## 六、确认后执行
