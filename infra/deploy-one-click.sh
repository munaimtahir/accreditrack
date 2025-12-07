#!/bin/bash

###############################################################################
# ONE-CLICK DEPLOYMENT SCRIPT FOR ACCEDITRACK
# This script handles complete deployment with all checks and automation
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         ACCEDITRACK - ONE-CLICK DEPLOYMENT                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Pre-flight checks
echo -e "${BLUE}🔍 Running pre-flight checks...${NC}"

# Check Docker
if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo -e "${YELLOW}💡 Please install Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo -e "${YELLOW}💡 Please start Docker and try again${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed and running${NC}"

# Check Docker Compose
if ! command_exists docker; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is available${NC}"

# Check secrets directory
if [ ! -d "./secrets" ]; then
    echo -e "${RED}❌ Error: secrets directory not found${NC}"
    echo -e "${YELLOW}💡 Creating secrets directory...${NC}"
    mkdir -p ./secrets
    echo -e "${RED}❌ Please create secrets/backend.env and secrets/frontend.env${NC}"
    exit 1
fi

# Check environment files
if [ ! -f "./secrets/backend.env" ]; then
    echo -e "${RED}❌ Error: secrets/backend.env not found${NC}"
    exit 1
fi

if [ ! -f "./secrets/frontend.env" ]; then
    echo -e "${RED}❌ Error: secrets/frontend.env not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Environment files found${NC}"

# Validate environment variables
echo -e "${BLUE}🔍 Validating environment configuration...${NC}"
set +e
source ./secrets/backend.env 2>/dev/null || true
set -e

if [ -z "${DB_PASSWORD}" ] || [ "${DB_PASSWORD}" = "your-secure-database-password" ]; then
    echo -e "${RED}❌ Error: DB_PASSWORD is not set or is using default value${NC}"
    exit 1
fi

if [ -z "${SECRET_KEY}" ] || [ "${SECRET_KEY}" = "your-secret-key-here-change-in-production" ]; then
    echo -e "${RED}❌ Error: SECRET_KEY is not set or is using default value${NC}"
    exit 1
fi

if [ -z "${ALLOWED_HOSTS}" ]; then
    echo -e "${YELLOW}⚠️  Warning: ALLOWED_HOSTS is not set${NC}"
fi

echo -e "${GREEN}✓ Environment configuration validated${NC}"

# Stop existing containers if running
echo -e "${BLUE}🛑 Stopping existing containers (if any)...${NC}"
docker compose down 2>/dev/null || true

# Pull latest code (if git repo)
if [ -d "../.git" ]; then
    echo -e "${BLUE}📥 Pulling latest code...${NC}"
    cd ..
    git pull || echo -e "${YELLOW}⚠️  Warning: Could not pull latest changes${NC}"
    cd infra
fi

# Build images
echo -e "${BLUE}🔨 Building Docker images (this may take a few minutes)...${NC}"
docker compose build --no-cache

# Start database
echo -e "${BLUE}🗄️  Starting database...${NC}"
docker compose up -d db

# Wait for database
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
MAX_TRIES=60
TRIES=0
until docker compose exec -T db pg_isready -U "${DB_USER:-accreditrack}" > /dev/null 2>&1; do
    TRIES=$((TRIES+1))
    if [ "$TRIES" -ge "$MAX_TRIES" ]; then
        echo -e "${RED}❌ Error: Database did not become ready in time${NC}"
        docker compose logs db
        exit 1
    fi
    printf "."
    sleep 1
done
echo ""
echo -e "${GREEN}✓ Database is ready${NC}"

# Run migrations
echo -e "${BLUE}🔄 Running database migrations...${NC}"
docker compose run --rm backend python config/manage.py migrate --noinput

# Collect static files
echo -e "${BLUE}📦 Collecting static files...${NC}"
docker compose run --rm backend python config/manage.py collectstatic --noinput

# Start all services
echo -e "${BLUE}🚀 Starting all services...${NC}"
docker compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 15

# Check service health
echo -e "${BLUE}🏥 Checking service health...${NC}"
sleep 5

# Display status
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    DEPLOYMENT COMPLETE                       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ All services are running!${NC}"
echo ""
echo -e "${BLUE}📊 Service Status:${NC}"
docker compose ps

echo ""
echo -e "${CYAN}🌐 Access Information:${NC}"
echo -e "  ${YELLOW}Application URL:${NC} http://34.123.45.67"
echo -e "  ${YELLOW}API Endpoint:${NC} http://34.123.45.67/api/v1"
echo -e "  ${YELLOW}Health Check:${NC} http://34.123.45.67/api/v1/health/"
echo ""

echo -e "${CYAN}📝 Useful Commands:${NC}"
echo -e "  ${YELLOW}View all logs:${NC}        docker compose logs -f"
echo -e "  ${YELLOW}View backend logs:${NC}    docker compose logs -f backend"
echo -e "  ${YELLOW}View frontend logs:${NC}    docker compose logs -f frontend"
echo -e "  ${YELLOW}View nginx logs:${NC}       docker compose logs -f nginx"
echo -e "  ${YELLOW}Stop services:${NC}         docker compose down"
echo -e "  ${YELLOW}Restart services:${NC}      docker compose restart"
echo -e "  ${YELLOW}Rebuild and redeploy:${NC} ./deploy-one-click.sh"
echo ""

echo -e "${GREEN}🎉 Deployment successful! Your application is ready to use.${NC}"
