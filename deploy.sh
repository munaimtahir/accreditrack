#!/bin/bash
# AccrediFy Production Deployment Script
# Single consolidated script for deploying AccrediFy to VPS or local environment
# Version: 2.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VPS_IP="${VPS_IP:-172.104.187.212}"
GEMINI_API_KEY="${GEMINI_API_KEY:-}"  # Set via environment variable or will prompt
HEALTHCHECK_ENDPOINT="/api/"
LOG_FILE="deployment_$(date +%Y%m%d_%H%M%S).log"

# Logging functions
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
    echo -e "${CYAN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

section() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}$1${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Validate prerequisites
validate_prerequisites() {
    section "Validating Prerequisites"
    
    local all_good=true
    
    # Check Docker
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version)
        log "✓ Docker found: $DOCKER_VERSION"
    else
        log_error "✗ Docker not found. Please install Docker first."
        log_info "Visit: https://docs.docker.com/get-docker/"
        all_good=false
    fi
    
    # Check Docker Compose
    if docker compose version >/dev/null 2>&1; then
        COMPOSE_VERSION=$(docker compose version)
        log "✓ Docker Compose found: $COMPOSE_VERSION"
    elif command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version)
        log "✓ Docker Compose found: $COMPOSE_VERSION"
    else
        log_error "✗ Docker Compose not found. Please install Docker Compose first."
        log_info "Visit: https://docs.docker.com/compose/install/"
        all_good=false
    fi
    
    # Check Docker daemon
    if docker info >/dev/null 2>&1; then
        log "✓ Docker daemon is running"
    else
        log_error "✗ Docker daemon is not running. Please start Docker."
        all_good=false
    fi
    
    # Check Node.js and npm (needed for frontend build)
    if command_exists node; then
        NODE_VERSION=$(node --version)
        log "✓ Node.js found: $NODE_VERSION"
    else
        log_warning "⚠ Node.js not found. Frontend will be built inside Docker container."
    fi
    
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        log "✓ npm found: v$NPM_VERSION"
    else
        log_warning "⚠ npm not found. Frontend will be built inside Docker container."
    fi
    
    # Check internet connectivity
    if ping -c 1 google.com >/dev/null 2>&1; then
        log "✓ Internet connectivity available"
    else
        log_warning "⚠ Cannot reach internet. Some features may not work."
    fi
    
    # Check disk space (require at least 2GB free)
    FREE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$FREE_SPACE" -gt 2 ]; then
        log "✓ Sufficient disk space: ${FREE_SPACE}GB available"
    else
        log_warning "⚠ Low disk space: ${FREE_SPACE}GB available. Recommended: >2GB"
    fi
    
    if [ "$all_good" = false ]; then
        log_error "Prerequisites validation failed. Please fix the issues above."
        exit 1
    fi
    
    log "✅ All prerequisites validated successfully"
}

# Setup environment configuration
setup_environment() {
    section "Setting Up Environment"
    
    if [ ! -f .env ]; then
        log "Creating .env file from template..."
        
        if [ ! -f .env.template ]; then
            log_error ".env.template not found!"
            exit 1
        fi
        
        cp .env.template .env
        
        # Generate secure passwords
        log_info "Generating secure credentials..."
        DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
        SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
        
        # Update .env with generated values
        sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=$DB_PASSWORD|" .env
        sed -i "s|DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$SECRET_KEY|" .env
        sed -i "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$GEMINI_API_KEY|" .env
        sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=localhost,127.0.0.1,$VPS_IP|" .env
        sed -i "s|CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1,http://$VPS_IP|" .env
        
        log "✅ .env file created with secure credentials"
    else
        log_info ".env file already exists, verifying configuration..."
        
        # Update VPS IP if not present
        if ! grep -q "$VPS_IP" .env; then
            log_info "Adding VPS IP to configuration..."
            sed -i "s|ALLOWED_HOSTS=\(.*\)|ALLOWED_HOSTS=\1,$VPS_IP|" .env
            sed -i "s|CORS_ALLOWED_ORIGINS=\(.*\)|CORS_ALLOWED_ORIGINS=\1,http://$VPS_IP|" .env
        fi
        
        # Update Gemini API key if provided
        if [ -n "$GEMINI_API_KEY" ]; then
            sed -i "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$GEMINI_API_KEY|" .env
        fi
        
        log "✅ .env file verified and updated"
    fi
    
    # Display sanitized configuration
    log_info "Current configuration:"
    grep -v "PASSWORD\|SECRET\|API_KEY" .env | while read line; do
        log_info "  $line"
    done
    log_info "  DB_PASSWORD=***HIDDEN***"
    log_info "  DJANGO_SECRET_KEY=***HIDDEN***"
    if grep -q "GEMINI_API_KEY=.\+" .env 2>/dev/null && [ -n "$(grep GEMINI_API_KEY .env | cut -d= -f2)" ]; then
        log_info "  GEMINI_API_KEY=***CONFIGURED***"
    else
        log_warning "  GEMINI_API_KEY=***NOT CONFIGURED*** (AI features will not work)"
    fi
}

