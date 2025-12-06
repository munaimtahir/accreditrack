#!/bin/bash

set -e

echo "🔄 Updating application..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Pull latest changes
echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
cd ..
git pull || { echo -e "${YELLOW}❌ Failed to pull changes. Aborting update.${NC}"; exit 1; }

# Rebuild images
echo -e "${YELLOW}🔨 Rebuilding Docker images...${NC}"
cd infra
docker compose build

# Run migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
docker compose run --rm backend python config/manage.py migrate

# Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
docker compose run --rm backend python config/manage.py collectstatic --noinput

# Restart services
echo -e "${YELLOW}🚀 Restarting services...${NC}"
docker compose down
docker compose up -d

echo -e "${GREEN}✅ Update completed successfully!${NC}"
docker compose ps
