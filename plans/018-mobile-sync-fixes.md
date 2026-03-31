# Plan 018: 移动工作台同步修复

## 背景

管理后台经过多轮迭代后，移动工作台未做相应调整，存在前后端数据契约不一致的严重问题，部分功能完全无法正常工作。

## 问题清单

### Bug（功能性错误，必须修复）

#### Bug 1：优先级字段类型不匹配 — 创建/编辑事项必定失败或数据错乱
- **表现**：前端发送 `priority: "high"/"medium"/"low"`，后端期望 `priority: 1~5`
- **影响**：TodoFormSheet.vue、TodoView.vue 的筛选
- **涉及文件**：TodoFormSheet.vue、TodoView.vue、stores/todo.js

#### Bug 2：状态值不匹配 — 勾选完成操作无效
- **表现**：前端发送 `status: "done"`，后端期望 `status: "completed"`；列表也用 `"done"` 做判断，但后端返回的是 `"completed"`
- **影响**：TodoView.vue 的 toggleDone、状态标签过滤、完成态样式
- **涉及文件**：TodoView.vue

#### Bug 3：分类名显示崩溃
- **表现**：前端用 `item.category.name` 访问分类名，但后端返回的是扁平字段 `category_name`（字符串），无 category 对象
- **影响**：TodoView.vue 第 58 行、NewsDetailView.vue 第 11 行
- **涉及文件**：TodoView.vue、NewsDetailView.vue

#### Bug 4：新闻详情 Markdown 渲染未做 XSS 防护
- **表现**：`marked()` 输出直接赋给 `v-html`，未经 DOMPurify 过滤（管理后台已修复，移动端漏了）
- **涉及文件**：NewsDetailView.vue

### 功能缺失（后端已支持但移动端未实现）

#### 缺失 1：重要程度字段
- 后端有 `importance: 1~5`，移动端完全未展示和编辑
- **处理**：表单增加重要程度选择，列表高重要度项给出标识

#### 缺失 2：执行时间（scheduled_at）及联动逻辑
- 后端支持 scheduled_at，指定执行时间时 due_date = scheduled_at
- **处理**：表单增加"指定执行时间"开关，与管理后台逻辑一致

#### 缺失 3：标签展示
- store 已 fetch tags 但列表和表单未使用
- **处理**：列表显示标签（彩色胶囊），表单支持选择标签

#### 缺失 4：新闻详情图片样式
- 管理后台已给 `.article-content img` 加了 margin/shadow，移动端缺失
- **处理**：补充 img 样式

### 用词不统一

- 移动端全称"待办"，管理后台统一为"事项"
- 状态标签"进行中"→"未完成"（对应 pending），"已完成"→"已完成"（对应 completed）
- 表单标题"编辑待办"→"编辑事项"，"新建待办"→"新建事项"，"创建待办"→"创建事项"

## 实施步骤

- [x] Phase 1：修复 Bug 1~3（优先级/状态/分类名）— 不修这些移动端基本不可用
- [x] Phase 2：修复 Bug 4（DOMPurify）+ 图片样式
- [x] Phase 3：补齐重要程度 + 执行时间联动
- [x] Phase 4：补齐标签展示与选择
- [x] Phase 5：统一用词（待办→事项，进行中→未完成，等）
