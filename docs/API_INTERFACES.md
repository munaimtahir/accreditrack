# API_INTERFACES.md – REST API Design (v1)

Base URL: `/api/v1/`

Authentication: JWT (e.g., via `/auth/login/`), Bearer token in `Authorization` header.

Only core endpoints are listed here; expand as needed.

---

## Auth

### POST `/auth/login/`
- Request: `{ "email": string, "password": string }`
- Response: `{ "access": string, "refresh": string, "user": { ... } }`

### POST `/auth/refresh/`
- Request: `{ "refresh": string }`
- Response: `{ "access": string }`

---

## Users & Departments

### GET `/users/me/`
- Returns current user profile and roles.

### GET `/departments/`
- List departments (SuperAdmin/QAAdmin see all; others limited).

---

## Proformas

### GET `/proformas/templates/`
- List templates.
- Query params: `is_active`, `search`.

### POST `/proformas/templates/` (QAAdmin / SuperAdmin)
- Create a new template.

### GET `/proformas/templates/{id}/`
- Retrieve template details, including sections and items (or via nested endpoints).

### PATCH `/proformas/templates/{id}/`
- Update basic info.

### POST `/proformas/templates/{id}/sections/`
- Create a section within a template.

### GET `/proformas/templates/{id}/sections/`
- List sections.

### POST `/proformas/sections/{id}/items/`
- Create items under a section.

### GET `/proformas/sections/{id}/items/`
- List items.

---

## Assignments

### GET `/assignments/`
- List assignments visible to the user.
- Filters: `template`, `department`, `status`, `due_before`, `due_after`.

### POST `/assignments/` (QAAdmin)
- Create assignment(s).
- Body can allow multiple departments:
  ```json
  {
    "proforma_template": "uuid",
    "departments": ["uuid1", "uuid2"],
    "start_date": "2025-01-01",
    "due_date": "2025-03-01"
  }
  ```

### GET `/assignments/{id}/`
- Retrieve assignment with summary stats.

---

## Item Status & Evidence

### GET `/assignments/{id}/items/`
- Returns sections and items with status for this assignment.

### PATCH `/item-status/{id}/` (Coordinator / QAAdmin)
- Update status and completion_percent (with permission checks).

### POST `/item-status/{id}/evidence/`
- Upload evidence file(s).
- Multipart form:
  - `file`
  - `description`

### GET `/item-status/{id}/evidence/`
- List attached evidence.

### POST `/item-status/{id}/comments/`
- Body: `{ "text": "...", "type": "General" }`

### GET `/item-status/{id}/comments/`
- List comments.

---

## Dashboard & Analytics

### GET `/dashboard/summary/`
- Query params: `template`, `department`.
- Response:
  - `overall_completion_percent`
  - `assignments`: list with `{ id, department_name, completion_percent, due_date, status }`
  - `sections`: list with `{ code, title, completion_percent }`

### GET `/dashboard/pending-items/`
- Returns list of items not Completed/Verified, filtered by role and permissions.

---

## Conventions

- All timestamps in ISO 8601 UTC.
- Paginate lists using `?page=` and `?page_size=`.
- Use standard DRF error responses.

This spec is a starting point; keep it updated as the implementation evolves.
