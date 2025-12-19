#!/bin/bash
# AccrediFy Single-Click VPS Deployment Script
# Usage: ./deploy-vps.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# VPS Configuration
VPS_IP="${VPS_IP:-172.104.187.212}"
GEMINI_API_KEY="${GEMINI_API_KEY:-AIzaSyAvK-H204qOxbincL3UZaiU1f8bSglvULg}"

# Logging
LOG_FILE="deployment_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

section() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}$1${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    section "Checking Prerequisites"
    
    local missing=()
    
    command -v docker >/dev/null 2>&1 || missing+=("docker")
    command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1 || missing+=("docker-compose")
    command -v node >/dev/null 2>&1 || missing+=("node")
    command -v npm >/dev/null 2>&1 || missing+=("npm")
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing[*]}"
        log_info "Please install: ${missing[*]}"
        exit 1
    fi
    
    docker info >/dev/null 2>&1 || {
        log_error "Docker daemon is not running"
        exit 1
    }
    
    log "✅ All prerequisites met"
}

# Setup environment
setup_env() {
    section "Setting Up Environment"
    
    if [ ! -f .env ]; then
        log "Creating .env file from template..."
        cp .env.template .env
        
        # Generate secure passwords
        DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
        SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
        
        # Update .env
        sed -i "s|DB_PASSWORD=|DB_PASSWORD=$DB_PASSWORD|" .env
        sed -i "s|DJANGO_SECRET_KEY=|DJANGO_SECRET_KEY=$SECRET_KEY|" .env
        sed -i "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$GEMINI_API_KEY|" .env
        sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=localhost,127.0.0.1,$VPS_IP|" .env
        sed -i "s|CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1,http://$VPS_IP|" .env
        
        log "✅ .env file created"
    else
        log_info ".env file exists, updating VPS IP..."
        # Ensure VPS IP is in config
        if ! grep -q "$VPS_IP" .env; then
            sed -i "s|ALLOWED_HOSTS=\(.*\)|ALLOWED_HOSTS=\1,$VPS_IP|" .env
            sed -i "s|CORS_ALLOWED_ORIGINS=\(.*\)|CORS_ALLOWED_ORIGINS=\1,http://$VPS_IP|" .env
        fi
        # Update Gemini API key if provided
        if [ -n "$GEMINI_API_KEY" ]; then
            sed -i "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$GEMINI_API_KEY|" .env
        fi
        log "✅ .env file updated"
    fi
}

# Build frontend
build_frontend() {
    section "Building Frontend"
    
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        log "Installing frontend dependencies..."
        npm ci
    fi
    
    log "Building frontend..."
    npm run build
    
    if [ ! -d "dist" ]; then
        log_error "Frontend build failed - dist directory not found"
        exit 1
    fi
    
    log "✅ Frontend built successfully"
    cd ..
}

# Deploy with Docker Compose
deploy_docker() {
    section "Deploying with Docker Compose"
    
    log "Stopping existing containers..."
    docker compose down 2>/dev/null || true
    
    log "Building Docker images..."
    docker compose build --no-cache
    
    log "Starting services..."
    docker compose up -d
    
    log "✅ Services started"
}

# Wait for services
wait_for_services() {
    section "Waiting for Services"
    
    log "Waiting for database..."
    for i in {1..30}; do
        if docker compose exec -T db pg_isready -U accredify >/dev/null 2>&1; then
            log "✅ Database is ready"
            break
        fi
        sleep 2
    done
    
    log "Waiting for backend..."
    for i in {1..60}; do
        if docker compose exec -T backend curl -f http://localhost:8000/admin/ >/dev/null 2>&1; then
            log "✅ Backend is ready"
            break
        fi
        sleep 2
    done
    
    log "Waiting for nginx..."
    sleep 5
    if curl -f http://localhost/ >/dev/null 2>&1; then
        log "✅ Nginx is ready"
    else
        log_warning "Nginx may not be fully ready yet"
    fi
}

# Run migrations
run_migrations() {
    section "Running Database Migrations"
    
    log "Running migrations..."
    docker compose exec -T backend python manage.py migrate --noinput
    
    log "Collecting static files..."
    docker compose exec -T backend python manage.py collectstatic --noinput
    
    log "✅ Migrations completed"
}

# Create admin user
create_admin() {
    section "Setting Up Admin User"
    
    log "Creating admin user..."
    docker compose exec -T backend python manage.py shell <<EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created')
else:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print('✅ Admin user password updated')
EOF
    
    log "✅ Admin user ready (username: admin, password: admin123)"
}

# Health checks
health_check() {
    section "Health Checks"
    
    log "Checking services..."
    docker compose ps
    
    log "Testing API..."
    if curl -f http://localhost/api/schema/ >/dev/null 2>&1; then
        log "✅ API is accessible"
    else
        log_warning "API may not be fully ready"
    fi
    
    log "Testing frontend..."
    if curl -f http://localhost/ >/dev/null 2>&1; then
        log "✅ Frontend is accessible"
    else
        log_warning "Frontend may not be fully ready"
    fi
}

# Display summary
display_summary() {
    section "Deployment Complete!"
    
    echo ""
    log "🎉 AccrediFy deployed successfully!"
    echo ""
    log "📍 Access URLs:"
    log "   Local:      http://localhost/"
    log "   VPS:        http://$VPS_IP/"
    log "   API Docs:   http://$VPS_IP/api/docs/"
    log "   Admin:      http://$VPS_IP/admin/"
    echo ""
    log "🔑 Admin Credentials:"
    log "   Username: admin"
    log "   Password: admin123"
    echo ""
    log "📊 Service Status:"
    docker compose ps
    echo ""
    log "📝 Useful Commands:"
    log "   View logs:     docker compose logs -f"
    log "   Restart:       docker compose restart"
    log "   Stop:           docker compose down"
    echo ""
    log "📄 Deployment log: $LOG_FILE"
    echo ""
}

# Main execution
main() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║     AccrediFy Single-Click VPS Deployment Script           ║"
    echo "║                                                              ║"
    echo "║  VPS IP: $VPS_IP"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    
    check_prerequisites
    setup_env
    build_frontend
    deploy_docker
    wait_for_services
    run_migrations
    create_admin
    health_check
    display_summary
    
    log "✅ Deployment completed successfully!"
}

# Run main
main
