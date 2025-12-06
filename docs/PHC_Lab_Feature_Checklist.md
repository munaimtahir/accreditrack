# PHC Laboratory Accreditation – Feature Checklist

This checklist is for reviewing whether the PHC Lab module and dashboard
are actually built and working in the codebase.

Tick = verified in code and UI.  
Question mark = partial / needs work.

---

## 1. App Structure & Access

- [ ] App can start locally without errors (backend + frontend).
- [ ] There is an authentication system (login) in place.
- [ ] After login, there is a main **dashboard/home** page.
- [ ] A **PHC Laboratory** module/card/link is visible from the main dashboard.

---

## 2. PHC-LAB Module & Template

- [ ] `PHC-LAB` exists as a module identifier (model/enum/field).
- [ ] At least one **Proforma Template** is linked to `PHC-LAB`.
- [ ] A template with a code like `PHC-MSDS-2018` or similar exists.
- [ ] There is a **seed command** to populate the PHC Lab MSDS template.
- [ ] The template includes:
  - [ ] Categories/domains (ROM, FMS, HRM, MER, RRS, QA, BSBS, AAC, COP, PRE).
  - [ ] Standards under each category (e.g. ROM-1, ROM-2…).
  - [ ] Indicators under each standard (with codes and text).

---

## 3. Roles & Permissions

- [ ] System supports multiple roles, at least:
  - [ ] SUPERADMIN
  - [ ] DASHBOARD_ADMIN (for PHC-LAB)
  - [ ] CATEGORY_ADMIN
  - [ ] USER (normal assignee)
- [ ] A user can have **different roles in different modules**.
- [ ] SUPERADMIN can assign roles to users per module.
- [ ] DASHBOARD_ADMIN for PHC-LAB can:
  - [ ] See PHC Lab dashboard.
  - [ ] Manage/checklist & assignments.
- [ ] CATEGORY_ADMIN can:
  - [ ] Manage or assign items only in their category.
- [ ] USER can:
  - [ ] View their own assignments only.
  - [ ] Upload evidence.
  - [ ] Post updates/progress.

---

## 4. Checklist UI (PHC MSDS Viewer)

- [ ] There is a **PHC Lab dashboard** view/page.
- [ ] From PHC Lab dashboard, there is a way to open the **PHC MSDS checklist**.
- [ ] Checklist view shows:
  - [ ] Categories (ROM, FMS, etc.) as tabs/sections.
  - [ ] Standards within each category.
  - [ ] Indicators within each standard.
- [ ] For each indicator, the UI shows:
  - [ ] Code (e.g. ROM-1-1).
  - [ ] Full text/description.
  - [ ] Basic scoring info (max_score / weightage) if available.

---

## 5. Assignments & Workflow

- [ ] There is an **Assignment** model in the backend.
- [ ] Assignments can be linked to:
  - [ ] A specific indicator.
  - [ ] A standard or section.
- [ ] Assignments can be assigned to:
  - [ ] One user.
  - [ ] Multiple users.
- [ ] Assignment includes:
  - [ ] Instructions text.
  - [ ] Due date.
  - [ ] Status field (e.g. NOT_STARTED, IN_PROGRESS, PENDING_REVIEW, VERIFIED).
- [ ] From the checklist UI:
  - [ ] Dashboard Admin can create an assignment for a standard.
  - [ ] Dashboard Admin can create an assignment for an indicator.

- [ ] A “My Assignments” view exists for normal users where:
  - [ ] They see tasks assigned to them.
  - [ ] They can open assignment details.

---

## 6. Evidence & Status Updates

- [ ] There is an **Evidence** model in the backend.
- [ ] Evidence is linked to:
  - [ ] An assignment and/or indicator.
  - [ ] A user who uploaded it.
- [ ] Evidence supports:
  - [ ] File upload.
  - [ ] Text note/description.
  - [ ] Reference code (e.g. file number).
- [ ] A user can:
  - [ ] Upload one or more evidence items for an assignment.
  - [ ] See a list of their uploaded evidence.
- [ ] Assignment status changes when:
  - [ ] Evidence is added (moves to IN_PROGRESS or similar).
  - [ ] User submits for review (PENDING_REVIEW).
  - [ ] Admin verifies (VERIFIED).
- [ ] There is some form of **progress log / history** (optional but preferred).

---

## 7. PHC Lab Dashboard Analytics

- [ ] PHC Lab dashboard shows:
  - [ ] Overall completion percentage for PHC-LAB.
  - [ ] Category-wise completion (ROM, FMS, etc.).
- [ ] Completion is based on:
  - [ ] Number of indicators marked as completed/verified vs total.
- [ ] There is at least a basic view of:
  - [ ] Total assignments.
  - [ ] Overdue assignments (based on due_date).
- [ ] When an assignment is completed/verified, dashboard numbers update accordingly
  (after refresh or API call).

---

## 8. Technical Utilities (Optional but Helpful)

- [ ] A management command exists to:
  - [ ] Seed PHC MSDS (`seed_phc_lab_msds` or similar).
- [ ] There is at least one automated test or script that:
  - [ ] Verifies the PHC-MSDS template exists.
  - [ ] Verifies categories and indicators are loaded.