# Build frontend
build_frontend() {
    section "Building Frontend"
    
    if [ -d "frontend" ]; then
        log "Installing frontend dependencies..."
        cd frontend
        
        if command_exists npm; then
            log "Running npm ci (clean install)..."
            if ! npm ci 2>&1 | tee -a "../$LOG_FILE"; then
                log_warning "npm ci failed, trying npm install instead..."
                npm install 2>&1 | tee -a "../$LOG_FILE"
            fi
            
            log "Building frontend production bundle..."
            npm run build 2>&1 | tee -a "../$LOG_FILE"
            
            if [ -d "dist" ]; then
                DIST_SIZE=$(du -sh dist | cut -f1)
                log "✅ Frontend built successfully (size: $DIST_SIZE)"
            else
                log_error "Frontend build failed - dist directory not found"
                exit 1
            fi
        else
            log_warning "npm not found, frontend will be built inside Docker container"
        fi
        
        cd ..
    else
        log_error "frontend directory not found!"
        exit 1
    fi
}

# Clean up old deployment
cleanup_old_deployment() {
    section "Cleaning Up Old Deployment"
    
    log "Stopping existing containers..."
    docker compose down 2>&1 | tee -a "$LOG_FILE" || true
    
    log "✅ Cleanup completed"
}

# Build and deploy services
deploy_services() {
    section "Building and Deploying Services"
    
    log "Building Docker images..."
    docker compose build 2>&1 | tee -a "$LOG_FILE"
    
    log "✅ Docker images built successfully"
    
    log "Starting services..."
    docker compose up -d 2>&1 | tee -a "$LOG_FILE"
    
    log "✅ Services started"
}

# Wait for services to be healthy
wait_for_services() {
    section "Waiting for Services to be Ready"
    
    log "Waiting for database to be healthy..."
    local db_ready=false
    for i in {1..30}; do
        if docker compose exec -T db pg_isready -U accredify >/dev/null 2>&1; then
            log "✅ Database is healthy"
            db_ready=true
            break
        fi
        echo -n "." | tee -a "$LOG_FILE"
        sleep 2
    done
    echo "" | tee -a "$LOG_FILE"
    
    if [ "$db_ready" = false ]; then
        log_error "Database failed to become healthy"
        docker compose logs db | tail -50 | tee -a "$LOG_FILE"
        exit 1
    fi
    
    log "Waiting for backend to be healthy..."
    local backend_ready=false
    for i in {1..60}; do
        # Using ${HEALTHCHECK_ENDPOINT} instead of /admin/ for healthcheck
        if docker compose exec -T backend curl -f "http://localhost:8000${HEALTHCHECK_ENDPOINT}" >/dev/null 2>&1; then
            log "✅ Backend is healthy"
            backend_ready=true
            break
        fi
        echo -n "." | tee -a "$LOG_FILE"
        sleep 2
    done
    echo "" | tee -a "$LOG_FILE"
    
    if [ "$backend_ready" = false ]; then
        log_error "Backend failed to become healthy"
        log_info "Checking backend logs..."
        docker compose logs backend | tail -50 | tee -a "$LOG_FILE"
        exit 1
    fi
    
    log "Waiting for nginx to be ready..."
    sleep 5
    if curl -f http://localhost/ >/dev/null 2>&1; then
        log "✅ Nginx is ready"
    else
        log_warning "Nginx may not be fully ready yet, but continuing..."
    fi
    
    log "✅ All services are ready"
}

