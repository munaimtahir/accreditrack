# CI/CD Documentation

This document describes the CI/CD setup for the AccrediTrack application.

## Overview

AccrediTrack uses GitHub Actions for continuous integration and deployment. We have three main workflows:

1. **Backend CI** - Tests and validates the Django backend
2. **Frontend CI** - Tests and builds the Next.js frontend  
3. **Docker Build** - Validates and builds Docker images

## Workflows

### Backend CI (`.github/workflows/backend-ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches (when backend files change)
- Pull requests to `main` or `develop` branches (when backend files change)

**What it does:**
1. Sets up Python 3.12 environment
2. Installs dependencies from `backend/requirements.txt`
3. Runs syntax checks
4. Runs linting with flake8 (non-blocking)
5. Runs code formatting check with black (non-blocking)
6. Sets up PostgreSQL test database
7. Runs Django system checks
8. Runs database migrations
9. Runs pytest test suite with coverage
10. Runs security scan with bandit (non-blocking)
11. Uploads coverage reports to Codecov (non-blocking)

**Requirements:**
- PostgreSQL 16 service container
- Environment variables: `SECRET_KEY`, `DEBUG`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

### Frontend CI (`.github/workflows/frontend-ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches (when frontend files change)
- Pull requests to `main` or `develop` branches (when frontend files change)

**What it does:**
1. Sets up Node.js 20 environment
2. Installs dependencies with npm
3. Runs ESLint for code quality (non-blocking)
4. Runs TypeScript type checking (non-blocking)
5. Runs Jest tests with coverage (non-blocking)
6. Builds the production Next.js application
7. Runs npm security audit (non-blocking)

**Requirements:**
- Node.js 20
- Environment variable: `NEXT_PUBLIC_API_URL`

### Docker Build (`.github/workflows/docker-build.yml`)

**Triggers:**
- Push to `main` branch
- Push of version tags (e.g., `v1.0.0`)
- Manual workflow dispatch

**What it does:**
1. **Validate Docker Compose** - Checks that `docker-compose.yml` is valid
2. **Build Backend Image** - Builds the Django backend Docker image
3. **Build Frontend Image** - Builds the Next.js frontend Docker image

Both build jobs:
- Use Docker Buildx for efficient builds
- Enable GitHub Actions cache for faster builds
- Optionally push to Docker Hub (if credentials are configured)
- Tag images as `latest` and with commit SHA

**Requirements:**
- Docker and Docker Compose
- Optional: `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets for pushing to Docker Hub

## Running Tests Locally

### Backend Tests

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (first time only)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY=your-secret-key
export DEBUG=True
export DB_NAME=accreditrack_test
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_PORT=5432

# Run Django checks
python config/manage.py check

# Run migrations
python config/manage.py migrate

# Run tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run linting
flake8 .

# Check code formatting
black --check .
```

### Frontend Tests

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Run linter
npm run lint

# Run type checking
npx tsc --noEmit

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Build for production
npm run build

# Run security audit
npm audit
```

## Docker Setup

### Local Development with Docker Compose

```bash
# Navigate to infra directory
cd infra

# Create secrets directory and env files
mkdir -p secrets

# Create backend.env
cat > secrets/backend.env << EOF
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=accreditrack
DB_USER=accreditrack
DB_PASSWORD=your-db-password-here
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
EOF

# Create frontend.env
cat > secrets/frontend.env << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF

# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and remove volumes (WARNING: deletes data)
docker compose down -v
```

### Building Individual Images

```bash
# Build backend image
docker build -t accreditrack-backend:latest ./backend

# Build frontend image
docker build -t accreditrack-frontend:latest ./frontend

# Run backend container (example)
docker run -p 8000:8000 \
  -e SECRET_KEY=test \
  -e DB_HOST=host.docker.internal \
  accreditrack-backend:latest

# Run frontend container (example)
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
  accreditrack-frontend:latest
```

### Validating Docker Compose Configuration

```bash
cd infra

# Export required environment variables
export DB_PASSWORD=your-password

# Validate configuration
docker compose config

# Check for syntax errors without starting services
docker compose config --quiet
```

## Environment Variables

### Backend

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | Django secret key | - |
| `DEBUG` | No | Enable debug mode | `False` |
| `DB_NAME` | Yes | Database name | - |
| `DB_USER` | Yes | Database user | - |
| `DB_PASSWORD` | Yes | Database password | - |
| `DB_HOST` | Yes | Database host | `localhost` |
| `DB_PORT` | No | Database port | `5432` |
| `ALLOWED_HOSTS` | No | Allowed hosts | `localhost` |
| `CORS_ALLOWED_ORIGINS` | No | CORS origins | - |

### Frontend

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL | - |

## Troubleshooting

### Backend CI Failures

**Import errors or module not found:**
- Check that all dependencies are in `requirements.txt`
- Ensure Python version is correct (3.12)

**Database connection errors:**
- Verify PostgreSQL service is configured correctly
- Check environment variables are set

**Test failures:**
- Run tests locally to debug
- Check if database migrations are up to date

### Frontend CI Failures

**Build failures:**
- Check that all dependencies are in `package.json`
- Verify Node.js version (20)
- Look for TypeScript errors with `npx tsc --noEmit`

**Lint errors:**
- Run `npm run lint -- --fix` to auto-fix issues
- Check `.eslintrc.json` configuration

### Docker Build Failures

**Build context errors:**
- Ensure Dockerfile paths are correct
- Check that all required files are present

**docker-compose validation fails:**
- Make sure required environment variables are set
- Validate YAML syntax
- Check that env files exist

**Out of disk space:**
- Run `docker system prune -a` to clean up

## Best Practices

1. **Always run tests locally before pushing**
   - Backend: `pytest`
   - Frontend: `npm test && npm run build`

2. **Keep dependencies up to date**
   - Backend: Use `pip list --outdated`
   - Frontend: Use `npm outdated`

3. **Use feature branches**
   - Create branches from `main` or `develop`
   - Open pull requests for review
   - CI runs automatically on PRs

4. **Monitor CI status**
   - Check GitHub Actions tab for workflow status
   - Fix failures promptly
   - Review logs for detailed error messages

5. **Security**
   - Never commit secrets to the repository
   - Use GitHub Secrets for sensitive values
   - Run security audits regularly

## GitHub Secrets Configuration

For full CI/CD functionality, configure these secrets in your GitHub repository:

| Secret | Description | Required |
|--------|-------------|----------|
| `DOCKER_USERNAME` | Docker Hub username | Optional (for pushing images) |
| `DOCKER_PASSWORD` | Docker Hub password/token | Optional (for pushing images) |

To add secrets:
1. Go to repository Settings
2. Navigate to Secrets and variables → Actions
3. Click "New repository secret"
4. Add the secret name and value

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Next.js Deployment Documentation](https://nextjs.org/docs/deployment)
