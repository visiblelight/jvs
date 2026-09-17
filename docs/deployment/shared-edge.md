# 独立公共入口部署

DEPLOY_MODE=edge 写入服务器 .env；缺省 standalone 保留原有独立 HTTPS 方式。
公共入口由 projects/edge 独立维护；创建外部网络 jvs-edge 后，运行 bash build-1.sh。
edge 模式仅 nginx-edge 加入代理网络，以 jvs-web:80 提供服务，无宿主端口；数据库及后端留在默认网络。证书由 Edge 管理。

CI 发布触发提交的准确 SHA，不再 reset --hard 或二次 git pull；存在受控文件修改则停止，避免覆盖人工改动。发布串行执行，固定 Compose 名 jvs，防止目录变化产生新数据卷。

首次迁移先启动 nginx-edge 并验证，准备公共 Edge 的证书与配置后再停止旧 nginx-plan1/certbot、交接 80/443。普通发布不会停止 Edge，也不会删除其它 profile 的容器。旧模式的容器须在首次切换完成后显式停止；回退则先释放 Edge 的端口再启动旧 nginx-plan1。不得执行 down -v。

配置变更在本地提交后发布，不在服务器修改受 Git 管理的模板。验收应覆盖前端、mobile、API、Web 健康以及独立重启不影响其它网站。
