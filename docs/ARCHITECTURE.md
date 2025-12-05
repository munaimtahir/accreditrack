# ARCHITECTURE.md – System Architecture

## Overview

AccrediTrack is a **monorepo** with:

- **Backend**: Django 5, Django REST Framework, PostgreSQL.
- **Frontend**: Next.js (React) with TypeScript, Tailwind CSS, and shadcn/ui.
- **Infra**: Docker and docker‑compose for local development, with a simple Nginx reverse proxy skeleton for production.

The aim is to keep the system **simple but scalable** for a medium‑sized university or teaching hospital.

## High-Level Diagram (Conceptual)

- User (Browser)
  - ↔ Next.js frontend (SSR/CSR)
  - ↔ Django REST API `/api/...`
    - ↔ PostgreSQL DB
    - ↔ File storage (local or S3‑compatible)

Nginx (or similar) terminates TLS and routes:
- `/` → Next.js
- `/api/` → Django
- `/static/`, `/media/` → Django or object storage.

## Backend Structure

Inside `backend/`:

- `config/` – Django project configuration (settings, urls, wsgi/asgi).
- `accounts/` – User model, auth, roles, and permissions.
- `core/` – Shared utilities (mixins, base models).
- `organizations/` – Departments and future multi‑institution support.
- `proformas/` – ProformaTemplate, ProformaSection, ProformaItem.
- `assignments/` – Assignment, ItemStatus.
- `evidence/` – Evidence and comments.
- `dashboard/` – Aggregated analytics endpoints.

APIs are versioned, starting with `/api/v1/`.

## Frontend Structure

Inside `frontend/`:

- `app/` or `src/app/` – Next.js routing (App Router).
- `components/` – Reusable UI components.
- `features/` – Feature‑specific bundles (auth, proforma-builder, assignments, dashboards).
- `lib/` – API clients, hooks, helpers.
- `styles/` – Global CSS/Tailwind configuration.

Main pages:

- `/login`
- `/dashboard` – role‑aware landing.
- `/proformas`
- `/assignments`
- `/assignments/[id]`
- `/analytics`

## Data Flow

1. User logs in → obtains JWT token.
2. Frontend stores token securely (httpOnly cookie where possible, or secure storage).
3. Subsequent requests include token in Authorization header.
4. Backend enforces RBAC via DRF permissions.
5. Frontend uses a thin API client layer in `lib/api.ts` (or similar) to call REST endpoints.
6. Aggregated metrics are computed on the backend in `dashboard` service functions and exposed via endpoints like `/api/v1/dashboard/summary/`.

## Scaling Considerations

- Horizontal scaling of backend using stateless application instances.
- PostgreSQL single instance is initially fine; can move to managed DB in production.
- File storage abstracted via Django storage backend; can move from local to S3/MinIO.
- Add Redis later if we introduce background tasks, caching, or notifications.

## Security Notes

- Use HTTPS everywhere in production.
- Use secure cookies for tokens if integrated with Next.js.
- Enforce reasonable file upload limits and allowed MIME types.
- Apply database constraints/group‑based permissions to prevent cross‑department data leakage.
