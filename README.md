# JVS

一个模块化 Web 应用，包含管理后台、移动工作台和开放 API 三个组成部分。

## 目录

- [项目结构](#项目结构)
- [功能模块](#功能模块)
- [技术栈](#技术栈)
- [本地开发](#本地开发)
- [生产部署](#生产部署)
  - [方案一：全量 VPS 部署](#方案一全量-vps-部署)
  - [方案二：Vercel + VPS 部署](#方案二vercel--vps-部署)
- [环境变量说明](#环境变量说明)
- [文档](#文档)

---

## 项目结构

```
jvs/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/
│   │   │   ├── admin/        # 管理后台接口（JWT 鉴权）
│   │   │   └── open/         # 开放接口（Access Key 鉴权）
│   │   ├── core/             # 配置、数据库、安全、依赖注入
│   │   ├── models/           # SQLAlchemy 模型
│   │   ├── schemas/          # Pydantic Schema
│   │   └── services/         # 业务逻辑
│   ├── alembic/              # 数据库迁移
│   ├── uploads/              # 用户上传文件（头像等）
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── admin/                # 管理后台（Vue 3 + Vite，端口 3001）
│   └── mobile/               # 移动工作台（Vue 3 + Vite，端口 3002）
├── nginx/
│   ├── plan1.conf.template   # 方案一：静态文件 + API 代理
│   └── plan2.conf.template   # 方案二：仅 API 代理
├── docs/                     # 详细文档
├── plans/                    # 功能规划记录
├── docker-compose.yml
├── build-1.sh                # 方案一一键部署脚本
├── build-2.sh                # 方案二一键部署脚本
└── .env.example              # 环境变量模板（见 backend/.env.example）
```

---

## 功能模块

| 模块 | 说明 |
|------|------|
| **认证** | JWT 登录、修改密码、用户头像上传 |
| **ToDo** | 任务管理，支持分类、标签、优先级、重要度筛选 |
| **新闻** | 文章管理，支持分类、来源、关键词搜索 |
| **Access Key** | 可配置权限范围（scopes）的 API 密钥管理 |
| **开放 API** | 基于 Access Key 的外部接口，当前支持新闻文章提交 |

---

## 技术栈

**后端**

- Python 3.12 + FastAPI + uvicorn
- SQLAlchemy 2.x（开发：SQLite，生产：PostgreSQL）
- Alembic（数据库迁移）
- python-jose（JWT）、passlib（bcrypt 密码哈希）

**前端**

- Vue 3 + Vite + Pinia + Vue Router
- Axios（HTTP 请求）
- Syne + Manrope 字体，支持明暗主题切换

**基础设施**

- Docker + Docker Compose（profiles 区分部署方案）
- nginx（反向代理 / 静态文件服务）
- Let's Encrypt（SSL 自动申请与续签）
- PostgreSQL 16 + Redis 7

---

## 本地开发

### 前提条件

- Python 3.12+
- Node.js 20+
- （可选）Redis

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 复制环境变量（开发默认值已可直接使用）
cp .env.example .env

# 启动开发服务器（http://localhost:8000）
uvicorn main:app --reload
```

首次启动时数据库表会自动创建。如需使用 Alembic 管理迁移：

```bash
alembic upgrade head
```

### 管理后台前端

```bash
cd frontend/admin
npm install
npm run dev    # http://localhost:3001
```

### 移动工作台前端

```bash
cd frontend/mobile
npm install
npm run dev    # http://localhost:3002
```

### 默认账号

首次启动后需手动创建管理员账号，或通过初始化脚本（如有）创建。

---

## 生产部署

两套方案均通过一键脚本完成，脚本会自动检测操作系统并安装 Docker（支持 Ubuntu 20.04+、Debian 11+、CentOS 7+、Rocky Linux 8+）。

### 准备工作

在 VPS 上执行以下步骤：

**1. 获取代码**

```bash
git clone <your-repo-url> /opt/jvs
cd /opt/jvs
```

**2. 创建并填写 .env**

```bash
cp backend/.env.example .env
nano .env   # 或使用你习惯的编辑器
```

必须填写的变量：

```ini
DOMAIN=your-domain.com          # 已解析到本机 IP 的域名
SECRET_KEY=<随机长字符串>        # 建议：openssl rand -hex 32
POSTGRES_DB=jvs
POSTGRES_USER=jvs
POSTGRES_PASSWORD=<强密码>
DATABASE_URL=postgresql://jvs:<上面的密码>@postgres:5432/jvs
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=https://your-domain.com
```

> **注意**：域名必须提前完成 DNS 解析（A 记录指向 VPS IP），否则 SSL 申请会失败。

---

### 方案一：全量 VPS 部署

前后端均运行在同一台 VPS，nginx 同时提供静态文件服务和 API 代理。

**访问地址：**
- 管理后台：`https://your-domain.com/`
- 移动工作台：`https://your-domain.com/mobile/`
- API：`https://your-domain.com/api/`

**执行部署：**

```bash
sudo bash build-1.sh
```

脚本执行流程：
1. 检测 Docker，未安装则自动安装
2. `git pull` 拉取最新代码
3. 通过 Node Docker 容器构建 admin 和 mobile 前端（无需宿主机安装 Node）
4. 构建后端 Docker 镜像
5. 启动 PostgreSQL 和 Redis
6. 执行 `alembic upgrade head` 完成数据库迁移
7. 申请 Let's Encrypt SSL 证书（首次），后续自动续签
8. 启动全部服务

**后续更新：**

```bash
cd /opt/jvs && sudo bash build-1.sh
```

每次执行都会拉取最新代码、重建镜像、自动迁移数据库。

---

### 方案二：Vercel + VPS 部署

前端（admin + mobile）部署到 Vercel，享受全球 CDN 加速；后端运行在 VPS。

**额外准备：**

1. 在 [vercel.com/account/tokens](https://vercel.com/account/tokens) 创建 Token，填入 `.env`：

```ini
VERCEL_TOKEN=your-vercel-token
CORS_ORIGINS=https://your-domain.com,https://your-app.vercel.app
```

2. 在 Vercel 项目的环境变量中设置（**不在本地 .env 中配置**）：

```
VITE_API_BASE_URL=https://your-domain.com
```

**执行部署：**

```bash
sudo bash build-2.sh
```

脚本执行流程（与方案一相比，跳过前端构建，增加 Vercel 部署）：
1. 检测 Docker，未安装则自动安装
2. `git pull` 拉取最新代码
3. 构建后端 Docker 镜像
4. 启动 PostgreSQL 和 Redis
5. 执行数据库迁移
6. 申请 SSL 证书（首次）
7. 启动后端服务（API only nginx）
8. 通过 Vercel CLI 部署 admin 和 mobile

---

### 两种方案对比

| | 方案一 | 方案二 |
|---|---|---|
| 前端托管 | VPS（nginx 静态文件） | Vercel（全球 CDN）|
| 配置复杂度 | 低 | 稍高（需 Vercel 账号和 Token）|
| 前端访问速度 | 取决于 VPS 带宽和地理位置 | 快（Vercel CDN 节点）|
| 费用 | 仅 VPS | VPS + Vercel（免费额度通常足够）|

---

### 持久化数据说明

以下数据通过 Docker named volume 持久化，重建容器不会丢失：

| Volume | 内容 |
|---|---|
| `postgres_data` | 数据库数据 |
| `redis_data` | Redis 持久化数据 |
| `uploads` | 用户上传文件（头像等） |
| `letsencrypt` | SSL 证书 |

**备份建议：**

```bash
# 备份数据库
docker compose exec postgres pg_dump -U jvs jvs > backup_$(date +%Y%m%d).sql

# 备份上传文件
docker run --rm -v jvs_uploads:/data -v $(pwd):/backup alpine \
    tar czf /backup/uploads_$(date +%Y%m%d).tar.gz /data
```

---

## 环境变量说明

完整模板见 `backend/.env.example`。

| 变量 | 开发默认值 | 生产说明 |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./dev.db` | 改为 PostgreSQL URL |
| `SECRET_KEY` | `change-me-in-production` | 必须替换为随机强密钥 |
| `CORS_ORIGINS` | `http://localhost:3001,...` | 填写实际域名 |
| `DOMAIN` | — | VPS 部署必填 |
| `POSTGRES_*` | — | VPS 部署必填 |
| `REDIS_URL` | `redis://localhost:6379/0` | 容器内改为 `redis://redis:6379/0` |
| `VERCEL_TOKEN` | — | 方案二专用 |

---

## 文档

| 文档 | 路径 |
|---|---|
| API 总览 | `docs/api/README.md` |
| 管理后台认证接口 | `docs/api/admin-auth.md` |
| 管理后台 ToDo 接口 | `docs/api/admin-todo.md` |
| 管理后台新闻接口 | `docs/api/admin-news.md` |
| 管理后台 Access Key 接口 | `docs/api/admin-access-key.md` |
| 开放接口（新闻） | `docs/api/open-news.md` |
| 功能说明 | `docs/features/` |
| 部署方案规划 | `plans/007-deployment.md` |
