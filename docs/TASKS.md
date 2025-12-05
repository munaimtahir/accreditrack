# TASKS.md – Initial Task Backlog

This is a starting backlog for the AI developer or human contributors.

## Phase 1 – Backend Foundations

1. **Bootstrap Django project**
   - Create project `config`.
   - Set up settings for Postgres, env vars, DRF, JWT auth.

2. **Accounts app**
   - Custom User model (email login).
   - Role and UserRole models.
   - JWT auth endpoints: login, refresh.
   - `/users/me/` endpoint.

3. **Organizations app**
   - Department model and basic CRUD (admin only).

4. **Proformas app**
   - Models: ProformaTemplate, ProformaSection, ProformaItem.
   - Basic CRUD APIs for templates, sections, items.

## Phase 2 – Assignments & Status

5. **Assignments app models and APIs**
   - Assignment, ItemStatus.
   - Endpoint to create assignments from a template for multiple departments.
   - Logic to auto‑create ItemStatus records.

6. **Permissions & policies**
   - Enforce RBAC for all main endpoints.

## Phase 3 – Evidence & Comments

7. **Evidence app**
   - File upload endpoint linked to ItemStatus.
   - List evidence.

8. **Comments app**
   - Comments linked to ItemStatus.
   - List/add endpoints.

## Phase 4 – Dashboards & Analytics

9. **Dashboard endpoints**
   - Summary completion for an assignment.
   - Summary for template × department.
   - Pending items list.

## Phase 5 – Frontend

10. **Auth & layout**
    - Login page.
    - Basic shell with sidebar/topbar and role‑aware navigation.

11. **Proforma pages**
    - List templates.
    - View single template with sections/items.

12. **Assignments pages**
    - Assignment list + filters.
    - Assignment detail with per‑section progress and item table.

13. **Item detail drawer**
    - Status update controls.
    - Evidence uploads.
    - Comments.

14. **Dashboard UI**
    - Basic charts (completion by section and department).

Keep this file updated as tasks are completed or re‑prioritized.
