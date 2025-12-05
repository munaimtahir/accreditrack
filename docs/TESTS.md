# TESTS.md – Testing Strategy

## Backend (Django + DRF)

Use `pytest` for:

- **Unit tests**:
  - Model methods and services (e.g., completion calculations).
  - Permission classes.
- **API tests**:
  - Auth flows (login, refresh).
  - CRUD for proformas.
  - Assignment creation.
  - Status transitions and permission enforcement.
  - Dashboard endpoints return correct summaries.

### Command

```bash
cd backend
pytest
```

## Frontend (Next.js + TypeScript)

Use Jest + React Testing Library:

- **Unit tests**:
  - Pure functions (helpers, formatters).
- **Component tests**:
  - Core components: layout, forms, status badge, progress bars.
- **Page tests**:
  - Smoke tests to ensure pages render with mocked API responses.

### Commands

```bash
cd frontend
npm test
```

## End-to-End Testing (Later)

Consider adding Playwright or Cypress to cover:

- Login flow.
- Proforma browsing.
- Assignment update scenarios.

This can be added once the main flows are stable.
