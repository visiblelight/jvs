# 部署配置与验收

## 同源 VPS

仓库根目录 `.env` 配置 `DEPLOY_MODE=standalone`，后台 origin 与 API、上传文件相同。`build-1.sh` 构建已选择版本，固定 Compose 项目名 jvs、获取部署锁，升级数据库后启动 profile plan1。前端环境中不要遗留分离部署的 VITE_API_BASE_URL；移动端 VITE_BASE_PATH 保持 /mobile/。

## 公共 Edge

`DEPLOY_MODE=edge` 使用 profile edge，只有 nginx-edge 加入外部 jvs-edge 网络。数据库与后端留在项目内部网络，TLS 由公共 Edge 管理。详见 shared-edge.md；不要在普通更新中停止公共 Edge 或删除其他 profile 的容器。

## Vercel + VPS

两个 Vercel 项目分别以 frontend/admin、frontend/mobile 为根目录，构建 npm run build，输出 dist。两者均设置 `VITE_API_BASE_URL=https://api.example.com`，仅允许 http(s) origin，不含 /api、查询字符串或凭据；mobile 设置 `VITE_BASE_PATH=/`。前端将请求发往后端 origin 的 /api，图片发往该 origin 的 /uploads；Vercel 的 SPA 回退只负责本项目页面。

后端 CORS_ORIGINS 逐个列出前端 origin，生产连接必须使用 HTTPS。在根目录配置后端 `.env` 与 VERCEL_TOKEN 后，build-2.sh 构建当前已选择版本、使用固定 jvs 项目名和部署锁、profile plan2，然后调用 Vercel CLI 发布。它不会自动拉取其他版本，也不会使用 remove-orphans 删除其他 profile 容器。执行前需单独完成前端构建配置及账户关联。

## 必查项目

- 后台和移动端登录、深层路由刷新、事项创建／编辑、打卡、新闻读取。
- 头像、Markdown 图片及真实上传内容，非法 HTML 上传不可访问。
- CORS 允许实际前端；API 请求不能返回 index.html。
- 新建事项时间符合浏览器时区，打卡午夜符合 Asia/Shanghai。
- `/health`、Edge 的 `/healthz` 及各服务状态。单独更新 JVS 不影响其他项目。
- 镜像不含 `.env`、开发库、上传数据、虚拟环境或缓存。

Plan 024 涉及的历史打卡周期切换必须先完成 plan024-upgrade.md 的核验，不随应用启动自动执行。
