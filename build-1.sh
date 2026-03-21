#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── 颜色输出 ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── 1. 检查并安装 Docker ───────────────────────────────────────────────────────
install_docker() {
    if command -v docker &>/dev/null; then
        info "Docker already installed: $(docker --version)"
        return
    fi
    info "Installing Docker..."
    if command -v apt-get &>/dev/null; then
        apt-get update -qq
        apt-get install -y -qq ca-certificates curl gnupg
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
            > /etc/apt/sources.list.d/docker.list
        apt-get update -qq
        apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    elif command -v yum &>/dev/null; then
        yum install -y -q yum-utils
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        yum install -y -q docker-ce docker-ce-cli containerd.io docker-compose-plugin
        systemctl enable --now docker
    elif command -v dnf &>/dev/null; then
        dnf install -y -q dnf-plugins-core
        dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
        dnf install -y -q docker-ce docker-ce-cli containerd.io docker-compose-plugin
        systemctl enable --now docker
    else
        error "Unsupported OS. Please install Docker manually: https://docs.docker.com/engine/install/"
    fi
    info "Docker installed successfully."
}

install_docker

# ── 2. 加载 .env ───────────────────────────────────────────────────────────────
[ -f .env ] || error ".env file not found. Copy .env.example and fill in your values."
set -a; source .env; set +a
[ -n "${DOMAIN:-}" ]            || error "DOMAIN is not set in .env"
[ -n "${SECRET_KEY:-}" ]        || error "SECRET_KEY is not set in .env"
[ -n "${POSTGRES_PASSWORD:-}" ] || error "POSTGRES_PASSWORD is not set in .env"

# ── 3. 拉取最新代码 ────────────────────────────────────────────────────────────
info "Pulling latest code..."
git pull

# ── 4. 构建前端（通过 Node Docker 容器，无需宿主机安装 Node）────────────────────
info "Building frontend/admin..."
mkdir -p dist/admin dist/mobile
docker run --rm \
    -v "$(pwd)/frontend/admin:/app" \
    -w /app \
    node:20-alpine \
    sh -c "npm ci --silent && npm run build"
cp -r frontend/admin/dist/. dist/admin/

info "Building frontend/mobile..."
docker run --rm \
    -v "$(pwd)/frontend/mobile:/app" \
    -w /app \
    node:20-alpine \
    sh -c "npm ci --silent && npm run build"
cp -r frontend/mobile/dist/. dist/mobile/

# ── 5. 构建后端镜像 ────────────────────────────────────────────────────────────
info "Building backend image..."
docker compose build backend

# ── 6. 启动数据库和 Redis ──────────────────────────────────────────────────────
info "Starting postgres and redis..."
docker compose up -d postgres redis
info "Waiting for postgres to be ready..."
until docker compose exec postgres pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" 2>/dev/null; do
    echo 'waiting for postgres...'; sleep 2;
done

# ── 7. 数据库迁移 ──────────────────────────────────────────────────────────────
info "Running database migrations..."
docker compose run --rm backend alembic upgrade head

# ── 8. SSL 证书 ────────────────────────────────────────────────────────────────
CERT_PATH="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"

if [ -f "/var/lib/docker/volumes/jvs_letsencrypt/_data/live/${DOMAIN}/fullchain.pem" ] 2>/dev/null ||
   docker run --rm -v jvs_letsencrypt:/etc/letsencrypt alpine \
       sh -c "[ -f '/etc/letsencrypt/live/${DOMAIN}/fullchain.pem' ]" 2>/dev/null; then
    info "SSL certificate already exists, skipping issuance."
else
    info "Obtaining SSL certificate for ${DOMAIN} (first-time, standalone mode)..."
    # 首次申请：nginx 尚未启动（启动需要证书），用 standalone 模式直接监听 80 端口
    docker compose stop nginx-plan1 2>/dev/null || true
    docker run --rm \
        -p 80:80 \
        -v jvs_letsencrypt:/etc/letsencrypt \
        certbot/certbot certonly \
        --standalone \
        --email "admin@${DOMAIN}" \
        --agree-tos \
        --no-eff-email \
        -d "${DOMAIN}" || warn "SSL certificate issuance failed. Continuing without HTTPS."
fi

# ── 9. 启动全部服务 ────────────────────────────────────────────────────────────
info "Starting all services (plan1)..."
docker compose --profile plan1 up -d --remove-orphans

# Reload nginx to pick up the certificate
sleep 2
docker compose exec nginx-plan1 nginx -s reload 2>/dev/null || true

info "✓ Deployment complete (plan1)"
info "  Admin:  https://${DOMAIN}/"
info "  Mobile: https://${DOMAIN}/mobile/"
info "  API:    https://${DOMAIN}/api/"
