#!/usr/bin/env bash
# 数据库恢复脚本
# 用法：./restore.sh backups/backup_20260327_020000.sql.gz

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# ── 参数检查 ───────────────────────────────────────────────────────────────────
if [ $# -ne 1 ]; then
    echo "用法: $0 <备份文件路径>"
    echo "示例: $0 backups/backup_20260327_020000.sql.gz"
    echo ""
    echo "可用备份："
    find "$SCRIPT_DIR/backups" -maxdepth 1 -name "backup_*.sql.gz" | sort | while read -r f; do
        echo "  $(basename "$f")  ($(du -sh "$f" | cut -f1))"
    done
    exit 1
fi

BACKUP_FILE="$1"
[ -f "$BACKUP_FILE" ] || { log "ERROR: 备份文件不存在: $BACKUP_FILE"; exit 1; }

# ── 读取 .env ──────────────────────────────────────────────────────────────────
[ -f "$SCRIPT_DIR/.env" ] || { log "ERROR: .env not found"; exit 1; }
set -a; source "$SCRIPT_DIR/.env"; set +a

# ── 二次确认 ───────────────────────────────────────────────────────────────────
echo ""
echo "⚠️  警告：此操作将清空数据库 '$POSTGRES_DB' 并从备份恢复！"
echo "   备份文件：$BACKUP_FILE"
echo ""
read -r -p "确认继续？输入 yes 继续，其他任意键取消：" CONFIRM
[ "$CONFIRM" = "yes" ] || { echo "已取消。"; exit 0; }

# ── 执行恢复 ───────────────────────────────────────────────────────────────────
log "Restoring from $BACKUP_FILE ..."

gunzip -c "$BACKUP_FILE" | PGPASSWORD="$POSTGRES_PASSWORD" docker compose exec -T postgres \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    --single-transaction \
    -v ON_ERROR_STOP=1

log "Restore complete."
