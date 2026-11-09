# 开发指南

## 初始化

Python 3.12，Node.js 22。后端创建并激活 `.venv`，运行 `python -m pip install --require-hashes -r requirements-dev.txt`，复制 `.env.example` 为 `.env`，按实际环境修改配置。

先 `alembic upgrade head`，再 `python -m scripts.init_admin`。应用启动不建表；不要先用 `create_all` 建表再执行初始迁移。管理员初始密码应立即修改。后端通过 `uvicorn main:app --reload` 在 8000 端口启动。

两个前端目录分别 `npm ci`、`npm run dev`；后台 3001，移动端 3002 的 `/mobile/`。同源开发不需设置 VITE_API_BASE_URL。

## 测试

在 backend 运行 `python -m pytest tests/ -q`，默认使用内存 SQLite，开启外键；每个测试在独立事务和保存点中运行。上传测试使用临时目录，迁移测试使用临时数据库，不应连接已有业务库。

PostgreSQL 测试需要独立的 PostgreSQL 16 实例，账号具有创建数据库权限。环境变量示例（仅测试账号）：

```bash
TEST_DATABASE_URL=postgresql://jvs_test:jvs_test@127.0.0.1:55424/jvs_plan024_test \
TEST_POSTGRES_URL=postgresql://jvs_test:jvs_test@127.0.0.1:55424/jvs_plan024_test \
python -m pytest tests/ -q
```

- `TEST_DATABASE_URL`：运行完整 API 测试，测试前建表、结束清表；仅允许名字以 `_test` 结尾的专用空库。
- `TEST_POSTGRES_URL`：提供迁移、会话时区、历史周期映射及并发测试的管理连接；这些用例另建随机临时数据库，结束后清理。不要填写生产连接。
- 没有 PostgreSQL 时，SQLite 的并发重复插入用例明确跳过；CI 会实际运行 PostgreSQL 对应用例。
- `python -m pytest tests/test_migrations.py -q` 独立进程验证 Alembic，防止主应用导入掩盖模型漏注册。

两个前端目录分别运行 `npm test`、`npm run build`。时间行为测试覆盖 UTC、上海和纽约时区、夏令时、表单往返、业务午夜刷新和内部图片 origin。

## 依赖锁定

`requirements.in` 为运行依赖输入，`requirements-dev.in` 为测试依赖输入并约束到运行锁。`requirements.txt` 和 `requirements-dev.txt` 是带哈希的安装锁，生产、测试、Docker 和 CI 均使用锁文件安装。

更新时在干净的 Linux/Python 3.12 环境安装 `pip-tools==7.6.2`，执行：

```bash
pip-compile --generate-hashes --no-emit-index-url --no-emit-trusted-host requirements.in -o requirements.txt
pip-compile --generate-hashes --no-emit-index-url --no-emit-trusted-host requirements-dev.in -o requirements-dev.txt
```

编译默认复用已有锁定版本。升级特定依赖时明确选择目标，重新运行两种数据库及前端检查，不从任意开发机直接 freeze 作为生产依赖。Node 依赖通过已提交的 package-lock.json 与 npm ci 安装。

## 修改与迁移

新增模型必须在 `app/models/__init__.py` 注册；提交迁移前在空库和带数据的临时库验证 `alembic upgrade head` 与 `alembic check`。不要未经检查接受自动生成的删除表操作。所有时间点字段使用 `UTCDateTime`，HTTP 输入采用带时区 datetime；业务日期单独处理。

开发遵循 CLAUDE.md：先写并确认 plan，代码、API 和数据结构文档同步更新，未经授权不提交、推送或部署。

## ToDo 草稿维护（Plan 025）

两端使用相同的草稿存储与编辑器保护逻辑，相关实现位于 `utils/drafts.mjs`、`utils/editorProtection.mjs` 和 `composables/useTodo*.js`。独立存储键避免整份草稿列表相互覆盖；Web Locks 在编辑器生命周期内保持独占，无法取得锁时使用新 UUID 写副本。不要在登录跳转、提交开始或失败时清理草稿。

`npm test` 包含草稿完整往返、空稿、账号／后端／应用隔离、写入失败重试、清理失败、多窗口锁与兼容回退、损坏数据、事项版本、返回 URL 和旧 401 的回归用例。浏览器验收应在独立数据库和测试账号中模拟业务 401、写入 5xx、本机存储配额失败，并检查两端重新登录后的表单与提交结果；不得在生产库制造故障。

编辑旧稿时读取并比较服务端 `updated_at`，发现冲突后阻止覆盖。这是客户端的提交前检查，尚不提供服务器原子版本条件更新，因此不能消除“检查与写入之间”极短窗口内的并发修改。请求超时保留草稿、不自动重试；当前创建接口没有幂等键，应提示先核对列表再重试。

本机持久化只是同浏览器的恢复能力，不应承诺强制结束进程、清空站点存储后仍能恢复；需要跨设备恢复时再引入服务端草稿协议。尚在上传的图片二进制不保存在草稿中，已完成的 Markdown 图片链接作为正文保存。
