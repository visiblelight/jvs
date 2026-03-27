# Plan 016: 自动化测试体系

## 背景

随着系统模块增多，局部修改可能影响到预期外的其它模块。需要建立一键可运行的自动化测试体系，覆盖前后端所有重要功能。

## 分层策略

### 第一层：后端 API 集成测试（核心）

**技术栈**：pytest + httpx + SQLite 内存库（已在 requirements-dev.txt 中）

每个测试用例走真实 HTTP 请求，使用独立的测试数据库，测试完自动清理。

**目录结构**：
```
backend/tests/
  conftest.py          # 测试 DB、TestClient、创建测试用户/token 的 fixture
  test_auth.py         # 登录、token 校验、权限拦截
  test_todo.py         # 事项 CRUD、分类、标签、执行时间/截止时间联动
  test_news.py         # 文章 CRUD、分类、来源
  test_uploads.py      # 图片上传类型/大小校验
  test_access_key.py   # key 的生成与鉴权
```

**重点覆盖场景**：
- 正常路径：创建 → 查询 → 更新 → 删除
- 字段清空：`scheduled_at=null`、`due_date=null` 等能否正确写入
- 边界值：文件大小超限、非法文件类型、必填项缺失
- 权限隔离：A 用户无法读写 B 用户的数据
- 分页与过滤：按分类/标签/状态筛选结果正确

### 第二层：前端 E2E 测试

**技术栈**：Playwright

只覆盖最核心的用户操作流，不测组件渲染细节。

**目录结构**：
```
frontend/admin/e2e/
  auth.spec.js     # 登录/登出流程
  todo.spec.js     # 创建事项 → 列表出现 → 编辑 → 完成 → 删除
  news.spec.js     # 发布文章 → 列表出现 → 编辑 → 删除
```

### 第三层：一键运行脚本

项目根目录 `test.sh`：
1. 后端：临时测试环境 → pytest → 打印覆盖率
2. 前端：启动 dev server → Playwright → 关闭 server

### 第四层：GitHub Actions 集成

每次 push 自动触发测试，测试失败则不执行部署步骤。

## 实施顺序

- [ ] Phase 1：后端测试基础设施（conftest.py）
- [ ] Phase 2：test_auth.py
- [ ] Phase 3：test_todo.py（最复杂，优先级最高）
- [ ] Phase 4：test_news.py、test_uploads.py、test_access_key.py
- [ ] Phase 5：前端 E2E（Playwright）
- [ ] Phase 6：GitHub Actions 集成
- [ ] Phase 7：根目录 test.sh 一键脚本

## 约定

- 测试数据库：SQLite 内存库，每个测试函数独立事务，互不干扰
- 测试用户：fixture 自动创建，密码固定为测试值
- 不 mock 数据库：所有测试走真实 ORM，避免 mock 与真实行为不一致