# Create admin user
create_admin_user() {
    section "Setting Up Admin User"
    
    log "Creating admin user..."
    docker compose exec -T backend python manage.py shell <<'EOF' 2>&1 | tee -a "$LOG_FILE"
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
    
    log "✅ Admin user ready"
}

# Run health checks
run_health_checks() {
    section "Running Health Checks"
    
    log "Checking service status..."
    docker compose ps | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log "Testing API endpoint..."
    if curl -f "http://localhost${HEALTHCHECK_ENDPOINT}" >/dev/null 2>&1; then
        log "✅ API is accessible at http://localhost${HEALTHCHECK_ENDPOINT}"
    else
        log_warning "API may not be fully accessible"
    fi
    
    log "Testing API documentation..."
    if curl -f http://localhost/api/docs/ >/dev/null 2>&1; then
        log "✅ API documentation is accessible"
    else
        log_warning "API documentation may not be fully ready"
    fi
    
    log "Testing frontend..."
    if curl -f http://localhost/ >/dev/null 2>&1; then
        log "✅ Frontend is accessible"
    else
        log_warning "Frontend may not be fully ready"
    fi
    
    log "Testing admin panel..."
    if curl -s http://localhost/admin/ | grep -q "Django"; then
        log "✅ Admin panel is accessible"
    else
        log_warning "Admin panel may not be fully ready"
    fi
}

# Display deployment summary
display_summary() {
    section "Deployment Complete!"
    
    echo "" | tee -a "$LOG_FILE"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
    echo -e "${GREEN}║          🎉 AccrediFy Deployed Successfully! 🎉            ║${NC}" | tee -a "$LOG_FILE"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log "📍 Access URLs:"
    log "   Frontend:      http://localhost/"
    log "   Frontend (VPS): http://$VPS_IP/"
    log "   API Root:      http://$VPS_IP/api/"
    log "   API Docs:      http://$VPS_IP/api/docs/"
    log "   Admin Panel:   http://$VPS_IP/admin/"
    echo "" | tee -a "$LOG_FILE"
    
    log "🔑 Admin Credentials:"
    log "   Username: admin"
    log "   Password: admin123"
    log "   ⚠️  Please change the admin password after first login!"
    echo "" | tee -a "$LOG_FILE"
    
    log "📊 Container Status:"
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log "📝 Useful Commands:"
    log "   View all logs:        docker compose logs -f"
    log "   View backend logs:    docker compose logs -f backend"
    log "   View frontend logs:   docker compose logs -f frontend"
    log "   Restart services:     docker compose restart"
    log "   Stop services:        docker compose down"
    log "   Rebuild & restart:    docker compose up -d --build"
    echo "" | tee -a "$LOG_FILE"
    
    log "📄 Deployment log saved to: $LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Error handler
error_handler() {
    log_error "Deployment failed at line $1"
    log_info "Check the log file for details: $LOG_FILE"
    log_info "To view container logs, run: docker compose logs"
    exit 1
}

# Set error trap
trap 'error_handler $LINENO' ERR

# Main execution
main() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║        AccrediFy VPS Deployment Automation Script          ║"
    echo "║                                                            ║"
    echo "║  This script will deploy AccrediFy to your VPS with:      ║"
    echo "║  • Complete environment setup                             ║"
    echo "║  • Docker container deployment                            ║"
    echo "║  • Health checks and validation                           ║"
    echo "║  • Gemini AI API integration                              ║"
    echo "║  • Automated debugging                                    ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    
    log "🚀 Starting AccrediFy deployment to VPS $VPS_IP..."
    log "📝 Deployment log: $LOG_FILE"
    echo ""
    
    validate_prerequisites
    setup_environment
    build_frontend
    cleanup_old_deployment
    deploy_services
    wait_for_services
    create_admin_user
    run_health_checks
    display_summary
    
    log "✅ Deployment completed successfully!"
}

# Run main function
main "$@"
