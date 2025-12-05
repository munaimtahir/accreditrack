# CI_CD.md – Continuous Integration / Deployment

## CI (GitHub Actions)

Goal: keep it simple and fast.

### Workflows

1. **Backend CI** – `.github/workflows/backend-ci.yml`
   - Trigger: push and PR to main branches.
   - Steps:
     - Set up Python.
     - Install dependencies from `backend/requirements.txt`.
     - Run `python -m compileall` for syntax check.
     - Run `pytest` for backend tests.

2. **Frontend CI** – `.github/workflows/frontend-ci.yml`
   - Trigger: push and PR.
   - Steps:
     - Set up Node.
     - Install deps with `npm ci` in `frontend/`.
     - Run `npm run lint`.
     - Run `npm test`.

3. **Monorepo Meta CI** (optional later)
   - Lint Markdown or check formatting.

## CD (Deployment)

Not fully automated yet; recommended approach:

- Build Docker images for backend and frontend.
- Push to a container registry.
- Use docker-compose or Kubernetes manifest on the target server.
- Manage secrets via environment variables or secret manager.

Document environment variables in `docs/SETUP.md` and `.env.example` files.

CD automation can be added later once the hosting environment is chosen.
