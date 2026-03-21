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
[ -n "${VERCEL_TOKEN:-}" ]      || error "VERCEL_TOKEN is not set in .env (required for plan2)"

# ── 3. 拉取最新代码 ────────────────────────────────────────────────────────────
info "Pulling latest code..."
git pull

# ── 4. 构建后端镜像 ────────────────────────────────────────────────────────────
info "Building backend image..."
docker compose build backend

# ── 5. 启动数据库和 Redis ──────────────────────────────────────────────────────
info "Starting postgres and redis..."
docker compose up -d postgres redis
info "Waiting for postgres to be ready..."
sleep 10

# ── 6. 数据库迁移 ──────────────────────────────────────────────────────────────
info "Running database migrations..."
docker compose run --rm backend alembic upgrade head

# ── 7. SSL 证书 ────────────────────────────────────────────────────────────────
CERT_PATH="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"

if docker compose run --rm certbot sh -c "[ -f '${CERT_PATH}' ]" 2>/dev/null; then
    info "SSL certificate already exists, skipping issuance."
else
    info "Obtaining SSL certificate for ${DOMAIN}..."
    docker compose --profile plan2 up -d nginx-plan2
    sleep 3
    docker compose run --rm certbot certonly \
        --webroot \
        --webroot-path /var/www/certbot \
        --email "admin@${DOMAIN}" \
        --agree-tos \
        --no-eff-email \
        -d "${DOMAIN}" || warn "SSL certificate issuance failed. Continuing without HTTPS."
fi

# ── 8. 启动全部后端服务 ────────────────────────────────────────────────────────
info "Starting all backend services (plan2)..."
docker compose --profile plan2 up -d --remove-orphans

# Reload nginx
sleep 2
docker compose exec nginx-plan2 nginx -s reload 2>/dev/null || true

# ── 9. 部署前端到 Vercel ───────────────────────────────────────────────────────
info "Deploying frontend/admin to Vercel..."
if ! command -v vercel &>/dev/null; then
    info "Installing Vercel CLI..."
    npm install -g vercel --silent
fi

cd frontend/admin
VERCEL_TOKEN="${VERCEL_TOKEN}" vercel --prod --yes --token "${VERCEL_TOKEN}"
cd "$SCRIPT_DIR"

info "Deploying frontend/mobile to Vercel..."
cd frontend/mobile
VERCEL_TOKEN="${VERCEL_TOKEN}" vercel --prod --yes --token "${VERCEL_TOKEN}"
cd "$SCRIPT_DIR"

info "✓ Deployment complete (plan2)"
info "  Backend API: https://${DOMAIN}/api/"
info "  Frontend:    Check Vercel dashboard for URLs"
info ""
warn "  Remember to set VITE_API_BASE_URL=https://${DOMAIN} in Vercel project settings"
