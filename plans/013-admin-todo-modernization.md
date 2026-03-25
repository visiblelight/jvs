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
