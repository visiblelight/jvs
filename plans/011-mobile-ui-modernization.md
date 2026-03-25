# 011 - Mobile UI Modernization Plan

## 目标 (Objective)
全面重构 `frontend/mobile` (移动工作台) 的视觉设计与 UI 交互，抛弃传统的枯燥排版，引入现代化的设计风格，包括：毛玻璃 (Glassmorphism)、无衬线现代排版 (Modern Typography)、流体微交互动效 (Micro-Animations) 以及具有悬浮感的卡片式设计 (Soft Cards)。

## 实施细节 (Implementation Details)

### 1. 全局样式变量与重置 (`src/assets/theme.css`)
*   **字体升级**：引入 `Inter` 或 `Manrope` 作为默认正文字体，配合现有的 `Syne` 增强标题辨识度。
*   **颜色系统升级**：
    *   主色调（Accent）调整为更加鲜亮的渐变紫蓝系。
    *   背景色采用非常浅的灰白色以凸显纯白卡片。
*   **阴影系统升级**：
    *   移除僵硬的投影，引入基于多重柔和层叠的阴影效果 (`box-shadow` values 采用更广的 `blur` 半径)。
    *   新增“光晕彩色投影”支持（Accent drop shadow）。
*   **圆角与几何感**：增大全图的 `border-radius`，如小组件 `12px`，大卡片 `20px-24px`。
*   **过渡动画与微交互**：
    *   新增 `.active-scale` 工具类，利用 `:active` + `transform: scale(0.96)` 赋予所有可点击元素“阻尼按压感”。
    *   统一将动画曲线改为 `cubic-bezier(0.4, 0, 0.2, 1)`（弹簧般更自然的缓动效果）。

### 2. 字体资源注入 (`index.html`)
*   更新 `index.html` 的头部链接，通过 Google Fonts 引入新的正文字体资源。

### 3. 全局布局与底栏重构 (`src/App.vue` 等布局相关文件)
*   **导航栏/底边栏毛玻璃化**：
    *   移除静态纯色背景，使用 `backdrop-filter: blur(20px)` 及 `background-color: rgba(255, 255, 255, 0.7)`。
    *   如果是暗色模式，则调整半透明底色为黑色。
*   **悬浮底边导航 (Floating Tabbar)**：
    *   将原本贴边的底侧导航改为两侧留有外边距、具有药丸形或超大圆角 (`border-radius: 9999px`) 的悬浮栏。

### 4. 核心页面视觉调优 (Login / Home / Todo)
*   去除冗余的硬性边框 (`border`)。
*   在按钮和显眼的控件上部署彩色环境光（Box-shadow 光晕）。
*   增加必要的内边距（Padding）和留白，提升呼吸感。

## 影响范围 (Impact Scope)
仅影响 `frontend/mobile` 前端项目，无后端依赖变更。
修改集中在 CSS 与 Vue 模板层，不影响现有 Pinia 状态或 Vue Router 逻辑。
