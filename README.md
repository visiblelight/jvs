# JVS

模块化 Web 应用，包含 PC 管理后台、移动工作台和开放 API。现有功能包括事项（分类、标签、日历、评论、归档与回收站）、打卡（周期、积分、补录）、新闻、用户与板块权限、Access Key。

## 结构与技术栈

- `backend/`：Python 3.12、FastAPI、SQLAlchemy、Alembic；开发默认 SQLite，生产 PostgreSQL 16。
- `frontend/admin/`：Vue 3、Vite、Pinia、Vue Router，完整管理界面。
- `frontend/mobile/`：独立 Vue 应用，复用管理 API，提供简化工作台。
- `nginx/`、`docker-compose.yml`：同源部署、公共 Edge 入口或 API-only 模式。
- `docs/`：API、数据结构、开发及部署说明；`plans/`：功能和修复方案记录。
- Redis 是预留基础设施，目前没有业务使用。

## 本地开发

使用 Python 3.12 和 Node.js 22（部署前端构建也可使用 Node.js 20）。

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
python -m scripts.init_admin
uvicorn main:app --reload
```

应用启动不自动建表。先迁移再创建账号；初始化脚本使用的演示密码应立即修改，详见脚本输出。

在另外两个终端分别执行：

```bash
cd frontend/admin
npm ci
npm run dev
```

```bash
cd frontend/mobile
npm ci
npm run dev
```

管理后台：`http://localhost:3001/`；移动工作台：`http://localhost:3002/mobile/`；API 文档：`http://localhost:8000/docs`。两个开发服务代理 `/api` 和 `/uploads` 到 8000 端口。

## 验证

```bash
cd backend
python -m pytest tests/ -q
```

在两个前端目录分别运行 `npm test` 和 `npm run build`。PostgreSQL 回归、迁移一致性检查、锁定依赖更新见 [开发指南](docs/development/README.md)。测试必须使用独立测试库，不能指定已有业务数据库。

## 时间约定

- 时间点统一按 UTC 存取，API 返回带 `Z` 的 ISO 8601，界面转换为浏览器本地时间。
- 输入截止时间、执行时间、新闻发布时间和日历查询边界必须带时区。
- 打卡日期、ISO 周和月份使用 `BUSINESS_TIMEZONE=Asia/Shanghai`；纯日期不是时间点。
- 旧版无时区响应由前端按已知 UTC 语义兼容解析，不给历史数据库整体加减 8 小时。

已有打卡记录的部署升级，先阅读 [Plan 024 发布前核验与回滚](docs/deployment/plan024-upgrade.md)。历史周期变更不会随应用启动自动执行。

## 部署方式

| 方式 | 脚本／配置 | 前端路径 | TLS |
| --- | --- | --- | --- |
| 独立 VPS | `build-1.sh`，`DEPLOY_MODE=standalone` | 后台 `/`，移动端 `/mobile/` | 本项目 nginx + certbot |
| 公共 Edge | `build-1.sh`，`DEPLOY_MODE=edge` | 后台 `/`，移动端 `/mobile/` | 独立 Edge 项目 |
| Vercel + VPS | `build-2.sh`，两个独立前端项目 | 各自 `/` | Vercel 与后端 nginx |

部署前在仓库根目录配置 `.env`（参考 `backend/.env.example`）。必须填写域名、数据库连接和账号、随机 `SECRET_KEY`、CORS 等配置。不要将 `.env` 或业务数据提交到 Git；后端镜像排除这些本地文件。

部署脚本构建调用者已选择的代码版本，不自动 `git pull`。CI 对 main 的发布使用触发提交的准确 SHA；后端测试、SQLite/PostgreSQL 迁移检查和两个前端测试／构建全部成功才允许发布。提交、推送、部署仍须按项目协作约定授权。

分离部署时，在两个 Vercel 项目设置 `VITE_API_BASE_URL=https://后端域名`（仅 origin，不含 `/api`）；移动端另设 `VITE_BASE_PATH=/`。同源模式不设置前者，移动端默认 `/mobile/`。头像及 Markdown 内部图片使用同一后端 origin。后端 `CORS_ORIGINS` 需列出实际前端 origin。

详见 [部署说明](docs/deployment/deployment.md) 和 [Edge 接入](docs/deployment/shared-edge.md)。

## 数据保留与备份

数据库、上传文件等通过 Docker volume 持久化。事项的“永久删除”仍是二级软删除，数据保留在数据库，但所有业务 API 均不可见；打卡任务删除则级联删除其日志，二者语义不同。

`backup.sh` 提供数据库备份；上传文件需要单独备份。恢复必须在临时库演练，并确认目标库的现状与恢复流程；不要在业务库直接试验。不得执行会删除业务 volume 的 `down -v`。

## 文档

- [API 索引](docs/api/README.md)
- [数据结构](docs/database/schema.md)
- [开发指南](docs/development/README.md)
- [Plan 024 修复方案与验证记录](plans/024-reliability-security-and-timezone-fixes.md)
