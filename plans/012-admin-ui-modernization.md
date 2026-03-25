# 012 - Admin UI Modernization Plan

## 目标 (Objective)
通过移除传统的线框结构，并引入悬浮岛屿式 (Island Array) 的侧边栏、网格动态环境光背景 (Mesh Gradient Background) 和极尽通透的亚克力材质 (Glassmorphism)，将 `frontend/admin` 后台管理系统打造成类 macOS 桌面端、且具有强烈空间深度的现代效率工具界面。

## 实施细节 (Implementation Details)

### 1. 动态与通透背景 (`src/assets/theme.css`)
*   **Mesh Ambient Background**：在原有的噪点叠加 (Noise Overlay) 基础上，采用 CSS `radial-gradient` 引入微妙柔和的环境光束，让背景带有呼吸般的色彩层次感，而不是枯燥的死白或纯黑。
*   **亚克力面板材质**：移除所有大色块的阻光背景。侧边栏及主要内容块背景调低透明度，加入 `backdrop-filter: blur(...)`，实现玻璃毛玻璃透过效果。
*   **交互弹簧动效 (Spring-based Micro-interactions)**：统一向移动端看齐，为按钮、列表以及侧边栏切换注入 `cubic-bezier(0.4, 0, 0.2, 1)` 并新增 `.active-scale { transform: scale(0.95); }` 等工具类，赋予全场物理按键点击阻尼回馈感。

### 2. 悬浮岛式布局重构 (`src/layouts/AdminLayout.vue`)
*   **去除边框 (Borderless)**：消除 `sidebar` 的 `border-right: 1px solid var(--color-border-light)`，依靠色块和软投影划分视觉边界。
*   **岛屿分离 (Floating Array)**：使左侧导航栏脱离左上边缘，增加外边距 (`margin: 16px`) 和大圆角 (`border-radius: 20px`)，使其成为一个悬空飘浮在背景光上的“中控面板”。
*   **呼吸式侧边栏细节优化**：调整 icon 大小、内部 padding 留白，并在悬停 (`hover`) 状态使用基于大圆角的悬浮背景，提升精致感。
*   **Main Content Area**：主操作区同样配合左侧的岛屿化，增加四周预留大边距、加持圆角。

## 影响评估 (Impact)
*   只针对 `frontend/admin` 的静态 CSS 与 Vue DOM 结构进行安全刷新。
*   完全兼容现有夜间模式逻辑（Dark Mode），不会损坏功能。
