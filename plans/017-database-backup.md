# Plan 017: 数据库自动备份

## 背景

生产环境使用 PostgreSQL（Docker 容器），需要定期备份防止数据丢失。仅依赖 Docker volume 不够安全，需要独立的备份文件便于还原。

## 方案概述

- **backup.sh**：备份脚本，通过 `pg_dump` 导出并 gzip 压缩，自动清理 7 天前旧文件
- **restore.sh**：手动恢复脚本，从指定备份文件还原数据库，执行前二次确认
- **VPS cron**：每天凌晨 2 点自动触发 backup.sh
- **backups/ 目录**：存储备份文件和日志，内容由 .gitignore 排除

## 已实现内容

- [x] backup.sh
- [x] restore.sh
- [x] .gitignore 更新
- [x] backups/.gitkeep 占位

## VPS 部署操作（手动执行一次）

### 1. 拉取最新代码

```bash
cd /项目目录
git pull origin main
```

### 2. 安装 cron 任务

```bash
# 写入当前用户的 crontab（0 2 * * * = 每天凌晨 2 点）
(crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/backup.sh >> $(pwd)/backups/backup.log 2>&1") | crontab -

# 确认写入成功
crontab -l
```

### 3. 手动执行一次验证

```bash
./backup.sh
```

正常输出示例：
```
[2026-03-27 02:00:01] Starting backup → /项目目录/backups/backup_20260327_020001.sql.gz
[2026-03-27 02:00:03] Backup complete. Size: 256K
[2026-03-27 02:00:03] Current backups:
  backup_20260327_020001.sql.gz  (256K)
[2026-03-27 02:00:03] Done.
```

### 4. 恢复数据库（灾难恢复时使用）

```bash
# 查看可用备份
./restore.sh

# 从指定文件恢复（会提示二次确认）
./restore.sh backups/backup_20260327_020000.sql.gz
```

## 日志查看

```bash
# 查看最近备份日志
tail -50 backups/backup.log

# 查看所有备份文件
ls -lh backups/*.sql.gz
```

## 后续可扩展方向

### Phase 2：异地备份到 OSS

备份文件写入本地后，再上传到阿里云 OSS / 腾讯云 COS，防止 VPS 宕机导致备份文件一起丢失。

实现思路：
- 安装 `ossutil` 或 `coscmd` 命令行工具
- 在 backup.sh 末尾追加上传命令：
  ```bash
  ossutil cp "$BACKUP_FILE" oss://bucket-name/db-backups/
  ```
- OSS 侧设置生命周期规则，30 天自动过期删除

### Phase 3：备份失败通知

备份脚本执行失败时发送通知，目前只写日志，不会主动告警。

实现思路：
- 在 backup.sh 中捕获错误并调用通知接口：
  ```bash
  trap 'notify_failure "$LINENO"' ERR
  ```
- 通知渠道选项：
  - **邮件**：通过 `sendmail` 或 SMTP 服务发送
  - **微信/企业微信**：调用 Webhook 接口
  - **Telegram Bot**：发送到指定频道
- 配置参数写入 .env，不硬编码在脚本里

### Phase 4：备份完整性校验

上传前验证备份文件能正常解压，防止备份文件损坏：
```bash
gunzip -t "$BACKUP_FILE" && log "Integrity check passed."
```
