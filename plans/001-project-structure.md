# Plan 001 - 项目目录结构初始化

**日期**: 2026-03-19
**状态**: 待确认

---

## 一、技术栈确认

| 层次 | 技术选型 | 说明 |
|------|----------|------|
| 后端框架 | FastAPI | 异步、自带 OpenAPI 文档，适合开放 API 鉴权 |
| ORM | SQLAlchemy 2.x | 同时支持 SQLite / PostgreSQL，切换只需改连接串 |
| 数据库迁移 | Alembic | 与 SQLAlchemy 配套，管理 schema 版本 |
| 当前数据库 | SQLite | 开发阶段轻量使用 |
| 未来数据库 | PostgreSQL | 通过环境变量切换，无需改代码 |
| 缓存中间件 | Redis（预留） | 依赖已引入，未正式启用 |
| 前端（管理后台） | Vue 3 + Vite | 独立项目，PC 端布局 |
| 前端（移动工作台） | Vue 3 + Vite | 独立项目，移动端适配 |

---

## 二、目录结构

```
jvs/
├── backend/                    # Python 后端
│   ├── app/
│   │   ├── api/                # 路由层，按模块拆分
│   │   │   ├── admin/          # 管理后台接口
│   │   │   ├── mobile/         # 移动工作台接口
│   │   │   └── open/           # 开放 API（Access Key 鉴权）
│   │   ├── core/               # 核心基础设施
│   │   │   ├── config.py       # 环境配置（数据库URL、Redis等由此切换）
│   │   │   ├── database.py     # SQLAlchemy engine / session 工厂
│   │   │   ├── security.py     # JWT、Access Key 签名验证
│   │   │   └── deps.py         # FastAPI 依赖注入（获取DB session等）
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── schemas/            # Pydantic 请求/响应 Schema
│   │   ├── services/           # 业务逻辑层（供 API 层调用）
│   │   └── utils/              # 通用工具函数
│   ├── alembic/                # 数据库迁移脚本
│   │   └── versions/
│   ├── tests/                  # 后端测试
│   ├── alembic.ini
│   ├── requirements.txt        # 生产依赖
│   ├── requirements-dev.txt    # 开发依赖（pytest 等）
│   ├── .env.example            # 环境变量模板
│   └── main.py                 # FastAPI 应用入口
│
├── frontend/
│   ├── admin/                  # 管理后台（独立 Vue 3 项目）
│   │   ├── src/
│   │   │   ├── api/            # 接口请求封装
│   │   │   ├── assets/
│   │   │   ├── components/
│   │   │   ├── layouts/
│   │   │   ├── router/
│   │   │   ├── stores/         # Pinia 状态管理
│   │   │   ├── views/
│   │   │   └── main.js
│   │   ├── index.html
│   │   ├── vite.config.js
│   │   └── package.json
│   │
│   └── mobile/                 # 移动工作台（独立 Vue 3 项目）
│       ├── src/
│       │   ├── api/
│       │   ├── assets/
│       │   ├── components/
│       │   ├── layouts/
│       │   ├── router/
│       │   ├── stores/
│       │   ├── views/
│       │   └── main.js
│       ├── index.html
│       ├── vite.config.js
│       └── package.json
│
├── docs/                       # 说明文档
│   ├── api/                    # API 接口文档
│   ├── deployment/             # 部署文档
│   └── development/            # 开发指南
│
└── plans/                      # Plan 文档（Claude 生成，供确认留档）
    └── 001-project-structure.md
```

---

## 三、关键设计说明

### 数据库可迁移性
`core/config.py` 通过 `DATABASE_URL` 环境变量控制数据库连接：
- 开发：`sqlite:///./dev.db`
- 生产：`postgresql://user:pass@host/dbname`

SQLAlchemy 抽象层保证代码无需修改，Alembic 管理迁移脚本。

### Redis 预留方式
`requirements.txt` 中引入 `redis[asyncio]`，`core/config.py` 中保留 `REDIS_URL` 配置项，但不强制启动连接，待功能需要时按需激活。

### 开放 API 鉴权
`app/api/open/` 模块独立，使用 Access Key + HMAC 签名或 Bearer Token 方式，与管理后台的 JWT 鉴权隔离。

---

## 四、执行步骤（确认后执行）

1. 创建上述所有目录
2. 生成 `backend/` 骨架文件（`main.py`、`core/config.py`、`core/database.py`、`requirements.txt`、`.env.example`、`alembic.ini`）
3. 初始化 `frontend/admin/` Vue 3 + Vite 项目骨架
4. 初始化 `frontend/mobile/` Vue 3 + Vite 项目骨架
5. 创建 `docs/` 分类子目录及 README 占位文件
