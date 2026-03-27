#!/usr/bin/env bash
# 数据库备份脚本
# 用法：./backup.sh
# 建议通过 cron 每天凌晨 2 点执行：
#   0 2 * * * /项目目录/backup.sh >> /项目目录/backups/backup.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BACKUP_DIR="$SCRIPT_DIR/backups"
KEEP_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.sql.gz"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# ── 读取 .env ──────────────────────────────────────────────────────────────────
[ -f "$SCRIPT_DIR/.env" ] || { log "ERROR: .env not found"; exit 1; }
set -a; source "$SCRIPT_DIR/.env"; set +a

[ -n "${POSTGRES_USER:-}"     ] || { log "ERROR: POSTGRES_USER not set";     exit 1; }
[ -n "${POSTGRES_DB:-}"       ] || { log "ERROR: POSTGRES_DB not set";       exit 1; }
[ -n "${POSTGRES_PASSWORD:-}" ] || { log "ERROR: POSTGRES_PASSWORD not set"; exit 1; }

# ── 创建备份目录 ───────────────────────────────────────────────────────────────
mkdir -p "$BACKUP_DIR"

# ── 执行备份 ───────────────────────────────────────────────────────────────────
log "Starting backup → $BACKUP_FILE"

PGPASSWORD="$POSTGRES_PASSWORD" docker compose exec -T postgres \
    pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
    | gzip > "$BACKUP_FILE"

SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
log "Backup complete. Size: $SIZE"

# ── 清理超过 7 天的旧备份 ──────────────────────────────────────────────────────
DELETED=$(find "$BACKUP_DIR" -maxdepth 1 -name "backup_*.sql.gz" -mtime "+$KEEP_DAYS" -print -delete | wc -l | tr -d ' ')
[ "$DELETED" -gt 0 ] && log "Deleted $DELETED old backup(s) older than ${KEEP_DAYS} days."

# ── 列出当前所有备份 ───────────────────────────────────────────────────────────
log "Current backups:"
find "$BACKUP_DIR" -maxdepth 1 -name "backup_*.sql.gz" | sort | while read -r f; do
    echo "  $(basename "$f")  ($(du -sh "$f" | cut -f1))"
done

log "Done."
