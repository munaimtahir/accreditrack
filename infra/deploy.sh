#!/bin/bash

set -e

echo "🚀 Starting deployment process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env files exist
if [ ! -f "../backend/.env.production" ]; then
    echo -e "${RED}❌ Error: backend/.env.production not found${NC}"
    echo -e "${YELLOW}💡 Copy backend/.env.production.example to backend/.env.production and update the values${NC}"
    exit 1
fi

if [ ! -f "../frontend/.env.production" ]; then
    echo -e "${RED}❌ Error: frontend/.env.production not found${NC}"
    echo -e "${YELLOW}💡 Copy frontend/.env.production.example to frontend/.env.production and update the values${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    exit 1
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Error: docker compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment files found${NC}"
echo -e "${GREEN}✓ Docker is running${NC}"

# Pull latest changes (if using git)
if [ -d "../.git" ]; then
    echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
    cd ..
    git pull || echo "Warning: Could not pull latest changes"
    cd infra
fi

# Build and start services
echo -e "${YELLOW}🔨 Building Docker images...${NC}"
docker compose build --no-cache

echo -e "${YELLOW}🗄️  Starting database...${NC}"
docker compose up -d db

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 10

echo -e "${YELLOW}🔄 Running database migrations...${NC}"
docker compose run --rm backend python config/manage.py migrate

echo -e "${YELLOW}📦 Collecting static files...${NC}"
docker compose run --rm backend python config/manage.py collectstatic --noinput

echo -e "${YELLOW}🚀 Starting all services...${NC}"
docker compose up -d

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${YELLOW}📊 Checking service status...${NC}"
docker compose ps

echo -e "${GREEN}🎉 Your application should now be running!${NC}"
echo -e "${YELLOW}💡 Access your application at: http://your-google-cloud-ip${NC}"
echo -e "${YELLOW}💡 To view logs: docker compose logs -f${NC}"
echo -e "${YELLOW}💡 To stop services: docker compose down${NC}"
