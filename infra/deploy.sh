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

# Check and create secrets directory
if [ ! -d "./secrets" ]; then
    echo -e "${YELLOW}📁 Creating secrets directory...${NC}"
    mkdir -p ./secrets
fi

# Create backend.env if it doesn't exist
if [ ! -f "./secrets/backend.env" ]; then
    echo -e "${YELLOW}📝 Creating secrets/backend.env with production values...${NC}"
    cat > ./secrets/backend.env << 'EOF'
# Django Settings
SECRET_KEY=5fbv&1sh_!&10k)wlqa@i^a!7%^-uecy$v8&e^zwbqz%7j@$4a
DEBUG=False
ALLOWED_HOSTS=34.123.45.67,localhost,127.0.0.1,accreditrack.com,www.accreditrack.com

# Database Configuration
DB_NAME=accreditrack
DB_USER=accreditrack
DB_PASSWORD=OQXDXwq29vxo/mFidP8mLN9i3P/xZcK+0FEcg/girzA=
DB_HOST=db
DB_PORT=5432

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://34.123.45.67,https://34.123.45.67,http://accreditrack.com,https://accreditrack.com,http://www.accreditrack.com,https://www.accreditrack.com

# Security Settings
SECURE_SSL_REDIRECT=False

# Optional: Email Configuration (uncomment and configure if needed)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
EOF
fi

# Create frontend.env if it doesn't exist
if [ ! -f "./secrets/frontend.env" ]; then
    echo -e "${YELLOW}📝 Creating secrets/frontend.env with production values...${NC}"
    cat > ./secrets/frontend.env << 'EOF'
# API Base URL - Production API endpoint
NEXT_PUBLIC_API_URL=http://34.123.45.67/api/v1
EOF
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
