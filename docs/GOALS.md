# GOALS.md – Product Goals

## 1. MVP Goals (Version 0.1)

The MVP should allow a QA/Accreditation team to:

1. Create an accreditation **Proforma Template** with:
   - Sections (e.g., A, B1, 1.2).
   - Items (requirement text + evidence hints).

2. Assign a template to one or more **Departments**:
   - Generate per‑department **Assignments**.
   - Auto‑create **ItemStatus** rows for each item.

3. Let **Department Coordinators**:
   - View their assignments and per‑section progress.
   - Change status of items (NotStarted → InProgress → Submitted).
   - Upload evidence files for each item.
   - Add comments and respond to QA feedback.

4. Let **QA Admins**:
   - View dashboards of completion by department and section.
   - Review submitted items and mark them Verified or Rejected.
   - Leave comments for clarification.

5. Provide basic **analytics**:
   - Completion % per Assignment.
   - Completion % per Section in an assignment.
   - Lists of pending / rejected items.

## 2. Version 1.0 Goals

On top of the MVP:

- Advanced analytics:
  - Heatmaps by department × section.
  - Overdue items lists and escalation views.
- Configurable status workflows (custom status names and transitions).
- Basic notifications:
  - Email for rejections and approaching deadlines.
- Evidence integrity:
  - File versioning or at least timestamps and uploader tracking.
- Role‑based dashboards:
  - Institution‑wide (SuperAdmin, QAAdmin).
  - Department‑specific (Coordinators).
- Multi‑institution support (tenancy) behind a simple tenant_id when needed.

## 3. Non‑Goals (For Now)

- Full OCR / parsing of PDFs or Word proformas.
- Public‑facing portals.
- Multi‑language UI (keep code ready for later i18n but not in MVP).
