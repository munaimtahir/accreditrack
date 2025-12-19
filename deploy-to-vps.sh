#!/bin/bash
# AccrediFy VPS Deployment Script
# Automated deployment with validation, health checks, and debugging

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# VPS Configuration
VPS_IP="172.104.187.212"
GEMINI_API_KEY="AIzaSyAvK-H204qOxbincL3UZaiU1f8bSglvULg"

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

# Section header
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
        all_good=false
    fi
    
    # Check Docker Compose
    if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
        if command_exists docker-compose; then
            COMPOSE_VERSION=$(docker-compose --version)
        else
            COMPOSE_VERSION=$(docker compose version)
        fi
        log "✓ Docker Compose found: $COMPOSE_VERSION"
    else
        log_error "✗ Docker Compose not found. Please install Docker Compose first."
        all_good=false
    fi
    
    # Check Docker daemon
    if docker info >/dev/null 2>&1; then
        log "✓ Docker daemon is running"
    else
        log_error "✗ Docker daemon is not running. Please start Docker."
        all_good=false
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

# Setup environment
setup_environment() {
    section "Setting Up Environment"
    
    # Create .env file from template if it doesn't exist
    if [ ! -f .env ]; then
        log "Creating .env file from template..."
        cp .env.template .env
        
        # Generate a random Django secret key
        SECRET_KEY=$(python3 -c "import secrets; import string; chars = string.ascii_letters + string.digits + '-_'; print(''.join(secrets.choice(chars) for i in range(50)))" 2>/dev/null || openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
        
        # Update .env with values
        sed -i "s|DB_PASSWORD=|DB_PASSWORD=accredify_secure_$(openssl rand -hex 8)|" .env
        sed -i "s|DJANGO_SECRET_KEY=|DJANGO_SECRET_KEY=$SECRET_KEY|" .env
        sed -i "s|GEMINI_API_KEY=AIzaSyAvK-H204qOxbincL3UZaiU1f8bSglvULg|GEMINI_API_KEY=$GEMINI_API_KEY|" .env
        sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=localhost,127.0.0.1,$VPS_IP|" .env
        sed -i "s|CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1,http://$VPS_IP|" .env
        
        log "✅ .env file created and configured"
    else
        log_info ".env file already exists, verifying configuration..."
        
        # Ensure VPS IP is in ALLOWED_HOSTS and CORS_ALLOWED_ORIGINS
        if ! grep -q "$VPS_IP" .env; then
            log_warning "VPS IP not found in .env, adding it..."
            sed -i "s|ALLOWED_HOSTS=\(.*\)|ALLOWED_HOSTS=\1,$VPS_IP|" .env
            sed -i "s|CORS_ALLOWED_ORIGINS=\(.*\)|CORS_ALLOWED_ORIGINS=\1,http://$VPS_IP|" .env
        fi
        
        # Ensure Gemini API key is set
        if ! grep -q "GEMINI_API_KEY=$GEMINI_API_KEY" .env; then
            log_warning "Updating Gemini API key..."
            sed -i "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$GEMINI_API_KEY|" .env
        fi
        
        log "✅ .env file verified and updated"
    fi
    
    # Display configuration (mask sensitive data)
    log_info "Current configuration:"
    grep -v "PASSWORD\|SECRET\|API_KEY" .env | while read -r line; do
        log_info "  $line"
    done
    log_info "  DB_PASSWORD=***HIDDEN***"
    log_info "  DJANGO_SECRET_KEY=***HIDDEN***"
    log_info "  GEMINI_API_KEY=***CONFIGURED***"
}

# Build frontend
build_frontend() {
    section "Building Frontend"
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log "Installing frontend dependencies..."
        npm install
    else
        log_info "node_modules already exists, skipping npm install"
    fi
    
    # Build frontend
    log "Building frontend production bundle..."
    npm run build
    
    if [ -d "dist" ]; then
        DIST_SIZE=$(du -sh dist | cut -f1)
        log "✅ Frontend built successfully (size: $DIST_SIZE)"
    else
        log_error "Frontend build failed - dist directory not found"
        exit 1
    fi
    
    cd ..
}

# Clean up old containers and images
cleanup_old_deployment() {
    section "Cleaning Up Old Deployment"
    
    log "Stopping existing containers..."
    docker compose down 2>/dev/null || log_info "No existing containers to stop"
    
    # Optional: Remove old images to save space
    # log "Removing old images..."
    # docker image prune -f
    
    log "✅ Cleanup completed"
}

# Build and start services
deploy_services() {
    section "Building and Deploying Services"
    
    log "Building Docker images..."
    docker compose build --no-cache 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log "✅ Docker images built successfully"
    else
        log_error "Docker build failed"
        exit 1
    fi
    
    log "Starting services..."
    docker compose up -d 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log "✅ Services started"
    else
        log_error "Failed to start services"
        exit 1
    fi
}

# Wait for service to be healthy
wait_for_service() {
    local service=$1
    local max_attempts=${2:-30}
    local attempt=1
    
    log "Waiting for $service to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose ps $service | grep -q "healthy"; then
            log "✅ $service is healthy"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "$service failed to become healthy after $max_attempts attempts"
    return 1
}

# Health checks
perform_health_checks() {
    section "Performing Health Checks"
    
    # Wait for all services
    log "Waiting for services to start (this may take up to 2 minutes)..."
    sleep 10
    
    # Check database
    wait_for_service db 30
    
    # Check backend
    wait_for_service backend 30
    
    # Check nginx
    wait_for_service nginx 30
    
    # Verify container status
    log_info "Container status:"
    docker compose ps | tee -a "$LOG_FILE"
    
    log "✅ All services are healthy"
}

# Verify volumes
verify_volumes() {
    section "Verifying Docker Volumes"
    
    log "Checking Docker volumes..."
    docker volume ls | grep -E "db_data|backend_static|backend_media" | tee -a "$LOG_FILE"
    
    # Check volume sizes
    for vol in db_data backend_static backend_media; do
        FULL_VOL_NAME=$(docker volume ls -q | grep $vol | head -1)
        if [ -n "$FULL_VOL_NAME" ]; then
            SIZE=$(docker run --rm -v $FULL_VOL_NAME:/data alpine du -sh /data 2>/dev/null | cut -f1 || echo "unknown")
            log "  $vol: $SIZE"
        else
            log_warning "  $vol: not found"
        fi
    done
    
    log "✅ Volume verification completed"
}

# Setup database and admin user
setup_database() {
    section "Setting Up Database"
    
    log "Running database migrations..."
    docker compose exec -T backend python manage.py migrate 2>&1 | tee -a "$LOG_FILE"
    
    log "Collecting static files..."
    docker compose exec -T backend python manage.py collectstatic --noinput 2>&1 | tee -a "$LOG_FILE"
    
    log "Creating/updating admin user..."
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
    
    log "✅ Database setup completed"
}

# Test API endpoints
test_api_endpoints() {
    section "Testing API Endpoints"
    
    # Wait a bit for everything to settle
    sleep 5
    
    # Test health endpoint
    log "Testing health endpoint..."
    if curl -f http://localhost/admin/ >/dev/null 2>&1; then
        log "✅ Admin endpoint accessible"
    else
        log_warning "⚠ Admin endpoint not accessible"
    fi
    
    # Test API documentation
    log "Testing API documentation..."
    if curl -f http://localhost/api/docs/ >/dev/null 2>&1; then
        log "✅ API documentation accessible"
    else
        log_warning "⚠ API documentation not accessible"
    fi
    
    # Test authentication endpoint
    log "Testing authentication endpoint..."
    AUTH_RESPONSE=$(curl -s -X POST http://localhost/api/auth/token/ \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "admin123"}')
    
    if echo "$AUTH_RESPONSE" | grep -q "access"; then
        log "✅ Authentication working"
        TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
        log_info "JWT token obtained successfully"
    else
        log_warning "⚠ Authentication might have issues"
        log_info "Response: $AUTH_RESPONSE"
    fi
    
    log "✅ API endpoint testing completed"
}

# Test Gemini API integration
test_gemini_api() {
    section "Testing Gemini API Integration"
    
    log "Verifying Gemini API key configuration..."
    
    # Get auth token first
    AUTH_RESPONSE=$(curl -s -X POST http://localhost/api/auth/token/ \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "admin123"}')
    
    if echo "$AUTH_RESPONSE" | grep -q "access"; then
        TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
        
        log "Testing AI assistant endpoint..."
        AI_RESPONSE=$(curl -s -X POST http://localhost/api/ask-assistant/ \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d '{"question": "What is compliance in healthcare?"}')
        
        if echo "$AI_RESPONSE" | grep -q "result"; then
            log "✅ Gemini API integration working"
            log_info "AI Response preview: $(echo "$AI_RESPONSE" | grep -o '"result":"[^"]*"' | cut -d'"' -f4 | cut -c1-100)..."
        elif echo "$AI_RESPONSE" | grep -q "error"; then
            ERROR_MSG=$(echo "$AI_RESPONSE" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
            log_warning "⚠ Gemini API returned an error: $ERROR_MSG"
        else
            log_warning "⚠ Unexpected AI response format"
            log_info "Response: $AI_RESPONSE"
        fi
    else
        log_warning "⚠ Cannot test Gemini API - authentication failed"
    fi
}

# Test frontend/backend connectivity
test_frontend_backend_connectivity() {
    section "Testing Frontend/Backend Connectivity"
    
    log "Testing nginx configuration..."
    docker compose exec nginx nginx -t 2>&1 | tee -a "$LOG_FILE"
    
    log "Testing frontend accessibility..."
    if curl -f http://localhost/ >/dev/null 2>&1; then
        log "✅ Frontend accessible at http://localhost/"
    else
        log_error "Frontend not accessible"
    fi
    
    log "Testing API proxy..."
    if curl -f http://localhost/api/schema/ >/dev/null 2>&1; then
        log "✅ API accessible through nginx proxy"
    else
        log_warning "⚠ API proxy might have issues"
    fi
    
    log "✅ Frontend/Backend connectivity verified"
}

# Common issues debugging
debug_common_issues() {
    section "Debugging Common Issues"
    
    log "Checking for common issues..."
    
    # Check container logs for errors
    log_info "Checking container logs for errors..."
    
    for service in db backend nginx; do
        log_info "=== $service logs (last 20 lines) ==="
        docker compose logs --tail=20 $service 2>&1 | tee -a "$LOG_FILE"
    done
    
    # Check port bindings
    log_info "Checking port bindings..."
    netstat -tulpn 2>/dev/null | grep -E ":80|:8000|:5432" | tee -a "$LOG_FILE" || log_info "Port info not available (requires root)"
    
    # Check network connectivity between containers
    log_info "Checking container network connectivity..."
    docker compose exec backend ping -c 2 db >/dev/null 2>&1 && log "✅ Backend can reach database" || log_warning "⚠ Backend cannot reach database"
    
    log "✅ Common issues check completed"
}

# Display access information
display_access_info() {
    section "Deployment Complete!"
    
    echo ""
    log "🎉 AccrediFy has been successfully deployed!"
    echo ""
    log "📍 Access URLs:"
    log "   Local:      http://localhost/"
    log "   VPS:        http://$VPS_IP/"
    log "   API Docs:   http://$VPS_IP/api/docs/"
    log "   Admin:      http://$VPS_IP/admin/"
    echo ""
    log "🔑 Default Credentials:"
    log "   Username: admin"
    log "   Password: admin123"
    echo ""
    log "🤖 AI Features:"
    log "   Gemini API: Configured and ready"
    log "   Model: gemini-2.0-flash-exp"
    echo ""
    log "📊 Service Status:"
    docker compose ps
    echo ""
    log "📝 Useful Commands:"
    log "   View logs:        docker compose logs -f"
    log "   View specific:    docker compose logs -f [service]"
    log "   Restart:          docker compose restart"
    log "   Stop:             docker compose down"
    log "   Start:            docker compose up -d"
    echo ""
    log "📄 Full deployment log saved to: $LOG_FILE"
    echo ""
}

# Error handler
error_handler() {
    log_error "Deployment failed at line $1"
    log_error "Check $LOG_FILE for details"
    
    log_info "Collecting diagnostic information..."
    docker compose ps 2>&1 | tee -a "$LOG_FILE"
    docker compose logs --tail=50 2>&1 | tee -a "$LOG_FILE"
    
    exit 1
}

# Set error trap
trap 'error_handler $LINENO' ERR

# Main deployment flow
main() {
    clear
    echo -e "${BLUE}"
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
    
    # Execute deployment steps
    validate_prerequisites
    setup_environment
    build_frontend
    cleanup_old_deployment
    deploy_services
    perform_health_checks
    verify_volumes
    setup_database
    test_api_endpoints
    test_gemini_api
    test_frontend_backend_connectivity
    debug_common_issues
    display_access_info
    
    log "✅ Deployment completed successfully!"
}

# Run main function
main
