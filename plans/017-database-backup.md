# Plan 017: 数据库自动备份

## 背景

生产环境使用 PostgreSQL（Docker 容器），需要定期备份防止数据丢失。

## 方案

- `backup.sh`：备份脚本，读取 .env 参数，pg_dump 压缩存储，清理 7 天前旧文件
- `restore.sh`：手动恢复脚本，从指定备份文件还原数据库
- VPS cron：每天凌晨 2 点自动执行 backup.sh
- `backups/` 目录：存储备份文件和日志，.gitignore 忽略内容

## 实施步骤

- [x] 编写 backup.sh
- [x] 编写 restore.sh
- [x] 更新 .gitignore
- [ ] VPS 上执行一键 cron 安装命令（手动操作）
