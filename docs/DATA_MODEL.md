# DATA_MODEL.md – Core Data Model

This document describes the main entities and relationships. Field names are indicative; adjust implementation details as needed.

## 1. Accounts & Organizations

### User
- `id: UUID`
- `email: string (unique)`
- `password: hashed`
- `full_name: string`
- `is_active: bool`
- `is_staff: bool`
- Timestamps: `created_at`, `updated_at`

### Department
- `id: UUID`
- `name: string`
- `code: string`
- `parent: FK -> Department (nullable)`

### Role
- `id: UUID`
- `name: enum("SuperAdmin", "QAAdmin", "DepartmentCoordinator", "Viewer")`

### UserRole
- `id: UUID`
- `user: FK -> User`
- `role: FK -> Role`
- `department: FK -> Department (nullable)`

## 2. Proforma Templates

### ProformaTemplate
- `id: UUID`
- `title: string`
- `authority_name: string`  (e.g., "PMDC")
- `description: text`
- `version: string`
- `is_active: bool`
- Timestamps: `created_at`, `updated_at`

### ProformaSection
- `id: UUID`
- `template: FK -> ProformaTemplate`
- `code: string`  (e.g., "A", "B1", "1.2")
- `title: string`
- `weight: integer`  (for ordering)

### ProformaItem
- `id: UUID`
- `section: FK -> ProformaSection`
- `code: string`  (e.g., "A.1", "B.2.3")
- `requirement_text: text`
- `required_evidence_type: string`  (free text: "policy document", "SOP", etc.)
- `importance_level: smallint` (1–5, optional)

## 3. Assignments and Progress

### Assignment
- `id: UUID`
- `proforma_template: FK -> ProformaTemplate`
- `department: FK -> Department`
- `start_date: date`
- `due_date: date`
- `status: enum("NotStarted", "InProgress", "Completed")`
- Timestamps: `created_at`, `updated_at`

### ItemStatus
- `id: UUID`
- `assignment: FK -> Assignment`
- `proforma_item: FK -> ProformaItem`
- `status: enum("NotStarted", "InProgress", "Submitted", "Verified", "Rejected")`
- `completion_percent: smallint` (0–100)
- `last_updated_by: FK -> User`
- `last_updated_at: datetime`

Constraints:
- `(assignment, proforma_item)` unique.

## 4. Evidence and Comments

### Evidence
- `id: UUID`
- `item_status: FK -> ItemStatus`
- `file: FileField`
- `description: text (nullable)`
- `uploaded_by: FK -> User`
- `uploaded_at: datetime`

### Comment
- `id: UUID`
- `item_status: FK -> ItemStatus`
- `text: text`
- `type: enum("General", "Query", "Clarification", "NonComplianceNote")`
- `author: FK -> User`
- `created_at: datetime`

## 5. Audit and Logging

### AuditLog
- `id: UUID`
- `user: FK -> User (nullable for system actions)`
- `action_type: string`
- `entity_type: string`
- `entity_id: string`
- `before_data: JSON (nullable)`
- `after_data: JSON (nullable)`
- `timestamp: datetime`

## 6. Computed Metrics

Not stored directly in DB (unless needed later):

- Assignment completion %:
  - `sum(item_status.completion_percent) / (100 * number_of_items)` or
  - `verified_items / total_items` depending on definition chosen.

The implementation should centralize this logic in a service/util to keep a single source of truth.
