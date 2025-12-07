# CI_CD.md – Continuous Integration / Deployment

## CI (GitHub Actions)

Goal: keep it simple and fast.

### Workflows

1. **Backend CI** – `.github/workflows/backend-ci.yml`
   - Trigger: push and PR to main/develop branches (when backend files change).
   - Steps:
     - Set up Python 3.12.
     - Install dependencies from `backend/requirements.txt`.
     - Run syntax check with `python -m compileall`.
     - Run linting with flake8 and black (format check).
     - Run tests with pytest (with coverage).
     - Run security scan with bandit.
     - Upload coverage to Codecov.

2. **Frontend CI** – `.github/workflows/frontend-ci.yml`
   - Trigger: push and PR to main/develop branches (when frontend files change).
   - Steps:
     - Set up Node.js 20.
     - Install dependencies with `npm ci`.
     - Run ESLint.
     - Run TypeScript type checking.
     - Run tests with Jest.
     - Build Next.js application.
     - Run security audit with `npm audit`.

3. **Docker Build** – `.github/workflows/docker-build.yml`
   - Trigger: push to main branch or version tags.
   - Steps:
     - Build and push backend Docker image.
     - Build and push frontend Docker image.
     - Uses Docker Buildx with caching.

### Workflow Features

- **Path-based triggers**: Only run when relevant files change.
- **Caching**: Python pip cache, Node npm cache, Docker layer cache.
- **Parallel jobs**: Backend and frontend CI run in parallel.
- **Continue on error**: Linting and security scans don't fail the build.
- **Coverage reporting**: Codecov integration for backend.

## CD (Deployment)

### Current Approach

Deployment is semi-automated using scripts in `infra/`:

1. **Initial Deployment**: `infra/deploy.sh`
   - Checks for environment files.
   - Builds Docker images.
   - Starts database and waits for readiness.
   - Runs migrations.
   - Collects static files.
   - Starts all services.

2. **Updates**: `infra/update.sh`
   - Pulls latest code.
   - Rebuilds images.
   - Runs migrations.
   - Collects static files.
   - Restarts services.

### Automated CD (Future)

For fully automated deployment:

1. **On merge to main**:
   - Build Docker images.
   - Push to container registry.
   - Deploy to staging environment.
   - Run smoke tests.
   - Deploy to production (if staging tests pass).

2. **Container Registry Options**:
   - Docker Hub
   - GitHub Container Registry (ghcr.io)
   - AWS ECR
   - Google Container Registry
   - Azure Container Registry

3. **Deployment Targets**:
   - VPS with Docker Compose (current)
   - Kubernetes cluster
   - Cloud Run / ECS / App Engine

### Secrets Management

- Use GitHub Secrets for CI/CD credentials.
- Use environment variables or secret managers for runtime secrets.
- Never commit `.env.production` files (see `docs/SECURITY.md`).

### Deployment Checklist

Before deploying to production:

- [ ] All CI checks passing
- [ ] Tests passing
- [ ] Security scans clean
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Backup created
- [ ] Deployment window scheduled
- [ ] Rollback plan ready

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Buildx](https://docs.docker.com/buildx/)
- [Deployment Guide](./DEPLOYMENT.md)
- [Security Guide](./SECURITY.md)
