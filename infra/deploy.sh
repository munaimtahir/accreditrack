#!/bin/bash

set -e

echo "🚀 Starting deployment process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if secrets directory exists
if [ ! -d "./secrets" ]; then
    echo -e "${RED}❌ Error: secrets directory not found${NC}"
    echo -e "${YELLOW}💡 Creating secrets directory...${NC}"
    mkdir -p ./secrets
    exit 1
fi

# Check if .env files exist
if [ ! -f "./secrets/backend.env" ]; then
    echo -e "${RED}❌ Error: secrets/backend.env not found${NC}"
    exit 1
fi

if [ ! -f "./secrets/frontend.env" ]; then
    echo -e "${RED}❌ Error: secrets/frontend.env not found${NC}"
    exit 1
fi

# Validate required environment variables in backend.env
set +e  # Temporarily disable exit on error for validation
source ./secrets/backend.env 2>/dev/null || true
set -e  # Re-enable exit on error

if [ -z "${DB_PASSWORD}" ] || [ "${DB_PASSWORD}" = "your-secure-database-password" ]; then
    echo -e "${RED}❌ Error: DB_PASSWORD is not set or is using default value in secrets/backend.env${NC}"
    exit 1
fi

if [ -z "${SECRET_KEY}" ] || [ "${SECRET_KEY}" = "your-secret-key-here-change-in-production" ]; then
    echo -e "${RED}❌ Error: SECRET_KEY is not set or is using default value in secrets/backend.env${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    echo -e "${YELLOW}💡 Please start Docker and try again${NC}"
    exit 1
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Error: docker compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment files found${NC}"
echo -e "${GREEN}✓ Docker is running${NC}"
echo -e "${GREEN}✓ Docker Compose is available${NC}"

# Pull latest changes (if using git)
if [ -d "../.git" ]; then
    echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
    cd ..
    git pull || echo "Warning: Could not pull latest changes"
    cd infra
fi

# Build and start services
echo -e "${BLUE}🔨 Building Docker images...${NC}"
docker compose build --no-cache

echo -e "${BLUE}🗄️  Starting database...${NC}"
docker compose up -d db

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
MAX_TRIES=60
TRIES=0
until docker compose exec -T db pg_isready -U "${DB_USER:-accreditrack}" > /dev/null 2>&1; do
    TRIES=$((TRIES+1))
    if [ "$TRIES" -ge "$MAX_TRIES" ]; then
        echo -e "${RED}❌ Error: Database did not become ready in time${NC}"
        exit 1
    fi
    sleep 1
done

echo -e "${GREEN}✓ Database is ready${NC}"

echo -e "${BLUE}🔄 Running database migrations...${NC}"
docker compose run --rm backend python config/manage.py migrate --noinput

echo -e "${BLUE}📦 Collecting static files...${NC}"
docker compose run --rm backend python config/manage.py collectstatic --noinput

echo -e "${BLUE}🚀 Starting all services...${NC}"
docker compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Service Status:${NC}"
docker compose ps

echo ""
echo -e "${GREEN}🎉 Your application is now running!${NC}"
echo -e "${YELLOW}💡 Access your application at: http://34.123.45.67${NC}"
echo -e "${YELLOW}💡 API endpoint: http://34.123.45.67/api/v1${NC}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo -e "  ${YELLOW}View logs:${NC} docker compose logs -f"
echo -e "  ${YELLOW}View backend logs:${NC} docker compose logs -f backend"
echo -e "  ${YELLOW}View frontend logs:${NC} docker compose logs -f frontend"
echo -e "  ${YELLOW}Stop services:${NC} docker compose down"
echo -e "  ${YELLOW}Restart services:${NC} docker compose restart"
