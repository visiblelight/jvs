# Plan 019: 事项列表分区 + 归档功能

## 背景

当前事项列表不区分状态，所有事项混在一起显示。用户希望：
1. 列表分为"未完成"和"已完成"两个区域，勾选完成后自动移到已完成区
2. 已完成的事项可以进一步"归档"，归档表示已完成且不需要再跟进
3. 未完成事项不能直接归档（必须先完成）

## 方案设计

### 后端改动

#### 1. 新增 `archived` 状态值

当前 status 支持：`pending`、`paused`、`completed`

新增 `archived` 状态，表示已完成且归档。校验规则：
- `TodoStatusUpdate` schema 的 pattern 改为 `pending|paused|completed|archived`
- 归档操作 = 将 status 从 `completed` 改为 `archived`
- 取消归档 = 将 status 从 `archived` 改回 `completed`
- 仅 `completed` 状态允许变为 `archived`（在 service 层校验）
- `archived` 不能直接变回 `pending`/`paused`（需先取消归档到 `completed`）

#### 2. 归档时间字段

在 TodoItem 模型新增 `archived_at` 字段（DateTime, nullable），与 `completed_at` 类似：
- 设为 `archived` 时自动填充当前时间
- 离开 `archived` 状态时清空

#### 3. 列表查询支持

`get_items` 的 status 过滤保持不变（精确匹配），前端按需传不同 status 值即可。但默认列表不应显示 archived 的事项，增加逻辑：
- 当 `status` 参数为空时，默认排除 `archived` 状态（只返回 pending/paused/completed）
- 当明确传 `status=archived` 时返回归档事项

#### 4. 数据库迁移

- 新增 `archived_at` 列（nullable DateTime）
- 无需修改 status 列（已是 String 类型）

### 前端改动（管理后台）

#### 1. TodoList.vue — 分区显示

将列表拆分为两个区域：
- **未完成区**（上半部分）：显示 `pending` 和 `paused` 状态的事项，按 created_at DESC 排序
- **已完成区**（下半部分）：显示 `completed` 状态的事项，可折叠，默认展开
- 各区域有小标题（如 "未完成 · 5" / "已完成 · 3"），数字为该区事项数
- 勾选完成后，事项平滑过渡到已完成区

#### 2. TodoSidebar.vue — 归档入口

在"系统"区域新增"归档"按钮（与垃圾桶同级），点击后打开归档面板。

侧栏状态筛选保持不变（未完成/暂停中/已完成），不包含"已归档"，因为归档是独立入口。

#### 3. TodoDetail.vue — 归档操作按钮

事项详情面板中，当事项为 `completed` 状态时，在操作区显示"归档"按钮。
当事项为 `archived` 状态时，显示"取消归档"按钮。

#### 4. TodoArchiveModal.vue — 归档面板（新增）

类似 TodoTrashModal 的弹窗，展示所有归档事项列表：
- 每个事项显示标题、归档时间
- 提供"取消归档"操作（恢复为 completed）
- 提供"永久删除"操作

### 前端改动（移动工作台）

暂不处理，下一轮迭代再同步。

## 实施步骤

- [x] Step 1：后端 — schema/model/service/migration 改动
- [x] Step 2：前端 — TodoList.vue 分区显示（未完成 / 已完成）
- [x] Step 3：前端 — TodoDetail.vue 归档按钮 + TodoArchiveModal.vue 归档面板
- [x] Step 4：前端 — TodoSidebar.vue 归档入口
- [x] Step 5：更新 API 文档
