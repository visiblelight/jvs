# 013 - Admin ToDo Module & Global UI Modernization Plan

## 目标 (Objective)
全面重构管理后台的 ToDo 模块交互方式，彻底抛弃传统的“全屏居中弹窗”和“层叠下拉菜单”等老旧体验，引入与顶级效率工具（如 Linear、Notion、Things 3）平齐的内阴面滑动面板（Drawers）、段落化控制（Segmented Controls）和侧边拖拽/原地内联编辑设计。
同时，全局优化老破灰色的遮罩层或下垫色，注入更加通透的亚克力光影层。

## 重构细节 (Implementation Details)

### 1. 摒弃居中弹窗，引入侧滑抽屉 (Slide-over Drawer)
*   废弃全屏遮挡或居中的 `TodoFormModal.vue`。
*   **新建交互方式**：创建 `TodoFormDrawer.vue` 或者在核心视图内复用抽屉概念。当点击“新建/编辑任务”时，从界面右侧平滑伸出一个大抽屉版面 (Drawer panel)。左侧保持原内容半可见，利用高斯模糊。抽屉具备无拘束布局和超大留白。

### 2. 状态/优先级选项扁平化 (Segmented Controls & Pills)
*   由于之前使用 `<select>` 或类似组件会导致多点击 2 次的糟糕交互。这里会将其直接打平在版面上。
*   对于“重要度 (Importance)” 和 “优先级 (Priority)”，改为 **分段控制器 (Segmented Control)** 或 **全展开带图标的胶囊按钮群 (Radio Pill Buttons)**。用户可一眼看全四个级别并能够单次一键切换。
*   这种组件级的样式变更如果涉及到基础 CSS 库或 `theme.css` 的新增逻辑，将确保作为全局 `.segmented-wrapper` 提供，保证其他业务板块随时均可用。

### 3. 侧边栏内联管理 (Inline Sidebar Management)
*   **弃用旧管理 Modal**：将 `CategoryManager.vue` 和 `TagManager.vue` 弹窗界面逻辑废弃。
*   **侧边注入内联新建与编辑**：在现有的 `TodoSidebar.vue` (项目侧栏) 中，为分类(Categories) 和 标签(Tags) 版块加入 `[+ 添加]` Inline Input。用户回车即可原地创建，光标悬停则出现快速编辑和删除 icon。

### 4. 全局弹窗/遮罩层色彩优化 (Global Overlay Enhancement)
*   你觉得原来的底色“太灰了”，那是因为直接使用了不透光的 `alpha(0.5) + #333` 类做法。
*   通过重写 `theme.css` 里的遮罩层逻辑，例如新增/修改 `.modal-overlay` 或者 `.drawer-backdrop`。
*   在明亮模式 (Light Theme) 下，将其改为 `rgba(255, 255, 255, 0.4)` 并附加上极强的 `backdrop-filter: blur(12px)`；在暗黑模式下变更为透明黑加上玻璃模糊度。这将带给全局（未来所有别的弹窗也是如此）质的飞跃。

## 影响评估
*   **视图层**：将重点改造和删减 `frontend/admin/src/views/todo` 内的相关 vue 文件逻辑，将其与 Vue Router 或父组件进行逻辑切割整合。
*   **样式层**：`theme.css` 将被更新，主要涉及 `.modal` 面板底层架构的亚克力重写和 `pill-buttons` 全局化。
*   无需更改 Python 后台 API（API 参数保持原有结构，仅改变交互提交方式）。

### 5. 引入软删除与垃圾箱机制 (Soft Delete & Trash Bin)
*   **后端修改**：在 `TodoItem` 模型设计中引入 `is_deleted` (Boolean) 和 `deleted_at` 字段，确保数据安全性。
*   **接口下沉**：原有的硬删除接口变更为向垃圾桶移动的接口；另新增专门的 `/restore`（恢复） 和 `/hard`（彻底销毁）管理接口。
*   **交互适配**：在 TodoSidebar 中新增“垃圾桶”系统入口，点击垃圾桶图标不再作为列表过滤条件，而是弹出专属的“垃圾箱管理窗口 (Trash Modal)”以进入独立空间；在新窗口中集中展示已删除的列表，并提供恢复 (Restore) 与彻底删除 (Hard Delete) 操作。这避免了因列表过滤导致的来回切换等反直觉体验。

### 6. 全局命令式搜索 (Command-Palette Global Search)
*   **快捷呼出**：抛弃繁琐的查找流程，全局支持监听 `Cmd+K` / `Ctrl+K` 热键，一键在屏幕中央召唤带有极致模糊层视觉效果的命令式搜索模块。
*   **防抖与高亮**：加入输入防抖 (`debounce`)，并将实时查询匹配结果的标题与详情匹配值作高亮切片处理 (`<mark>`)。
*   **键盘驱动导航**：支持 `↑ / ↓` 纯键盘快速浏览、高亮预览目标结果，搭配回车键 (`Enter`) 确认直达单条详情视图。
*   **后端支撑**：原获取列表的接口打通支持 `search` (或 `q`) 查询参数，利用 SQLAlchemy 后端 `ilike` 实现多字段无缝融合匹配。
