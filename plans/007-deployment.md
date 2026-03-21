# Plan 007 - 生产环境部署

**日期**: 2026-03-21
**状态**: 执行中

---

## 一、功能概述

提供两套一键部署方案，均基于 Docker Compose，通过 profiles 共用同一份 `docker-compose.yml`：

- **方案一（build-1.sh）**：前后端全部容器化部署在同一台 VPS
- **方案二（build-2.sh）**：前端部署到 Vercel，后端容器化部署在 VPS

---

## 二、技术方案

### 2.1 容器架构

**共用服务（两个方案均包含）**：

| 服务 | 镜像 | 说明 |
|------|------|------|
| backend | 本地构建 | FastAPI + uvicorn，启动前自动跑 alembic 迁移 |
| postgres | postgres:16-alpine | 生产数据库，数据通过 named volume 持久化 |
| redis | redis:7-alpine | 缓存/队列，数据持久化 |
| certbot | certbot/certbot | SSL 证书申请与自动续签 |
| nginx | nginx:alpine | 反向代理，profile 决定配置 |

**profile 区分**：

- `plan1`：nginx 挂载前端 dist 目录，同时提供静态文件服务和 API 代理
- `plan2`：nginx 仅提供 API 代理 + CORS 支持

### 2.2 路由规划

**方案一**：
```
https://DOMAIN/           → dist/admin/    (管理后台)
https://DOMAIN/mobile/    → dist/mobile/   (移动工作台)
https://DOMAIN/api/       → backend:8000
https://DOMAIN/uploads/   → backend:8000
```

**方案二**：
```
https://DOMAIN/api/       → backend:8000
https://DOMAIN/uploads/   → backend:8000
前端 admin/mobile 部署在 Vercel
```

### 2.3 数据库策略

| 环境 | DATABASE_URL | 驱动 |
|------|------|------|
| 开发 | `sqlite:///./dev.db`（默认） | 内置 |
| 生产 | `postgresql://user:pass@postgres:5432/jvs` | psycopg2-binary |

`database.py` 已根据 URL 前缀自动切换 `connect_args`，无需其他代码改动。

### 2.4 Alembic 迁移

`alembic/env.py` 已正确配置，从 `settings.DATABASE_URL` 读取连接地址。`versions/` 目录当前为空，本次执行生成初始迁移文件（包含全部现有表）。

Backend 容器 command：
```
sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"
```

### 2.5 SSL

1. 首次部署：HTTP-only 临时 nginx → certbot webroot 申请证书 → 替换完整 HTTPS 配置
2. 自动续签：certbot 容器每 12h 检查，到期前 30 天自动续签并 reload nginx
3. 域名通过 `.env` 中 `DOMAIN` 变量配置，nginx 模板用 `envsubst` 渲染

### 2.6 前端构建（方案一）

通过 Node 临时容器完成构建，无需在宿主机安装 Node：
```bash
docker run --rm -v $(pwd)/frontend/admin:/app -w /app node:20-alpine \
  sh -c "npm ci && npm run build"
```
产物输出到 `dist/admin/` 和 `dist/mobile/`，nginx 容器直接挂载。

### 2.7 CORS

`main.py` 添加 `CORSMiddleware`，`allow_origins` 从 `CORS_ORIGINS` 环境变量读取：
- 方案一：填入自有域名即可
- 方案二：需同时填入 VPS 域名和 Vercel 域名

---

## 三、涉及文件清单

### 新建
```
jvs/
├── docker-compose.yml
├── nginx/
│   ├── plan1.conf.template
│   └── plan2.conf.template
├── backend/Dockerfile
├── frontend/admin/vercel.json
└── build-1.sh
└── build-2.sh
```

### 修改
```
backend/requirements.txt          # 新增 psycopg2-binary
backend/app/core/config.py        # 新增 CORS_ORIGINS
backend/main.py                   # 新增 CORSMiddleware
.env.example                      # 补齐生产环境变量
```

### 生成
```
backend/alembic/versions/0001_initial.py   # autogenerate 初始迁移
```

---

## 四、环境变量（.env.example 新增）

```ini
# ── 通用 ──────────────────────────────────────────────
DOMAIN=example.com
SECRET_KEY=change-me-in-production
DEPLOY_PLAN=plan1                        # plan1 或 plan2

# ── 数据库 ────────────────────────────────────────────
DATABASE_URL=postgresql://jvs:password@postgres:5432/jvs
POSTGRES_DB=jvs
POSTGRES_USER=jvs
POSTGRES_PASSWORD=change-me

# ── Redis ─────────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── CORS ──────────────────────────────────────────────
# 方案一：填自有域名；方案二：还需加 Vercel 域名
CORS_ORIGINS=https://example.com

# ── 方案二专用 ────────────────────────────────────────
VERCEL_TOKEN=                            # vercel CLI token
# VITE_API_BASE_URL 在 Vercel 项目环境变量里配置，不写在此处
```

---

## 五、执行顺序

1. `backend/requirements.txt` 新增 `psycopg2-binary`
2. `config.py` 新增 `CORS_ORIGINS`
3. `main.py` 新增 `CORSMiddleware`
4. 生成 alembic 初始迁移文件
5. `backend/Dockerfile`
6. `docker-compose.yml`（含 profiles）
7. `nginx/plan1.conf.template`
8. `nginx/plan2.conf.template`
9. `build-1.sh`
10. `build-2.sh`
11. `frontend/admin/vercel.json`
12. `.env.example` 更新
